#!/usr/bin/env python3
"""Recrea la politica B del notebook original sin usar el conjunto de prueba para ajuste.

Primero selecciona hiperparametros por CV en entrenamiento; luego selecciona
el umbral en validacion con recall >= 0.70 y costo ilustrativo FN=5, FP=1.
Por ultimo mide el conjunto de prueba una sola vez y exporta el pipeline.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, average_precision_score, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.features import EXPECTED_SHA256, FEATURES, TARGET  # noqa: E402

SEED = 42
THRESHOLDS = np.round(np.linspace(0.05, 0.95, 91), 2)


def download_csv():
    import kagglehub

    folder = Path(kagglehub.dataset_download("uciml/default-of-credit-card-clients-dataset"))
    candidates = sorted(folder.rglob("UCI_Credit_Card.csv"))
    if not candidates:
        raise FileNotFoundError("Kaggle no entrego UCI_Credit_Card.csv")
    return candidates[0]


def metricas(y_true, scores, threshold):
    y_pred = (np.asarray(scores) >= threshold).astype(int)
    tn, fp, fn, tp = (int(x) for x in confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel())
    return {
        "umbral": float(threshold), "n": len(y_true),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "fpr": float(fp / (fp + tn)) if (fp + tn) else 0.0,
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "pr_auc": float(average_precision_score(y_true, scores)),
        "costo_total_ilustrativo": 5 * fn + fp,
    }


def choose_threshold(y_true, scores):
    results = pd.DataFrame([metricas(y_true, scores, t) for t in THRESHOLDS])
    eligible = results.loc[results["recall"] >= 0.70]
    if eligible.empty:
        raise RuntimeError("No hay umbral con recall >= 0.70 en validacion.")
    best = eligible.sort_values(
        ["costo_total_ilustrativo", "fpr", "umbral"],
        ascending=[True, True, False],
    ).iloc[0]
    return float(best["umbral"]), best.to_dict()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=None, help="CSV original; si se omite, se descarga desde Kaggle")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts")
    args = parser.parse_args()

    csv_path = args.csv if args.csv else download_csv()
    actual_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise ValueError(
            "SHA256 del dataset diferente al notebook original. "
            "No entrenaremos con un archivo no verificado. "
            f"Esperado: {EXPECTED_SHA256}; obtenido: {actual_hash}"
        )

    dataset = pd.read_csv(csv_path)
    dataset.columns = dataset.columns.str.strip()
    required = set(FEATURES + [TARGET, "ID"])
    if not required.issubset(dataset.columns):
        raise ValueError("Faltan columnas en el dataset original")
    if len(dataset) != 30_000 or dataset["ID"].duplicated().any():
        raise ValueError("Cantidad de filas inesperada o IDs duplicados")
    if dataset[TARGET].isna().any() or set(dataset[TARGET].unique()) != {0, 1}:
        raise ValueError("Variable objetivo invalida")
    X = dataset[FEATURES].apply(pd.to_numeric, errors="raise")
    y = dataset[TARGET].astype(int)

    indices = np.arange(len(y))
    idx_development, idx_test = train_test_split(indices, test_size=0.20, stratify=y, random_state=SEED)
    idx_train, idx_validation = train_test_split(
        idx_development, test_size=0.25, stratify=y.iloc[idx_development], random_state=SEED
    )
    X_train, y_train = X.iloc[idx_train], y.iloc[idx_train]
    X_validation, y_validation = X.iloc[idx_validation], y.iloc[idx_validation]
    X_test, y_test = X.iloc[idx_test], y.iloc[idx_test]

    estimator = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("modelo", HistGradientBoostingClassifier(random_state=SEED, early_stopping=False)),
    ])
    tuning = GridSearchCV(
        estimator=estimator,
        param_grid={
            "modelo__learning_rate": [0.05, 0.10],
            "modelo__max_leaf_nodes": [15, 31],
            "modelo__max_iter": [120],
            "modelo__min_samples_leaf": [40],
        },
        scoring="roc_auc",
        refit=True,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED),
        n_jobs=2,
        error_score="raise",
    )
    print("Entrenando 4 candidatos x 5 folds con 18,000 filas (puede tomar algunos minutos)...", flush=True)
    tuning.fit(X_train, y_train)
    winner = tuning.best_estimator_
    val_scores = winner.predict_proba(X_validation)[:, 1]
    selected_threshold, val_metrics = choose_threshold(y_validation, val_scores)
    val_metrics = {key: (val.item() if isinstance(val, np.generic) else val) for key, val in val_metrics.items()}
    test_scores = winner.predict_proba(X_test)[:, 1]
    test_metrics = metricas(y_test, test_scores, selected_threshold)

    args.output.mkdir(parents=True, exist_ok=True)
    model_path = args.output / "modelo_riesgo.joblib"
    joblib.dump(winner, model_path, compress=3)
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    metadata = {
        "modelo": "HistGradientBoostingClassifier + imputacion mediana",
        "features": FEATURES,
        "clase_positiva": 1,
        "umbral": selected_threshold,
        "recall_minimo_validacion": 0.70,
        "costos_teoricos": {"falso_negativo": 5, "falso_positivo": 1},
        "tipo_modelo": "clasificacion binaria de incumplimiento",
        "dataset": "uciml/default-of-credit-card-clients-dataset",
        "dataset_sha256": actual_hash,
        "modelo_sha256": model_hash,
        "n_entrenamiento": len(idx_train),
        "n_validacion": len(idx_validation),
        "n_prueba": len(idx_test),
        "cv_roc_auc": float(tuning.best_score_),
        "mejores_parametros": tuning.best_params_,
        "metricas_validacion": val_metrics,
        "metricas_prueba": test_metrics,
        "python_sklearn": sklearn.__version__,
        "entrenado_utc": datetime.now(timezone.utc).isoformat(),
        "limitaciones": [
            "Datos de Taiwan de 2005; no generalizable a otras poblaciones sin validacion.",
            "El puntaje predict_proba no fue calibrado; no interpretar como probabilidad validada.",
            "Uso academico exclusivamente; prohibido automatizar decisiones crediticias.",
            "Exclusion de sexo y edad del modelo no garantiza equidad.",
        ],
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(json.dumps({
        "artefactos": [str(model_path), str(args.output / "metadata.json")],
        "umbral": selected_threshold,
        "cv_roc_auc": tuning.best_score_,
        "metricas_prueba": test_metrics,
    }, indent=2, ensure_ascii=False))
    print("Importante: compara estas cifras con las salidas historicas del notebook.")


if __name__ == "__main__":
    main()

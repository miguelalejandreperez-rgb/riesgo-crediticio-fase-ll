"""Carga del artefacto versionado; NUNCA aceptar rutas suministradas por el cliente."""

import hashlib
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

from app.features import FEATURES

ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = Path(os.getenv("MODEL_FILE", str(ROOT / "artifacts" / "modelo_riesgo.joblib")))
META_FILE = Path(os.getenv("META_FILE", str(ROOT / "artifacts" / "metadata.json")))


class ModelUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelBundle:
    estimator: Any
    metadata: dict


@lru_cache(maxsize=1)
def load_bundle() -> ModelBundle:
    if not MODEL_FILE.is_file() or not META_FILE.is_file():
        raise ModelUnavailable("No se encontraron los artefactos. Ejecuta scripts/train_and_export.py antes de iniciar.")
    metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
    if metadata.get("features") != FEATURES:
        raise ModelUnavailable("Contrato de variables incompatible con el modelo exportado.")
    expected_hash = metadata.get("modelo_sha256")
    actual_hash = hashlib.sha256(MODEL_FILE.read_bytes()).hexdigest()
    if not expected_hash or expected_hash != actual_hash:
        raise ModelUnavailable("La huella del modelo no coincide con metadata.json.")
    # joblib.load requiere un archivo confiable; usamos exclusivamente el artefacto del proyecto.
    estimator = joblib.load(MODEL_FILE)
    if not hasattr(estimator, "predict_proba"):
        raise ModelUnavailable("Artefacto sin predict_proba.")
    return ModelBundle(estimator=estimator, metadata=metadata)

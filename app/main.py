"""API y frontend del prototipo; no apto para decision crediticia real."""

from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.features import FEATURES
from app.schemas import CreditApplication
from app.service import ModelUnavailable, load_bundle

app = FastAPI(
    title="Riesgo crediticio - demostracion academica",
    version="1.0.0",
    description="Puntaje experimental basado en datos historicos de Taiwan (2005). No usar en decisiones reales.",
)
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health():
    try:
        bundle = load_bundle()
    except (ModelUnavailable, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"estado": "listo", "modelo": bundle.metadata.get("modelo"), "version": "1.0.0"}


@app.get("/api/modelo")
def model_info():
    try:
        bundle = load_bundle()
    except (ModelUnavailable, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "modelo": bundle.metadata["modelo"],
        "umbral": bundle.metadata["umbral"],
        "features": FEATURES,
        "metricas_prueba": bundle.metadata.get("metricas_prueba", {}),
        "advertencia": "Demostracion academica; datos de Taiwan (2005), sin calibracion ni validacion externa.",
    }


@app.post("/api/predecir")
def predict(payload: CreditApplication):
    try:
        bundle = load_bundle()
    except (ModelUnavailable, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    data = payload.model_dump()
    frame = pd.DataFrame([[data[c] for c in FEATURES]], columns=FEATURES)
    try:
        probs = bundle.estimator.predict_proba(frame)[0]
        labels = list(bundle.estimator.classes_)
        idx = labels.index(1)
        score = float(probs[idx])
        if not np.isfinite(score) or not (0 <= score <= 1):
            raise ValueError("Salida del modelo fuera de [0, 1]")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al procesar la inferencia del modelo") from exc

    threshold = float(bundle.metadata["umbral"])
    return {
        "puntaje_incumplimiento": round(score, 6),
        "umbral_alerta": threshold,
        "alerta": bool(score >= threshold),
        "interpretacion": "Alerta experimental" if score >= threshold else "Sin alerta experimental",
        "uso": "Solo demostracion educativa; no aprobar, rechazar ni modificar creditos con esta salida.",
    }

#!/usr/bin/env python3
"""Verifica los artefactos guardados sin cargar objetos joblib no confiables."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
model_path = root / "artifacts" / "modelo_riesgo.joblib"
metadata_path = root / "artifacts" / "metadata.json"
if not model_path.is_file() or model_path.stat().st_size == 0:
    raise SystemExit("ERROR: falta artifacts/modelo_riesgo.joblib. Ejecuta bash scripts/prepare_model.sh una sola vez.")
if not metadata_path.is_file() or metadata_path.stat().st_size == 0:
    raise SystemExit("ERROR: falta artifacts/metadata.json. Ejecuta bash scripts/prepare_model.sh una sola vez.")
try:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
except (ValueError, OSError) as exc:
    raise SystemExit(f"ERROR: metadatos no validos: {exc}") from exc
expected = metadata.get("modelo_sha256")
actual = hashlib.sha256(model_path.read_bytes()).hexdigest()
if not isinstance(expected, str) or expected != actual:
    raise SystemExit("ERROR: el hash SHA256 del modelo difiere de metadata.json. No iniciar Docker.")
if not isinstance(metadata.get("features"), list) or len(metadata["features"]) != 19:
    raise SystemExit("ERROR: metadatos sin las 19 variables esperadas.")
print("OK: modelo exportado y metadatos presentes; integridad SHA256 verificada.")

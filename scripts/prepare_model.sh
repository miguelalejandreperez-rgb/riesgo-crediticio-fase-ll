#!/usr/bin/env bash
# Ejecutar SOLO una vez al crear el modelo; no forma parte del arranque habitual.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -s artifacts/modelo_riesgo.joblib && -s artifacts/metadata.json ]]; then
  python scripts/check_artifacts.py
  echo "El modelo ya existe y es valido. No se volvera a entrenar."
  exit 0
fi
if [[ -e artifacts/modelo_riesgo.joblib || -e artifacts/metadata.json ]]; then
  echo "ERROR: solo existe uno de los artefactos. Revisa los archivos en artifacts/ antes de entrenar." >&2
  exit 1
fi

echo "Preparacion inicial: instalando dependencias de ENTRENAMIENTO en Codespaces..."
python -m pip install -r requirements-train.txt

echo "Entrenando y guardando modelo reproducible por unica vez..."
python scripts/train_and_export.py
python scripts/check_artifacts.py

size_bytes=$(wc -c < artifacts/modelo_riesgo.joblib)
if (( size_bytes >= 100000000 )); then
  echo "ATENCION: modelo demasiado grande para Git normal (>100 MB). Consultar Git LFS o un almacén de artefactos." >&2
  exit 1
fi

echo "Modelo preparado. IMPORTANTE: para conservarlo entre Codespaces distintos, registra estos archivos en GitHub:"
echo "  git add artifacts/modelo_riesgo.joblib artifacts/metadata.json"
echo "  git commit -m 'Guardar modelo entrenado de riesgo crediticio'"
echo "  git push"
echo "Despues ejecuta: bash scripts/start_codespaces.sh"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no esta disponible. Abre Codespaces usando .devcontainer/devcontainer.json" >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: el daemon Docker no esta activo. Reconstruye el Codespace con Docker-in-Docker." >&2
  exit 1
fi

if [[ ! -s artifacts/modelo_riesgo.joblib || ! -s artifacts/metadata.json ]]; then
  echo "No hay modelo exportado. Entrenando y exportando a partir del dataset publico original..."
  python scripts/train_and_export.py
fi

echo "Construyendo imagen Docker..."
docker build -t riesgo-crediticio-faseii:1.0 .
docker rm -f riesgo-crediticio-demo >/dev/null 2>&1 || true
docker run -d --name riesgo-crediticio-demo -p 8000:8000 riesgo-crediticio-faseii:1.0

for trial in $(seq 1 20); do
  if curl --fail --silent http://localhost:8000/api/health >/dev/null; then
    echo "Aplicacion verificada en http://localhost:8000"
    echo "En Codespaces, abre el puerto 8000 desde la pestana PORTS (visibilidad Private)."
    exit 0
  fi
  sleep 2
done

docker logs riesgo-crediticio-demo
echo "ERROR: la aplicacion no supero la prueba de salud." >&2
exit 1

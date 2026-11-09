#!/usr/bin/env bash
# Arranque idempotente: NUNCA entrena, SOLO reutiliza el modelo exportado.
set -euo pipefail
cd "$(dirname "$0")/.."

image_name="riesgo-crediticio-faseii:1.0"
container_name="riesgo-crediticio-demo"
rebuild="${1:-}"
if [[ -n "$rebuild" && "$rebuild" != "--rebuild" ]]; then
  echo "Uso: bash scripts/start_codespaces.sh [--rebuild]" >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker no esta disponible en Codespaces. Revisa la configuracion Docker-in-Docker." >&2
  exit 1
fi

# Comprobacion SIN joblib ni otras librerias de ML instaladas en Codespaces.
python scripts/check_artifacts.py || {
  echo "No se entrena automaticamente durante el arranque. Si falta el modelo, ejecuta:" >&2
  echo "  bash scripts/prepare_model.sh" >&2
  echo "Y registra los dos artefactos en GitHub (README, seccion Persistencia)." >&2
  exit 2
}

if [[ "$rebuild" == "--rebuild" ]]; then
  echo "Reconstruccion solicitada: eliminando contenedor anterior y recreando imagen..."
  docker rm -f "$container_name" >/dev/null 2>&1 || true
  docker build -t "$image_name" .
elif ! docker image inspect "$image_name" >/dev/null 2>&1; then
  echo "Imagen no disponible: construyendo Docker con el modelo existente..."
  docker build -t "$image_name" .
fi

if docker container inspect "$container_name" >/dev/null 2>&1; then
  if [[ "$(docker inspect --format '{{.State.Running}}' "$container_name")" == "true" ]]; then
    echo "El contenedor ya esta iniciado; no se ha recreado."
  else
    echo "Reiniciando contenedor existente..."
    docker start "$container_name" >/dev/null
  fi
else
  echo "Creando contenedor sin volver a entrenar..."
  docker run -d --restart unless-stopped --name "$container_name" -p 8000:8000 "$image_name" >/dev/null
fi

for trial in $(seq 1 30); do
  if curl --noproxy '*' --fail --silent http://127.0.0.1:8000/api/health >/dev/null; then
    echo "OK: Aplicacion en http://127.0.0.1:8000/"
    echo "Prueba de inferencia: bash scripts/smoke_docker.sh"
    echo "Navegador: abrir puerto 8000 PRIVADO en la pestana PORTS de Codespaces."
    exit 0
  fi
  sleep 2
done

docker ps -a || true
docker logs --tail 80 "$container_name" || true
echo "ERROR: la aplicacion no supero la verificacion de salud." >&2
exit 1

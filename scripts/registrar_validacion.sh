#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidencias
OUT="evidencias/registro_tecnico_codespaces.txt"
{
  echo "VALIDACION TECNICA DE DOCKER - GENERADA DESDE CODESPACES"
  date -u '+Fecha UTC: %Y-%m-%d %H:%M:%S'
  echo
  echo '=== Version de Docker ==='
  docker version
  echo
  echo '=== Contenedores ==='
  docker ps
  echo
  echo '=== Imagenes ==='
  docker image ls riesgo-crediticio-faseii
  echo
  echo '=== Salud ==='
  curl --fail --silent http://localhost:8000/api/health
  echo
  echo '=== Prueba de inferencia real ==='
  bash scripts/smoke_docker.sh
} > "$OUT"
echo "Registro real guardado en: $OUT"

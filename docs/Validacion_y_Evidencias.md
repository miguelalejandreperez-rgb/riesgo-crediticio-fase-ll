# Verificación técnica y registro de evidencias

## Estado de las pruebas al preparar la entrega
- **Confirmado en este entorno de preparación:** `python -m pytest -q` devolvió `5 passed` al ejecutar pruebas de API con doble de pruebas simulado.
- **No ejecutado:** descarga de Kaggle, entrenamiento completo, exportación del modelo real, Docker build/run o validación remota en Codespaces.
- **Causa:** este entorno de trabajo no ofrece motor Docker y no pudo descargar el dataset desde sitios externos.
- **Acción pendiente del usuario:** crear el repositorio en GitHub, iniciar Codespaces y ejecutar `bash scripts/start_codespaces.sh`.

## Casos cubiertos por las pruebas unitarias
| Identificador | Propósito | Resultado |
|---|---|---|
| UT-01 | Renderizar la página HTML | OK |
| UT-02 | Devolver 503 si falta el modelo | OK |
| UT-03 | Responder con inferencia y respetar el umbral usando un modelo simulado | OK |
| UT-04 | Rechazar datos faltantes, adicionales, negativos inválidos o fuera de rango (422) | OK |
| UT-05 | Rechazar cadenas no numéricas, infinitos y pagos fraccionarios de estado (422) | OK |

## Pruebas pendientes con el modelo real
| Identificador | Procedimiento | Evidencia solicitada |
|---|---|---|
| INT-01 | `python scripts/train_and_export.py` | Salida de CV, umbral y metricas de prueba (metadata.json). |
| INT-02 | `docker build -t riesgo-crediticio-faseii:1.0 .` | Captura con build exitoso. |
| INT-03 | `docker run -d -p 8000:8000 ...` | `docker ps` y `docker logs`. |
| INT-04 | `curl http://localhost:8000/api/health` | Respuesta `estado=listo`. |
| INT-05 | `bash scripts/smoke_docker.sh` | Ejemplo de inferencia con puntuación real. |
| INT-06 | Probar UI, reiniciar formulario y validación requerida | Captura del formulario y del resultado. |
| INT-07 | GitHub Actions > workflow manual de Docker | Ejecución de CI exitosa, url/fecha. |

## Criterios de evaluación (rúbrica Fase II)
| Criterio | Evidencia planeada |
|---|---|
| 25 % Docker | Dockerfile, imagen, ejecución y salud del contenedor en Codespaces. |
| 25 % Integración | Frontend + API + modelo real, con demo y `/docs`. |
| 25 % Pruebas | Unitarias, casos extremos, smoke HTTP con modelo y resultados registrados. |
| 25 % Documentación | Repositorio estructurado, README y manual de despliegue replicable. |

## Observaciones metodológicas
El notebook original seleccionó Gradient Boosting por validación cruzada; el programa nuevo reproduce los cuatro valores de la rejilla del modelo y recalcula el umbral en validación. El modelo está entrenado con datos históricos de Taiwán (2005); no calibrado ni validado en contextos actuales, y no se utilizará para decisiones de crédito de clientes reales. El alcance de la Fase II cambia respecto de la Fase I; documentar explícitamente que el modelo proviene de la Actividad 6.

## Campos para completar después de ejecutar Codespaces
- Fecha UTC y URL de repositorio: ______________________________________________
- Imagen (`docker image ls`) y contenedor (`docker ps`): _________________________
- Umbral de metadata, ROC-AUC y recall en prueba: _______________________________
- Smoke HTTP y URL del workflow GitHub Actions: ________________________________
- Capturas de pantalla anexas: ________________________________________________

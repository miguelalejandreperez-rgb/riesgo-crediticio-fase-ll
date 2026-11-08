Este directorio recibe `modelo_riesgo.joblib` y `metadata.json` tras ejecutar
`python scripts/train_and_export.py`. No hay un modelo real preentrenado dentro
del paquete inicial: el archivo fuente original no lo serializa.

Los artefactos binarios se excluyen del repositorio mediante `.gitignore`.
Cualquier imagen Docker real se construye solo despues de generar ambos archivos.

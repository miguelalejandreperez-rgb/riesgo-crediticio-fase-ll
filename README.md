# Fase II - Prototipo de riesgo crediticio con FastAPI y Docker

**Proyecto educativo de Gestión de Proyectos de Inteligencia Artificial.**

Este repositorio adapta el notebook `original/Actividad_6_Riesgo_Crediticio.ipynb` (Actividad 6, **no** Fase I) a una aplicación web con API REST, frontend y Docker. **No presentarlo como una continuación técnica del modelo Fase I sin aclarar este cambio de alcance.**

> **ADVERTENCIA**: datos de tarjetas de crédito de Taiwán (2005). No es válido para decisiones de crédito reales, clientes de México ni uso con datos personales. El puntaje de `predict_proba` no cuenta con calibración ni validación externa. El umbral es una regla ilustrativa de alerta y no una recomendación financiera.

## 1. Qué contiene

| Carpeta / archivo | Propósito |
|---|---|
| `original/` | Notebook de origen, sin alterar. |
| `app/main.py` | FastAPI: `GET /`, `GET /api/health`, `GET /api/modelo`, `POST /api/predecir`. |
| `app/schemas.py` | Validación de las 19 variables, con mensajes de error estándar 422. |
| `app/service.py` | Carga única del pipeline y comprobación de integridad SHA256. |
| `app/static/` | Formulario sencillo con HTML, CSS y JavaScript. |
| `scripts/train_and_export.py` | Reproduce Grid Search del modelo boosting y elección del umbral sobre validación. |
| `scripts/prepare_model.sh` | Entrena y exporta una vez; instala `joblib` y las dependencias de entrenamiento. |
| `scripts/check_artifacts.py` | Revisa existencia e integridad SHA256 del modelo sin instalar `joblib`. |
| `scripts/start_codespaces.sh` | Inicia/reutiliza Docker usando el modelo guardado, sin volver a entrenar. |
| `scripts/smoke_docker.sh` | Prueba HTTP con modelo real. |
| `tests/` | Pruebas unitarias de API usando un modelo de prueba explícitamente simulado. |
| `.devcontainer/devcontainer.json` | Codespaces con Docker-in-Docker. |
| `.github/workflows/` | Pruebas unitarias y prueba manual de Docker con modelo real. |
| `Dockerfile` | Imagen reproducible para CPU sin datos históricos embebidos. |
| `docs/` | Manual de despliegue y reporte de verificación. |

## 2. Inicio desde Windows 11 sin instalar software

Solo se necesitan navegador, cuenta de GitHub e internet. La validación de Docker será **remota**, dentro de GitHub Codespaces; no equivale a instalar ni ejecutar Docker localmente en Windows.

1. Descarga el ZIP de entrega y selecciona **Extraer todo** en Windows.
2. Crea un repositorio en https://github.com/new; nombre sugerido `riesgo-crediticio-fase-ii`. Puede ser privado.
3. En el repositorio vacío, selecciona **uploading an existing file** o **Add file > Upload files**; arrastra el **contenido** de la carpeta `Riesgo_Crediticio_FaseII`, no el archivo ZIP. Asegúrate de incluir carpetas ocultas `.github` y `.devcontainer` y conservar los directorios. Confirma el commit.
4. En la página del repositorio elige **Code > Codespaces > Create codespace on main**. Espera a que el entorno se prepare y abre su terminal en el navegador.
5. **Primera vez, solo si el modelo no está guardado:** ejecuta `bash scripts/prepare_model.sh`. Este comando instala dependencias de entrenamiento en Codespaces, obtiene el dataset, entrena y guarda `artifacts/modelo_riesgo.joblib` y `artifacts/metadata.json`. Si ya existen y son validos, no entrena.
6. Para que **cualquier Codespace futuro** recupere el mismo modelo, confirma que el archivo `.joblib` sea inferior a 100 MB y registra ambos artefactos en GitHub:

   ```bash
   git add artifacts/modelo_riesgo.joblib artifacts/metadata.json
   git commit -m "Guardar modelo entrenado de riesgo crediticio"
   git push
   ```

   Este paso NO ocurre automáticamente: si no haces `git push`, el modelo puede desaparecer cuando borres el Codespace. No subas el dataset ni secretos.
7. **Cada vez que inicies o reabras Codespaces:** ejecuta `bash scripts/start_codespaces.sh`. El script nunca entrena: valida el modelo, reutiliza el contenedor si existe y, de ser necesario, reconstruye la imagen usando los artefactos guardados. Para incorporar cambios de código o del modelo al contenedor: `bash scripts/start_codespaces.sh --rebuild`.
8. Abre **PORTS** y selecciona puerto **8000** (**Private**). Solo mientras Codespaces y el servidor estén encendidos se podrá usar la aplicación. Prueba el formulario y `/docs`, sin datos personales.
9. Ejecuta `bash scripts/smoke_docker.sh` para validar salud e inferencia; después `bash scripts/registrar_validacion.sh` para conservar evidencia.
10. En GitHub, pestaña **Actions**, se puede ejecutar manualmente **Construir y verificar Docker con modelo versionado**; comprueba la misma version del modelo guardado en GitHub sin reentrenar.
11. Detén el Codespace cuando termines para cuidar la cuota. La aplicación no permanece disponible al público cuando el Codespace se detiene.

### Persistencia del modelo: diferencia entre Git, Codespaces y Docker

- **Artefacto de IA:** `artifacts/modelo_riesgo.joblib` y `artifacts/metadata.json` deben guardarse mediante commit/push en el repositorio. Una vez versionados, otro usuario autorizado puede clonar el repositorio y levantar la misma versión sin entrenar. Verificar que el archivo sea menor de 100 MB; para archivos mayores usar Git LFS o un almacén privado de modelos.
- **Archivos en Codespaces:** `/workspaces` conserva archivos al detener o reconstruir *ese* Codespace. Si se crea otro Codespace o se elimina el anterior, solo los cambios enviados a GitHub están asegurados.
- **Contenedor Docker:** puede detenerse, borrarse o recrearse. `start_codespaces.sh` lo recupera o reconstruye con el modelo existente. `--restart unless-stopped` ayuda dentro de un mismo daemon Docker; **no convierte Codespaces en hosting permanente**.
- **Usuarios:** no reentrenan al calcular un puntaje. La aplicación necesita un servidor encendido; el puerto privado solo está disponible para quienes tienen autorización. Para dar servicio continuo se requiere desplegar la imagen en un PaaS/servidor con autenticación y controles de seguridad.
- **Si sale `No module named joblib`:** se está tratando de ejecutar el ENTRENAMIENTO sin dependencias. Solo para la preparación inicial ejecuta `bash scripts/prepare_model.sh`; el arranque normal no necesita `joblib` instalado fuera del contenedor.
- **Si sale `Connection refused`:** comprobar `docker ps` y ejecutar `bash scripts/start_codespaces.sh` antes de `bash scripts/smoke_docker.sh`.
- **Si el navegador muestra 404 pero `curl localhost` devuelve 200:** revisar PORTS, sesión y permisos del puerto privado; la accesibilidad del túnel de Codespaces es diferente de la salud interna del backend.

**Importante:** GitHub Codespaces puede estar sujeto a límites de cuota, políticas de la cuenta y disponibilidad del servicio. No habilites facturación sin verificar los límites. No se han realizado acciones en tu cuenta de GitHub; el repositorio debes crearlo o conectarlo tú.

## 3. Entrenar y exportar (si se desea por separado)

Desde Codespaces, **solo la primera vez**:

```bash
bash scripts/prepare_model.sh
```

Crea automáticamente `artifacts/modelo_riesgo.joblib` y `artifacts/metadata.json`. El script verifica que el dataset descargado tenga la huella SHA256 del CSV original del notebook y exige las mismas 19 variables de entrada.

El entrenamiento **no** se ejecuta al arrancar el servidor ni en cada petición. `start_codespaces.sh` también está diseñado para NO entrenar automáticamente: si no existen los artefactos, muestra instrucciones y se detiene. Guarda y sube los dos archivos a GitHub para evitar el reentrenamiento incluso en Codespaces nuevos.

## 4. Construir y ejecutar Docker en cualquier equipo compatible

```bash
docker build -t riesgo-crediticio-faseii:1.0 .
docker run --rm -p 8000:8000 riesgo-crediticio-faseii:1.0
```

En otra terminal:

```bash
curl http://localhost:8000/api/health
bash scripts/smoke_docker.sh
```

La app escucha en el puerto 8000. Las rutas son `GET /`, `/docs`, `GET /api/health`, `GET /api/modelo` y `POST /api/predecir`.

## 5. Ejemplo de petición

```json
{
  "LIMIT_BAL": 120000,
  "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
  "BILL_AMT1": 1000, "BILL_AMT2": 1000, "BILL_AMT3": 1000,
  "BILL_AMT4": 1000, "BILL_AMT5": 1000, "BILL_AMT6": 1000,
  "PAY_AMT1": 100, "PAY_AMT2": 100, "PAY_AMT3": 100,
  "PAY_AMT4": 100, "PAY_AMT5": 100, "PAY_AMT6": 100
}
```

`POST /api/predecir` devuelve un número entre 0 y 1, un umbral aprendido, la bandera `alerta` y la advertencia de uso educativo. No se incluyen datos de personas identificables.

## 6. Qué se conserva del notebook original

- Conjunto `uciml/default-of-credit-card-clients-dataset` de 30,000 filas y hash SHA256 `a0f0ab49d6326671d6cd83be5c88dcf18007025fe9a53ecd699119c871176ca1`.
- Exclusión de ID, sexo, educación, estado civil y edad como predictores. Estas exclusiones no constituyen una evaluación de equidad.
- 19 variables de historial crediticio y pagos; división estratificada 60% entrenamiento, 20% validación y 20% prueba; semilla 42.
- `HistGradientBoostingClassifier` con imputación mediana y `GridSearchCV` (5 folds y cuatro combinaciones de hiperparámetros).
- Selección del umbral en validación, con recall >= 0.70 y costos FN=5 / FP=1 estrictamente ilustrativos; puede diferir del 0.14 del notebook si cambia el entorno de entrenamiento.
- Evaluación única sobre prueba independiente y reporte de resultados en `metadata.json`.

Los resultados que aparecen en el notebook (por ejemplo ROC-AUC cercano a 0.777 y umbral 0.14) son resultados **históricos** y no se presentan como ejecución verificada en este paquete. Los valores obtenidos tras un entrenamiento real deben leerse del archivo metadata y de la salida de la terminal.

## 7. Pruebas

```bash
python -m pytest -q
```

Estos tests no usan datos reales ni necesitan Kaggle; validan la interfaz HTTP mediante un doble de pruebas. La prueba `bash scripts/smoke_docker.sh` sí necesita una imagen Docker en ejecución con el modelo real. El workflow manual en GitHub Actions añade la construcción y prueba del contenedor con los artefactos versionados (sin reentrenar).

## 8. Limitaciones y seguridad

- No hacer inferencia con datos de clientes reales; para pruebas se recomiendan ejemplos sintéticos.
- Prohibido enviar información de tarjetas o información sensible al prototipo.
- El dataset externo es necesario para regenerar el modelo; podría cambiar el acceso a la descarga.
- Se verifica el SHA256 de los datos y del archivo modelo; **joblib no es seguro para cargar artefactos no confiables**.
- En Codespaces el puerto debe permanecer privado. No existe autenticación de usuario propia en esta demo.
- Un despliegue de producción requeriría autenticación, monitoreo, auditoría, políticas de seguridad, calibración, validación local y aprobación de riesgo/modelos.
- El paquete actualizado incorpora la solución de persistencia, pero NO incluye el modelo entrenado ni evidencias externas nuevas: el usuario debe ejecutar la preparación inicial en Codespaces, registrar los artefactos en GitHub y documentar pruebas reales. Las capturas compartidas en la conversación han confirmado anteriormente un docker build y un smoke test de inferencia, pero no la funcionalidad del nuevo script.

## 9. Referencias

- Notebook aportado: `original/Actividad_6_Riesgo_Crediticio.ipynb`.
- Dataset: https://www.kaggle.com/datasets/uciml/default-of-credit-card-clients-dataset
- Docker-in-Docker: https://github.com/devcontainers/features/tree/main/src/docker-in-docker
- GitHub Codespaces: https://docs.github.com/en/codespaces
- Port forwarding: https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace

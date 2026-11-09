[README_Fase2.md](https://github.com/user-attachments/files/34561783/README_Fase2.md)

# Evaluación experimental de riesgo crediticio

**Proyecto Fase II | Gestión de Proyectos de Inteligencia Artificial**

Aplicación web que utiliza un modelo `HistGradientBoostingClassifier` para generar una puntuación experimental de incumplimiento a partir de 19 variables de historial crediticio. El formulario está integrado con una API REST creada con FastAPI y se ejecuta en un contenedor Docker.

**Repositorio:** https://github.com/miguelalejandreperez-rgb/riesgo-crediticio-fase-ll

> **Alcance:** demostración académica basada en datos de tarjetas de crédito de Taiwán (2005). La puntuación no está calibrada ni validada para la población mexicana. No utilizar datos personales ni emplear el resultado para aprobar, rechazar o modificar créditos reales.

## 1. Iniciar el formulario en GitHub Codespaces

Esta es la forma recomendada si se trabaja desde Windows 11 sin permisos para instalar programas. Solo se necesita un navegador y acceso al repositorio en GitHub. **No es necesario instalar Python ni Docker en Windows.**

### 1.1 Abrir el entorno

1. Abre el repositorio en GitHub y selecciona **Code > Codespaces**.
2. Si ya existe un Codespace, selecciona **Open**. De lo contrario, elige **Create codespace on main**.
3. Cuando se abra el editor, selecciona **Terminal > New Terminal**.
4. Comprueba que la terminal esté en `/workspaces/riesgo-crediticio-fase-ll`.

### 1.2 Comandos habituales (cada vez que se abra una sesión)

Ejecuta estos comandos, uno por uno, desde la carpeta principal del repositorio:

```bash
# 1. Comprobar que el modelo guardado y sus metadatos son válidos.
python scripts/check_artifacts.py

# 2. Iniciar o recuperar el contenedor Docker. No vuelve a entrenar.
bash scripts/start_codespaces.sh

# 3. Verificar el servicio y realizar una predicción de prueba.
bash scripts/smoke_docker.sh
```

Si el inicio es correcto, la terminal indicará que la aplicación responde en `http://127.0.0.1:8000/` y el script de prueba mostrará `OK: /api/health y /api/predecir con modelo real`.

### 1.3 Abrir el formulario en el navegador

1. En la parte inferior del editor, abre la pestaña **Ports** (Puertos).
2. Localiza el puerto **8000**. Si no aparece, selecciona **Add Port**, escribe `8000` y confirma.
3. Mantén la visibilidad en **Private** y selecciona **Open in Browser**.
4. La ruta `/` abre el formulario **Evaluación experimental de riesgo crediticio**. La ruta `/docs` abre la documentación Swagger de la API.
5. Conserva o ingresa valores de prueba en los 19 campos y pulsa **Calcular puntuación**. La aplicación presentará el porcentaje, el umbral configurado y el estado de alerta.

El enlace del puerto privado funciona mientras el Codespace y el contenedor estén encendidos. No es un sitio de alojamiento público permanente. Si se muestra un error 404 del túnel, vuelve a abrir el enlace desde la pestaña **Ports** y verifica que estés conectado a GitHub con la cuenta autorizada.

### 1.4 Si el contenedor se detiene o desaparece

No es necesario volver a entrenar. Desde la carpeta del repositorio, ejecuta:

```bash
bash scripts/start_codespaces.sh
docker ps
bash scripts/smoke_docker.sh
```

El script recupera un contenedor detenido o lo recrea si ya no existe. Si se cambió el código, el Dockerfile o el archivo del modelo, reconstruye la imagen con:

```bash
bash scripts/start_codespaces.sh --rebuild
```

## 2. Preparación inicial del modelo (solo si faltan los artefactos)

El modelo se conserva en estos dos archivos del repositorio:

- `artifacts/modelo_riesgo.joblib`: pipeline entrenado.
- `artifacts/metadata.json`: variables, umbral y comprobación de integridad SHA256.

Si `python scripts/check_artifacts.py` informa que faltan, ejecuta una sola vez:

```bash
bash scripts/prepare_model.sh
```

El proceso instala las dependencias de entrenamiento **en Codespaces**, recupera los datos públicos, entrena y exporta el modelo. Para conservar los resultados en otros Codespaces, verifica primero que el artefacto sea apto para Git y sube los dos archivos:

```bash
git add artifacts/modelo_riesgo.joblib artifacts/metadata.json
git status --short
git commit -m "Guardar modelo de riesgo crediticio"
git push origin main
```

Si ambos artefactos ya están versionados, **no vuelvas a ejecutar el entrenamiento**. Calcular una puntuación tampoco vuelve a entrenar: utiliza el modelo ya cargado en memoria.

## 3. Requisitos y estructura del repositorio

| Elemento | Funcionalidad |
|---|---|
| `app/main.py` | API REST, carga del formulario y endpoints. |
| `app/schemas.py` | Validación de las 19 variables. |
| `app/service.py` | Carga del modelo y revisión de metadatos. |
| `app/static/` | Formulario HTML, estilos y JavaScript. |
| `artifacts/` | Modelo entrenado y metadatos versionados. |
| `scripts/start_codespaces.sh` | Inicio del contenedor sin reentrenamiento. |
| `scripts/prepare_model.sh` | Preparación inicial, si faltan artefactos. |
| `scripts/smoke_docker.sh` | Verificación de salud e inferencia real. |
| `tests/` | Pruebas unitarias. |
| `.github/workflows/` | Verificación automatizada y construcción de Docker. |
| `docs/` | Manual de despliegue y documento de validación. |

Para construir la imagen en un equipo donde sí está instalado Docker:

```bash
python scripts/check_artifacts.py
docker build -t riesgo-crediticio-faseii:1.0 .
docker run --rm -p 8000:8000 riesgo-crediticio-faseii:1.0
```

En otra terminal, ejecuta `bash scripts/smoke_docker.sh` o abre `http://localhost:8000/`. El procedimiento se probó en GitHub Codespaces; no Se ha comprobado en Windows local.

## 4. Uso de la API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Formulario web. |
| `GET` | `/api/health` | Estado del servicio y del modelo. |
| `GET` | `/api/modelo` | Variables, umbral e información del modelo. |
| `POST` | `/api/predecir` | Puntuación y alerta experimental. |
| `GET` | `/docs` | Documentación interactiva. |

Solicitud JSON de ejemplo para `POST /api/predecir`:

```json
{
  "LIMIT_BAL": 120000,
  "PAY_0": -1, "PAY_2": 2, "PAY_3": 0,
  "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
  "BILL_AMT1": 2682, "BILL_AMT2": 1725, "BILL_AMT3": 2682,
  "BILL_AMT4": 3272, "BILL_AMT5": 3455, "BILL_AMT6": 3261,
  "PAY_AMT1": 0, "PAY_AMT2": 1000, "PAY_AMT3": 1000,
  "PAY_AMT4": 1000, "PAY_AMT5": 0, "PAY_AMT6": 2000
}
```

En la versión probada, esos valores produjeron `puntaje_incumplimiento: 0.27602`, `umbral_alerta: 0.14` y `alerta: true`. La puntuación corresponde exclusivamente a ese artefacto y a esa entrada; no representa una probabilidad de impago calibrada.

**Validaciones:** la API responde `422` ante campos obligatorios ausentes, valores fuera de las restricciones o JSON mal formado. El formulario exige un límite de crédito mínimo de 0.01 y la API exige un valor estrictamente positivo. Esta diferencia de validación se encuentra registrada como mejora pendiente.

## 5. Verificar el proyecto

Desde Codespaces, con el contenedor en marcha:

```bash
bash scripts/smoke_docker.sh
python -m pytest -q
```

En GitHub, abre **Actions > Construir y verificar Docker con modelo versionado > Run workflow**, selecciona `main` y ejecuta el flujo. La ejecución #1 de `docker-validation` concluyó con resultado **Success** sobre el commit `8726777`.

El documento `docs/Validacion_y_Evidencias.pdf` contiene las pruebas del formulario, respuestas HTTP 200 y 422, evidencia de Docker y resultado del workflow.

## 6. Despliegue en la nube

El procedimiento propuesto para **Render (PaaS)** se desarrolla en `docs/Manual_Despliegue.pdf`. El servicio utilizaría el Dockerfile del repositorio, el modelo versionado y una comprobación de salud en `/api/health`.

El despliegue en Render está **documentado, pero no se ejecutó** como parte de las pruebas registradas. GitHub Codespaces se utilizó para ejecutar Docker de manera remota y comprobar el funcionamiento del sistema.

## 7. Solución de problemas

| Mensaje o síntoma | Causa probable y acción |
|---|---|
| `Connection refused` | No hay servidor escuchando: ejecutar `bash scripts/start_codespaces.sh` y revisar `docker ps`. |
| `No such container` | El contenedor anterior ya no existe: ejecutar el script de inicio; lo recrea. |
| `No module named joblib` | Se intentó entrenar sin preparar dependencias: usar `bash scripts/prepare_model.sh` solo si falta el modelo. |
| `HTTP 404` al abrir `app.github.dev` | Abrir el enlace vigente desde **Ports**; confirmar sesión GitHub y puerto privado. |
| `HTTP 422` con `Field required` | Falta una variable obligatoria en el JSON. |
| `HTTP 422` con `JSON decode error` | La solicitud tiene sintaxis JSON incorrecta (coma, comillas o llaves). |
| Docker no arranca tras cambiar el modelo | Ejecutar `python scripts/check_artifacts.py` y reconstruir con `--rebuild`. |

## 8. Límites de uso y referencias

El prototipo utiliza datos históricos de Taiwán de 2005 y una selección de 19 variables; excluye identificadores directos, pero esa exclusión no constituye una validación de equidad. No existe autenticación propia ni controles de privacidad para clientes reales. El sistema se limita a experimentación y demostración educativa.

- Notebook de origen: `original/Actividad_6_Riesgo_Crediticio.ipynb`.
- Dataset: https://www.kaggle.com/datasets/uciml/default-of-credit-card-clients-dataset
- Documentación de Codespaces: https://docs.github.com/en/codespaces
- Documentación de Docker en Render: https://render.com/docs/docker

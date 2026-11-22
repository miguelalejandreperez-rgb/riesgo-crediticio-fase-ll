# Evaluación experimental de riesgo crediticio

**Proyecto Fase II | Gestión de Proyectos de Inteligencia Artificial**

Aplicación web que calcula un puntaje experimental de incumplimiento a partir de 19 variables de historial crediticio. Integra un modelo `HistGradientBoostingClassifier`, una API REST con FastAPI, un formulario web y un contenedor Docker.

**Repositorio:** https://github.com/miguelalejandreperez-rgb/riesgo-crediticio-fase-ll

> **Uso académico.** El modelo fue desarrollado con datos históricos de tarjetas de crédito de Taiwán (2005). Su resultado no representa una probabilidad calibrada para México y no debe utilizarse para aprobar, rechazar o modificar créditos reales. No introduzca datos personales.

## 1. Inicio rápido: abrir el formulario en GitHub Codespaces

No es necesario instalar Python, Docker Desktop ni Visual Studio Code en la computadora. La construcción y ejecución del contenedor se realizan dentro de GitHub Codespaces.

### 1.1 Crear un Codespace desde el repositorio

1. Abra el [repositorio del proyecto](https://github.com/miguelalejandreperez-rgb/riesgo-crediticio-fase-ll) e inicie sesión en GitHub.
2. Seleccione **Code > Codespaces > Create codespace on main**. Si aparece **New with options**, elija la rama `main` y la configuración `.devcontainer/devcontainer.json` del repositorio.
3. Espere a que el editor se abra y termine de preparar el entorno.
4. Abra la terminal desde **Terminal > New Terminal**.

### 1.2 Ejecutar los comandos

En la terminal del Codespace, desde la raíz del repositorio, ejecute **en este orden**:

```bash
# 1. Comprobar que Docker está disponible
docker --version
docker info

# 2. Verificar que el modelo entrenado está guardado
python scripts/check_artifacts.py

# 3. Construir o iniciar el contenedor
bash scripts/start_codespaces.sh

# 4. Confirmar que la aplicación está activa
docker ps

# 5. Probar la API y realizar una predicción
bash scripts/smoke_docker.sh
```

Si todo está correcto, la prueba final muestra:

```text
OK: /api/health y /api/predecir con modelo real
```

El comando `start_codespaces.sh` **no vuelve a entrenar el modelo**: utiliza `artifacts/modelo_riesgo.joblib` y `artifacts/metadata.json`, que ya están guardados en el repositorio. En un Codespace nuevo construye la imagen Docker cuando es necesario y crea el contenedor `riesgo-crediticio-demo`.

### 1.3 Abrir el formulario

1. En el panel inferior del editor, abra **Ports / Puertos**.
2. Busque el puerto **8000**. Si no aparece, seleccione **Add Port** y escriba `8000`.
3. Mantenga la visibilidad **Private**.
4. Seleccione **Open in Browser** sobre la dirección del puerto.
5. Capture las variables de prueba y seleccione **Calcular puntuación**.

La ruta principal `/` muestra el formulario. La ruta `/docs` abre la documentación interactiva de la API (Swagger UI).

**Acceso:** cada persona utiliza su propio Codespace; hacer público el repositorio no permite entrar a los Codespaces privados de otras cuentas. La aplicación en Codespaces solo está disponible mientras el entorno y su contenedor están activos.

## 2. Utilizar el proyecto en sesiones posteriores

Cuando abra nuevamente el mismo Codespace, compruebe Docker y reinicie la aplicación con estos comandos:

```bash
docker info
python scripts/check_artifacts.py
bash scripts/start_codespaces.sh
bash scripts/smoke_docker.sh
```

Luego abra el puerto **8000** en **Ports**. No ejecute `prepare_model.sh` en cada sesión. Si el contenedor desapareció al reiniciar el entorno, `start_codespaces.sh` lo recreará con el modelo existente.

Si cambió el código de la aplicación, las dependencias o el archivo del modelo, reconstruya expresamente la imagen:

```bash
bash scripts/start_codespaces.sh --rebuild
bash scripts/smoke_docker.sh
```

## 3. Solución de problemas de Codespaces y Docker

### 3.1 `docker: command not found` o `Docker no está disponible`

1. Si el Codespace inicia en **Recovery Mode**, consulte **Ctrl + Shift + P > Codespaces: View Creation Log** para identificar el error.
2. Desde el editor seleccione **Ctrl + Shift + P > Codespaces: Rebuild Container**.
3. Si el problema persiste, cree un Codespace nuevo desde la rama `main`.
4. Verifique con `docker info` que el motor Docker está disponible antes de iniciar la aplicación.

**No instale Docker manualmente desde la terminal de recuperación.** Corrija primero el entorno de desarrollo.

### 3.2 `Connection refused` al ejecutar las pruebas

Compruebe si el contenedor está iniciado:

```bash
docker ps -a
bash scripts/start_codespaces.sh
curl -i http://127.0.0.1:8000/api/health
```

Una respuesta `HTTP/1.1 200 OK` en `/api/health` confirma que la API está disponible. Para probar también la inferencia use `bash scripts/smoke_docker.sh`.

Si el contenedor se detiene, consulte sus registros:

```bash
docker logs --tail 80 riesgo-crediticio-demo
```

### 3.3 `No such container: riesgo-crediticio-demo`

El contenedor no existe en este entorno Docker. Ejecute:

```bash
bash scripts/start_codespaces.sh
```

El script creará un contenedor nuevo sin volver a entrenar el modelo.

### 3.4 Error `404` en la dirección `app.github.dev`

Abra la dirección vigente directamente desde la pestaña **Ports**, compruebe que el puerto 8000 sea privado y que su sesión de GitHub siga iniciada. Para separar el problema del navegador de la aplicación, compruebe:

```bash
curl -i http://127.0.0.1:8000/
```

### 3.5 Falta el modelo o sus metadatos

Compruebe primero el estado del repositorio y los artefactos:

```bash
python scripts/check_artifacts.py
ls -lh artifacts/modelo_riesgo.joblib artifacts/metadata.json
```

En la versión publicada estos archivos deben estar disponibles. Si faltan y el repositorio está actualizado, su generación se realiza **una sola vez** mediante:

```bash
bash scripts/prepare_model.sh
```

El entrenamiento descarga datos públicos y requiere sus dependencias. Tras completarlo, deben conservarse ambos artefactos en el repositorio. Para el uso ordinario del formulario **no hace falta entrenar de nuevo**.

### 3.6 Errores de validación HTTP 422

FastAPI devuelve `422` cuando falta una variable obligatoria, hay valores que incumplen restricciones o el cuerpo JSON tiene un error de sintaxis. Consulte el detalle de respuesta en `/docs` para identificar el campo o la posición del error. Una solicitud mal formada no equivale a una prueba del comportamiento predictivo del modelo.

## 4. Arquitectura y archivos principales

```text
Navegador (formulario HTML/CSS/JavaScript)
      |
      | HTTP / JSON
      v
FastAPI (app/main.py, app/schemas.py)
      |
      v
Modelo guardado (artifacts/modelo_riesgo.joblib)
      |
      v
Puntuación y alerta experimental
```

| Ruta | Contenido |
|---|---|
| `.devcontainer/devcontainer.json` | Configuración del entorno Codespaces y del puerto 8000. |
| `app/main.py` | API REST y entrega del formulario. |
| `app/schemas.py` | Validación de los 19 campos de entrada. |
| `app/static/` | Página web, estilos y JavaScript. |
| `artifacts/modelo_riesgo.joblib` | Modelo entrenado. |
| `artifacts/metadata.json` | Metadatos, umbral de alerta y hash SHA256. |
| `scripts/check_artifacts.py` | Comprueba que el modelo y sus metadatos estén íntegros. |
| `scripts/start_codespaces.sh` | Inicia o recupera Docker sin reentrenar. |
| `scripts/smoke_docker.sh` | Prueba de salud e inferencia. |
| `scripts/prepare_model.sh` | Entrenamiento inicial solo cuando faltan artefactos. |
| `.github/workflows/` | Pruebas automáticas y validación del contenedor. |
| `docs/` | Manual de despliegue y documento de validación y pruebas. |

## 5. Consultar la API

| Método | Ruta | Función |
|---|---|---|
| `GET` | `/` | Formulario web. |
| `GET` | `/api/health` | Estado del servicio y disponibilidad del modelo. |
| `GET` | `/api/modelo` | Información del modelo, variables y umbral. |
| `POST` | `/api/predecir` | Puntuación e indicador de alerta. |
| `GET` | `/docs` | Interfaz interactiva Swagger UI. |

Ejemplo de solicitud a `POST /api/predecir`:

```json
{
  "LIMIT_BAL": 120000,
  "PAY_0": -1,
  "PAY_2": 2,
  "PAY_3": 0,
  "PAY_4": 0,
  "PAY_5": 0,
  "PAY_6": 0,
  "BILL_AMT1": 2682,
  "BILL_AMT2": 1725,
  "BILL_AMT3": 2682,
  "BILL_AMT4": 3272,
  "BILL_AMT5": 3455,
  "BILL_AMT6": 3261,
  "PAY_AMT1": 0,
  "PAY_AMT2": 1000,
  "PAY_AMT3": 1000,
  "PAY_AMT4": 1000,
  "PAY_AMT5": 0,
  "PAY_AMT6": 2000
}
```

Con el modelo validado, esta entrada produjo `puntaje_incumplimiento: 0.27602`, `umbral_alerta: 0.14` y `alerta: true`. Se trata de una puntuación experimental no calibrada, no de una recomendación crediticia.

## 6. Pruebas y verificación automática

Con el contenedor activo:

```bash
bash scripts/smoke_docker.sh
```

Para ejecutar las pruebas unitarias de Python, instale las dependencias de desarrollo **en el Codespace**, si aún no están disponibles, y ejecute:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

En GitHub, la ruta **Actions > Construir y verificar Docker con modelo versionado > Run workflow** permite ejecutar la validación automática. La ejecución #1 sobre el commit `8726777` finalizó correctamente.

Las evidencias de construcción, integración del formulario y API, respuestas `200`/`422`, consistencia de inferencia y resultados de GitHub Actions se documentan en `docs/Validacion_y_Evidencias.pdf`.

## 7. Ejecutar con Docker fuera de Codespaces

En cualquier equipo que tenga un motor Docker funcional, desde la raíz del repositorio:

```bash
python scripts/check_artifacts.py
docker build -t riesgo-crediticio-faseii:1.0 .
docker run --rm -p 8000:8000 riesgo-crediticio-faseii:1.0
```

En el navegador, abra `http://localhost:8000/`. Si se ejecuta el contenedor en primer plano, la terminal permanecerá ocupada mientras el servicio esté activo. Para detenerlo utilice `Ctrl + C`.

## 8. Despliegue en la nube y alcance

El manual `docs/Manual_Despliegue.pdf` incluye el procedimiento propuesto para publicar la aplicación mediante Docker en **Render (PaaS)**. Esa publicación es independiente de Codespaces y no forma parte de las pruebas de despliegue realizadas hasta ahora.

GitHub Codespaces sirve para construir, ejecutar y verificar el contenedor en un entorno remoto. **No equivale a alojar el formulario públicamente de manera permanente**. El acceso por puertos reenviados puede requerir autenticación y el entorno puede detenerse por inactividad.

## 9. Referencias

- Datos de origen: https://www.kaggle.com/datasets/uciml/default-of-credit-card-clients-dataset
- GitHub Codespaces: https://docs.github.com/en/codespaces
- Documentación de FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/
- Render: https://render.com/docs/docker

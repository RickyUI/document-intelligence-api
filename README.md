# Document Intelligence API

Este proyecto consiste en una API de procesamiento de documentos diseñada para realizar análisis semántico sobre archivos PDF. Utiliza técnicas de Generación Aumentada por Recuperación (RAG) para permitir consultas en lenguaje natural, manteniendo la coherencia a través de una memoria conversacional integrada.

---

## Funcionalidades Principales

* **Pipeline RAG:** Extracción y fragmentación de texto de PDFs para búsqueda semántica eficiente.
* **Memoria de Sesión:** Implementación de historial de conversación para permitir preguntas de seguimiento contextualmente relevantes.
* **Arquitectura de Microservicios:** Backend construido con FastAPI para asegurar baja latencia y escalabilidad.
* **Integración con LLM:** Uso de los modelos de Claude (Anthropic) para el razonamiento y la síntesis de respuestas.

---

## Estructura del Proyecto

```text
document-intel-api/
├── app/
│   ├── core/            # Configuraciones globales y manejo de variables de entorno.
│   ├── models/          # Esquemas de Pydantic para la validación de peticiones y respuestas.
│   ├── services/        # Servicios de procesamiento: RAG, extracción de PDF y lógica de FAISS.
│   └── main.py          # Punto de entrada de la aplicación y definición de rutas.
├── data/                # Directorio destinado al almacenamiento temporal de archivos cargados.
├── faiss_index/         # Directorio para la persistencia del índice vectorial local.
├── .env.example         # Referencia de las variables de entorno necesarias para la ejecución.
└── TODO.md              # Documento de seguimiento de tareas y fases de desarrollo.
```

---

## Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Framework Web:** FastAPI
* **Orquestación de IA:** LangChain
* **Motor de Búsqueda Vectorial:** FAISS (Facebook AI Similarity Search)
* **Modelo de Lenguaje:** Anthropic Claude API
* **Procesamiento de Documentos:** PyPDF

---

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/usuario/document-intel-api.git
cd document-intel-api
```

### 2. Gestión del Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En sistemas Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuración de Variables

Es necesario crear un archivo `.env` basado en el archivo de ejemplo para incluir las credenciales de acceso a la API de Anthropic:

```bash
cp .env.example .env
```

### 4. Ejecución del Servidor

Para iniciar la API en modo de desarrollo con recarga automática:

```bash
uvicorn app.main:app --reload
```

---

## Interfaz de Desarrollo

Una vez el servidor esté en ejecución, la documentación técnica y las pruebas de los endpoints (Swagger UI) están disponibles en la ruta local:

http://127.0.0.1:8000/docs

---

Este repositorio ha sido estructurado siguiendo estándares de ingeniería de software para facilitar su integración en entornos de producción y evaluación técnica.

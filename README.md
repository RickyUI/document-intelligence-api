# FinWise

FinWise es una aplicacion para analizar documentos financieros en PDF con un flujo RAG. El backend expone una API REST en FastAPI para subir archivos, indexarlos con FAISS y responder preguntas en lenguaje natural usando OpenAI. Ademas, el proyecto ya incluye `app/app.py`, archivo reservado para construir el frontend con Gradio.

## Estado actual del proyecto

- Backend API en FastAPI funcional.
- Carga de multiples PDFs al directorio `uploads/`.
- Procesamiento de PDFs con `PyPDFLoader` y fragmentacion con `RecursiveCharacterTextSplitter`.
- Indexacion semantica en memoria con FAISS y embeddings de OpenAI.
- Consulta de documentos con un flujo RAG y devolucion de fuentes.
- `app/app.py` agregado como punto de partida para el frontend con Gradio.
- `llm_service.py` ya no forma parte del proyecto.

## Stack tecnologico

- FastAPI
- Gradio
- LangChain
- OpenAI
- FAISS
- PyPDF
- Python dotenv

## Estructura del proyecto

```text
app/
|-- app.py                  # Frontend en Gradio (en construccion)
|-- main.py                 # App FastAPI y ciclo de vida del backend
|-- core/
|   |-- config.py
|   `-- constants.py
|-- models/
|   `-- schemas.py          # Modelos de request y response
|-- routers/
|   |-- upload.py           # POST /upload/
|   |-- index.py            # POST /index/
|   `-- query.py            # POST /query/
`-- services/
    |-- processor.py        # Carga y fragmentacion de PDFs
    `-- vector_store.py     # Gestion del indice FAISS
```

## Flujo de la aplicacion

1. El usuario sube uno o varios PDF a `/upload/`.
2. El backend guarda los archivos en `uploads/`.
3. Se llama `/index/` para cargar, dividir e indexar los documentos.
4. Se consulta `/query/` con una pregunta en lenguaje natural.
5. El sistema recupera contexto relevante y genera una respuesta con sus fuentes.

## Endpoints disponibles

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| POST | `/upload/` | Recibe y guarda uno o varios archivos PDF |
| POST | `/index/` | Procesa los PDFs guardados y construye el indice FAISS |
| POST | `/query/` | Responde preguntas usando los documentos indexados |

## Variables de entorno

Crea un archivo `.env` a partir de `.env.example`:

```env
OPENAI_API_KEY=sk-...
```

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion del backend

```bash
uvicorn app.main:app --reload
```

Documentacion interactiva:

```text
http://localhost:8000/docs
```

## Frontend con Gradio

El archivo `app/app.py` se dejo como base para construir la interfaz en Gradio. En el estado actual del repositorio, ese frontend todavia no implementa la UI completa ni reemplaza al backend FastAPI; la API sigue siendo la parte funcional principal del proyecto.

## Notas tecnicas

- El indice FAISS vive en memoria y se reinicia cuando el servidor se apaga.
- `app.state.vector_store` comparte la instancia del vector store entre los routers.
- La logica de consulta al LLM esta actualmente dentro de `app/routers/query.py`.
- Si vas a avanzar con la interfaz Gradio, `app/app.py` es ahora el archivo correcto para ese trabajo.

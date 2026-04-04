# FinWise

API REST construida con FastAPI que permite cargar multiples documentos PDF financieros, indexarlos semanticamente con FAISS y OpenAI Embeddings, y consultarlos en lenguaje natural usando RAG (Retrieval-Augmented Generation). El sistema responde citando la fuente exacta, incluyendo documento y pagina, de donde proviene la informacion. El frontend esta construido con Gradio.

## Sobre el proyecto

FinWise esta orientado al analisis de reportes trimestrales, estados financieros, earnings calls y otros documentos corporativos en PDF. El flujo principal consiste en cargar archivos, procesarlos en chunks, generar embeddings, indexarlos en FAISS y luego responder preguntas en lenguaje natural recuperando primero el contexto mas relevante.

## Stack tecnologico

- **Backend:** FastAPI
- **LLM:** OpenAI GPT-4o-mini
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Vector Store:** FAISS (en memoria)
- **Chunking:** LangChain `RecursiveCharacterTextSplitter`
- **PDF Loader:** LangChain `PyPDFLoader`
- **Frontend:** Gradio
- **Orquestacion LLM:** LangChain LCEL (`Runnable`)

## Estructura del proyecto

```text
app/
├── core/
│   ├── config.py          # Configuracion general de la aplicacion
│   └── constants.py       # Constantes globales (UPLOAD_DIR, modelos, etc.)
├── models/
│   └── schemas.py         # Modelos Pydantic para request/response
├── routers/
│   ├── upload.py          # POST /upload/ — recibe y guarda PDFs en disco
│   ├── index.py           # POST /index/ — chunking e indexing en FAISS
│   └── query.py           # GET  /query/ — consultas RAG con citacion de fuentes
├── services/
│   ├── processor.py       # PDFProcessor — carga y divide PDFs en chunks
│   ├── vector_store.py    # VectorStore — gestiona embeddings e indice FAISS
│   └── llm_service.py     # Servicio LLM — cadena RAG con prompt financiero
└── main.py                # Punto de entrada — lifespan, routers, app.state
```

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/upload/` | Recibe uno o varios PDFs y los guarda en disco |
| POST | `/index/` | Procesa los PDFs guardados y los indexa en FAISS |
| GET | `/query/` | Consulta en lenguaje natural sobre los documentos indexados |

## Flujo de la aplicacion

```text
Usuario sube PDFs -> /upload/ guarda en disco
                  -> /index/ genera chunks + embeddings + indexa en FAISS
                  -> /query/ recupera contexto relevante + LLM genera respuesta con fuentes
```

## Variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```env
OPENAI_API_KEY=sk-...
```

## Instalacion y uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr el servidor
uvicorn app.main:app --reload

# Acceder a la documentacion interactiva
http://localhost:8000/docs
```

## Notas de diseno

- FAISS corre en memoria, por lo que el indice se reconstruye llamando a `/index/` en cada sesion del servidor. La arquitectura esta preparada para migrar a una base vectorial persistente como Pinecone o pgvector.
- La instancia de `VectorStore` se comparte entre todos los endpoints usando `app.state` de FastAPI.
- Los servicios como `PDFProcessor` y `VectorStore` son independientes de FastAPI: no conocen `HTTPException` ni conceptos del framework, lo que facilita probarlos de forma aislada.

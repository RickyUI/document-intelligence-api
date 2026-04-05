from typing import List
from fastapi import APIRouter, File, Request, UploadFile, HTTPException
from app.models.schemas import UploadResponse
import os

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"application/pdf"}


@router.post("/", status_code=201, response_model=UploadResponse)
async def upload_file(files: List[UploadFile] = File(...)):
    """Endpoint para subir archivos PDF al servidor. Valida que los archivos sean PDFs válidos y los guarda en el directorio de uploads."""
    # 1. Validar todos los archivos antes de guardar
    for f in files:
        if not f.content_type or f.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail=f"Archivo '{f.filename}' no es un PDF válido.")
        
    # 2. Guardar los archivos válidos
    saved_files = []
    for f in files:
        file_path = os.path.join(UPLOAD_DIR, f.filename)
        try:
            with open(file_path, "wb") as buffer:
                content = await f.read() # Lee el contenido del archivo sin bloquearl el servidor, permitiendo que otros usuarios sean atentidos durante la espera
                buffer.write(content)
            saved_files.append(f.filename)
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar el archivo '{f.filename}': {str(e)}")
        
    return UploadResponse(
        message=f"{len(saved_files)} archivo(s) subido(s) exitosamente.",
        files=saved_files
    )


@router.get("/files", response_model=List[str])
async def get_uploaded_files():
    """Endpoint para obtener la lista de archivos subidos."""
    if not (os.path.exists(UPLOAD_DIR) and os.path.isdir(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="El directorio de uploads no existe o no es un directorio válido.")
    return os.listdir(UPLOAD_DIR)


@router.delete("/delete", status_code=200)
async def delete_uploaded_files(request: Request):
    """Endpoint para eliminar todos los archivos subidos."""
    if not (os.path.exists(UPLOAD_DIR) and os.path.isdir(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="El directorio de uploads no existe o no es un directorio válido.")
    
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            os.remove(file_path)
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Error al eliminar el archivo '{filename}': {str(e)}")
    
    vector_store = request.app.state.vector_store
    vector_store.reset()
    
    return {
        "message": "Todos los archivos subidos han sido eliminados y el vector store ha sido reiniciado."
    }
    


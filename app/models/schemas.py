# models/schemas.py
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    response: str
    sources: list[str]

class IndexResponse(BaseModel):
    message: str
    files: list[str]

class UploadResponse(BaseModel):
    message: str
    files: list[str]
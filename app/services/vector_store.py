from langchain_community.vectorstores import FAISS


class VectorStore:
    """Clase para almacenar los vectores de los fragmentos de texto utilizando OpenAIEmbeddings."""
    def __init__(self, embeddings):
        self._embeddings = embeddings
        self._vector_store = None
        
    def create_vector_store(self, chunks):
        try:
            # Creando el vector store utilizando FAISS y los embeddings generados por OpenAIEmbeddings
            self._vector_store = FAISS.from_documents(chunks, self._embeddings)
            return self._vector_store
        except Exception as e:
            raise RuntimeError(f"Error al crear el vector store: {str(e)}")

    def get_retriever(self, k: int = 10):
        if self._vector_store is None:
            raise ValueError("El vector store no ha sido creado.")
        return self._vector_store.as_retriever(search_kwargs={"k": k}) # Devuelve un objeto retriever para realizar consultas de similitud en el vector store

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFProcessor:
    '''Clase para procesar archivos PDF, cargarlos y dividirlos en fragmentos utilizando PyPDFLoader y RecursiveCharacterTextSplitter.'''
    def __init__(self, file_path):
        self.file_path = file_path
    def load_and_split(self):
        loader = PyPDFLoader(self.file_path)
        
        # Cargando el documento PDF
        documents = loader.load()
        
        # Dividiendo el documento en fragmentos utilizando RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        # Devolviendo los fragmentos resultantes -> chunks
        return chunks

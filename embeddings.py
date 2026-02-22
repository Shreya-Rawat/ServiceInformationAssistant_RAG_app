from config import model_name
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


vector_store = None

def create_embeddings(model_name, text: str, filename: str):
    global vector_store
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    if embeddings:
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = splitter.split_text(text)

        documents = []
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "chunk_id": i
                    }
                )
            )

        # persist the vector store in module-level variable for retrieval later
        vector_store = FAISS.from_documents(documents=documents, embedding=embeddings) 
        return chunks
    return 'embedder not initializing'

def get_vector_store():
    return vector_store

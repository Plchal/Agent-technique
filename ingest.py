import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

PDF_DIR = "data"
PERSIST_DIR = "storage"

def main():
    # Embeddings 100% local
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Lire les PDFs
    documents = SimpleDirectoryReader(PDF_DIR).load_data()

    # Chroma local persistant
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = chroma_client.get_or_create_collection("revue_technique")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Création index
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    print("Index local créé dans ./storage")

if __name__ == "__main__":
    main()


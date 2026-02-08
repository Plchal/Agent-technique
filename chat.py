import chromadb
from llama_index.core import StorageContext, VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

PERSIST_DIR = "storage"

def main():
    # ------------------------------
    # 1️⃣ Embeddings locaux
    # ------------------------------
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ------------------------------
    # 2️⃣ LLM léger 100% local
    # ------------------------------
    Settings.llm = Ollama(
        model="llama3.2:1b",
        request_timeout=120.0
    )

    # ------------------------------
    # 3️⃣ Charger index Chroma
    # ------------------------------
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = chroma_client.get_or_create_collection("revue_technique")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # ------------------------------
    # 4️⃣ Préparer le query engine
    # ------------------------------
    query_engine = index.as_query_engine(
        similarity_top_k=5
    )

    print("Agent RAG prêt. Tape ta question (ou 'exit').")

    while True:
        q = input("\n> ")
        if q.lower() in ["exit", "quit"]:
            break

        res = query_engine.query(q)

        print("\n--- Réponse ---")
        print(res)

        # Afficher les sources (page, section) si elles existent
        if hasattr(res, "source_nodes"):
            print("\n--- Sources ---")
            for n in res.source_nodes:
                meta = getattr(n, "metadata", {})
                page = meta.get("page", "??")
                section = meta.get("section", "??")
                print(f"Page: {page}, Section: {section}")

if __name__ == "__main__":
    main()

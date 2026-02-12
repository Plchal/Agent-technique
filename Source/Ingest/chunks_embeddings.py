import ollama
from embedding import embedding

def get_embeddings_for_chunks(langchain_chunks):
    vector_data = []
    for i, chunk in enumerate(langchain_chunks):
        response = embedding(chunk.page_content)
        vector_data.append({
            "content": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": response["embedding"]
        })
        print(f"Chunk {i+1} transformé")
    return vector_data
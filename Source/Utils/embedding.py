import ollama


def embedding(texte: str):
    vector = ollama.embeddings(model="nomic-embed-text", prompt=texte)
    return vector
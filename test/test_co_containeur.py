import ollama

try:
    response = ollama.embeddings(model="nomic-embed-text", prompt="test")
    print("Connexion réussie")
    print(f"Dimension du vecteur : {len(response['embedding'])}")
except Exception as e:
    print(f"Erreur de connexion : {e}")
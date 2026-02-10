from load_pdf import loader
from splitter import text_splitter
from embeddings import get_embeddings_for_chunks
from store import upload_data_with_snowpark

def main():
    docs =loader("../data/RTAktm125duke.pdf")
    chunks = text_splitter(docs)
    vector_data = get_embeddings_for_chunks(chunks)
    print(f"\nNombre total de vecteurs créés : {len(vector_data)}")
    print(f"Dimension du vecteur : {len(vector_data[0]['embedding'])}")

    if len(vector_data[0]['embedding']) == 768:
        print("Les vecteurs font bien 768")
    upload_data_with_snowpark(vector_data)


if __name__ == "__main__":
    main()


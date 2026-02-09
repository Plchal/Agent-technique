from load_pdf import loader
from splitter import text_splitter


def main():
    docs =loader("../../data/RTAktm125duke.pdf")
    chunks = text_splitter(docs)
    print(f"Nombre de chunks créés : {len(chunks)}")
    print(f"Exemple de contenu : {chunks[0].page_content}")
    print(f"Exemple de contenu : {chunks[len(chunks) - 1].page_content}")
    

if __name__ == "__main__":
    main()
from load_pdf import loader


def main():
    docs =loader("../../data/RTAktm125duke.pdf")
    print(f"J'ai récupéré {len(docs)} pages.")
    print(docs[0].page_content) 
    print(docs[0].metadata['page'])
    

if __name__ == "__main__":
    main()
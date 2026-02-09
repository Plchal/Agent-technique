from load_pdf import loader
from splitter import text_splitter

def main():
    docs =loader("../data/RTAktm125duke.pdf")
    chunks = text_splitter(docs)
    

if __name__ == "__main__":
    main()


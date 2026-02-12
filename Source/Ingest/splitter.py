from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_splitter(pages)-> list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chumks = text_splitter.split_documents(pages)
    return chumks
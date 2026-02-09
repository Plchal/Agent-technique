from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def loader(file_path: str)-> list[Document]:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs
import uuid

from utils import embedding, get_snowpark_session, SNOWFLAKE_TABLE_NAME

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from snowflake.snowpark.functions import col
from snowflake.snowpark.types import VectorType


def upload_data_with_snowpark(vector_data):
    
    session = get_snowpark_session()
    try :
        data_with_id = []
        for row in vector_data:
            new_row = (str(uuid.uuid4()), row['content'], row['metadata'], row['embedding'])
            data_with_id.append(new_row)
        
        df = session.create_dataframe(
            data_with_id,
            schema=["ID", "CONTENT", "METADATA", "EMBEDDING"]
        )

        df = df.with_column(
            "EMBEDDING",
            col("EMBEDDING").cast(VectorType(float, 768))
        )

        df.write.mode("append").save_as_table(SNOWFLAKE_TABLE_NAME)

    except Exception as e:
        raise e
    finally:
        session.close()

def text_splitter(pages)-> list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chumks = text_splitter.split_documents(pages)
    return chumks


def loader(file_path: str)-> list[Document]:
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs


def get_embeddings_for_chunks(langchain_chunks):
    vector_data = []
    for i, chunk in enumerate(langchain_chunks):
        response = embedding(chunk.page_content)
        vector_data.append({
            "content": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": response["embedding"]
        })
    return vector_data


def ingest_pdf(path: str):
    try:
        docs = loader(path)

        if not docs:
            assert FileNotFoundError

        chunks = text_splitter(docs)
        vector_data = get_embeddings_for_chunks(chunks)
        upload_data_with_snowpark(vector_data)

    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise e
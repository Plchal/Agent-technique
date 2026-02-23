import uuid
import os

from pathlib import Path
from utils import embedding, get_snowpark_session
from utils import SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from snowflake.snowpark.functions import col
from snowflake.snowpark.types import VectorType
from snowflake.snowpark import Session

TABLE_DOCUMENTS = "RAG_DB.RAG_SCHEMA.DOCUMENTS"
TABLE_CHUNKS = "RAG_DB.RAG_SCHEMA.DOCUMENT_CHUNKS"




def create_infrastructure():
    connection_parameters = {
        "account": SNOWFLAKE_ACCOUNT,
        "user": SNOWFLAKE_USER,
        "password": SNOWFLAKE_PASSWORD,
        "role": SNOWFLAKE_ROLE,
        "warehouse": SNOWFLAKE_WAREHOUSE
    }

    session = Session.builder.configs(connection_parameters).create()
    
    try:
        session.sql("CREATE DATABASE IF NOT EXISTS RAG_DB").collect()
        session.sql("CREATE SCHEMA IF NOT EXISTS RAG_DB.RAG_SCHEMA").collect()

        session.sql(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_DOCUMENTS} (
                DOC_ID STRING PRIMARY KEY,
                FILE_NAME STRING,
                BRAND STRING,
                MODEL STRING,
                YEAR INT,
                UPLOAD_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            );

        """).collect()

        session.sql(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_CHUNKS} (
                ID STRING DEFAULT UUID_STRING(),
                DOC_ID STRING,
                CONTENT STRING,
                METADATA VARIANT,
                EMBEDDING VECTOR(FLOAT, 768),
                FOREIGN KEY (DOC_ID) REFERENCES {TABLE_DOCUMENTS}(DOC_ID)
            );
        """).collect()
        return 0
    except Exception as e:
        print(f"\nError : {e}")
        raise e
    finally:
        session.close()

def upload_data_with_snowpark(vector_data, file_name: str, brand: str, model: str, year: int):
    
    session = get_snowpark_session()
    try :
        doc_id = str(uuid.uuid4())
        session.sql(f"""
            INSERT INTO {TABLE_DOCUMENTS} (DOC_ID, FILE_NAME, BRAND, MODEL, YEAR)
            VALUES ('{doc_id}', '{file_name}', '{brand}', '{model}', {int(year)})
        """).collect()

        data_with_id = []
        for row in vector_data:
            new_row = (str(uuid.uuid4()), doc_id, row['content'], row['metadata'], row['embedding'])
            data_with_id.append(new_row)
        
        df = session.create_dataframe(
            data_with_id,
            schema=["ID", "DOC_ID", "CONTENT", "METADATA", "EMBEDDING"]
        )

        df = df.with_column(
            "EMBEDDING",
            col("EMBEDDING").cast(VectorType(float, 768))
        )

        df.write.mode("append").save_as_table(TABLE_CHUNKS)

    except Exception as e:
        raise e
    finally:
        session.close()

def text_splitter(pages)-> list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=90,
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


def ingest_pdf(path: str, brand: str, model: str, year: int):
    try:
        create_infrastructure()

        file_name = Path(path).name

        docs = loader(path)

        if not docs:
            assert FileNotFoundError

        chunks = text_splitter(docs)
        vector_data = get_embeddings_for_chunks(chunks)
        upload_data_with_snowpark(vector_data, file_name, brand, model, year)
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise e
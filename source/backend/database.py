from snowflake.snowpark import Session
from utils import SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE


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
        session.sql("CREATE OR REPLACE DATABASE RAG_DB").collect()
        
        session.sql("CREATE OR REPLACE SCHEMA RAG_DB.RAG_SCHEMA").collect()

        session.sql("""
            CREATE OR REPLACE TABLE RAG_DB.RAG_SCHEMA.DOCUMENT_CHUNKS (
                ID STRING DEFAULT UUID_STRING(),
                CONTENT STRING,
                METADATA VARIANT,
                EMBEDDING VECTOR(FLOAT, 768)
            )
        """).collect()
        return 0
    except Exception as e:
        print(f"\nErreur : {e}")
        return 1
    finally:
        session.close()
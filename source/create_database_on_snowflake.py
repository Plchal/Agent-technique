import os
from snowflake.snowpark import Session
from dotenv import load_dotenv

load_dotenv()

def create_infrastructure():
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
    }

    print("Connexion en cours...")
    session = Session.builder.configs(connection_parameters).create()
    
    try:
        print("Création de la base RAG_DB via Python")
        session.sql("CREATE OR REPLACE DATABASE RAG_DB").collect()
        
        print("Création du schéma RAG_SCHEMA")
        session.sql("CREATE OR REPLACE SCHEMA RAG_DB.RAG_SCHEMA").collect()

        print("Création de la table DOCUMENT_CHUNKS")
        session.sql("""
            CREATE OR REPLACE TABLE RAG_DB.RAG_SCHEMA.DOCUMENT_CHUNKS (
                ID STRING DEFAULT UUID_STRING(),
                CONTENT STRING,
                METADATA VARIANT,
                EMBEDDING VECTOR(FLOAT, 768)
            )
        """).collect()

        print("\nSUCCÈS")
        print("La base a été recréée par Python.")
        
        print("\nVerification:")
        tables = session.sql("SELECT * FROM RAG_DB.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'DOCUMENT_CHUNKS'").collect()
        if len(tables) > 0:
            print("Python voit bien la table 'DOCUMENT_CHUNKS'.")
        else:
            print("La table a été créée mais reste invisible.")

    except Exception as e:
        print(f"\nErreur : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_infrastructure()
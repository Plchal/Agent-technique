import uuid
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from snowflake.snowpark.types import VectorType, FloatType

import os
from dotenv import load_dotenv

load_dotenv()

def upload_data_with_snowpark(vector_data):
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA")
    }

    session = Session.builder.configs(connection_parameters).create()
    session.use_database(os.getenv("SNOWFLAKE_DATABASE"))
    session.use_schema(os.getenv("SNOWFLAKE_SCHEMA"))

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

        df.write.mode("append").save_as_table(os.getenv("SNOWFLAKE_TABLE_NAME"))

        print(f"[Snowpark] {len(vector_data)} chunks synchronisés !")

    except Exception as e:
        print(f"Error Snowpark : {e}")
        raise e
    finally:
        session.close()
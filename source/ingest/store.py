import uuid
from snowflake.snowpark.functions import col
from snowflake.snowpark.types import VectorType
from utils import get_snowpark_session, SNOWFLAKE_TABLE_NAME


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

        print(f"[Snowpark] {len(vector_data)} chunks synchronisés !")

    except Exception as e:
        print(f"Error Snowpark : {e}")
        raise e
    finally:
        session.close()
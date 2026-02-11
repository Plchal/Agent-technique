from store import get_snowpark_session
from snowflake.snowpark.functions import col, count
import os
from dotenv import load_dotenv
import json

load_dotenv()

def verify_data():
    session = get_snowpark_session()
    table_name = os.getenv("SNOWFLAKE_TABLE_NAME")

    try:
        print(f"--- Vérification de la table {table_name} ---")
        
        df = session.table(table_name)
        
        total_rows = df.count()
        print(f"📊 Nombre total de chunks en base : {total_rows}")
        
        if total_rows > 0:
            print("\n👀 Aperçu des données :")
            df.select("ID", "CONTENT").show(3)
            
            sample = df.select("EMBEDDING").limit(1).collect()
            vector_sample = sample[0][0]
            
            
            if isinstance(vector_sample, str):
                vector_sample = json.loads(vector_sample)
                
            print(f"Validation dimensionnelle : {len(vector_sample)} dimensions trouvées.")
        else:
            print("La table est vide. L'ingestion a peut-être échoué.")

    except Exception as e:
        print(f"Erreur lors de la vérification : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_data()
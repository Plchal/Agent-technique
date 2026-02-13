from store import get_snowpark_session
from snowflake.snowpark.functions import count

import json


def verify_data():
    session = get_snowpark_session()
    table_name = "DOCUMENT_CHUNKS"

    try:
        print(f"--- Vérification de la table  ---")
        
        df = session.table(table_name)
        
        total_rows = df.count()
        print(f"Nombre total de chunks en base : {total_rows}")
        
        if total_rows > 0:
            print("\nAperçu des données :")
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
import ollama
from utils import embedding, get_snowpark_session


def get_contexte_from_db(session, question_embedding, limit=5):
    vector_str = str(question_embedding)
    sql_query = f"""
        SELECT CONTENT, 
               VECTOR_COSINE_SIMILARITY(EMBEDDING, {vector_str}::VECTOR(FLOAT, 768)) as SIMILARITY
        FROM DOCUMENT_CHUNKS
        ORDER BY SIMILARITY DESC
        LIMIT {limit}
    """
    rows = session.sql(sql_query).collect()
    
    if not rows:
        return "Aucun contexte trouvé dans la base de données."
        
    return "\n---\n".join([r['CONTENT'] for r in rows])

def ask_doc(question: str):
    
    session = get_snowpark_session()
    try:
        question_vector_response = embedding(question)
        question_vector = question_vector_response['embedding']
        context = get_contexte_from_db(session, question_vector)

        prompt = f"""
        Tu es un expert mécanique Moto. Réponds UNIQUEMENT à partir du contexte fourni.
        Si l'information n'est pas dans le texte, dis que tu ne sais pas.

        CONTEXTE RÉCUPÉRÉ DE SNOWFLAKE:
        {context}

        QUESTION:
        {question}
        """

        response = ollama.chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
        return(response.message.content)

    except Exception as e:
        print(f"Error : {e}")
        return None
    finally:
        session.close()
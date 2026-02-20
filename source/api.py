import os
import uvicorn

from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils import UPLOAD_DIRECTORY, get_snowpark_session
from backend import ingester, rag_engine


app = FastAPI()


class QuestionRequest(BaseModel):
    question: str
    doc_id: str

app.mount("/dist", StaticFiles(directory="static/dist"), name="dist")


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.post("/ingest")
async def upload_file(file: UploadFile, brand: str = Form(...), model: str = Form(...), year: int = Form(...)):
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    with open(file_location, 'wb') as buffer:
        buffer.write(await file.read())
    
    try:
        ingester.ingest_pdf(file_location, brand, model, year)
        return {"message": f"{file.filename} saved at {file_location}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ingestion failure.")

@app.get("/models")
async def get_models():
    session = get_snowpark_session()
    try:
        rows= session.sql("""
            SELECT DOC_ID, BRAND || ' ' || MODEL || ' (' || YEAR || ')' as FULL_NAME
            FROM RAG_DB.RAG_SCHEMA.DOCUMENTS
            ORDER BY BRAND, MODEL
        """).collect()
        return[{"id": r['DOC_ID'], "name": r['FULL_NAME']} for r in rows]
    except Exception as e:
        return
    finally:
        session.close()

@app.post("/ask")
async def chat_with_your_doc(request: QuestionRequest):
    try:
        answer = rag_engine.ask_doc(request.question, request.doc_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Error with answer generation.")
        return {"question": request.question, "answer": answer["answer"], "sources": answer["sources"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error with RAG engine.")
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

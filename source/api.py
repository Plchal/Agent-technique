import os

from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel

from utils import UPLOAD_DIRECTORY
from backend import ingester, rag_engine

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ingest")
async def upload_file(file: UploadFile):
    print(UPLOAD_DIRECTORY)
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    with open(file_location, 'wb') as buffer:
        buffer.write(await file.read())
    
    try:
        ingester.ingest_pdf(file_location)
        return {"message": f"{file.filename} saved at {file_location}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Echec  de l'ingestion.")

@app.post("/ask")
async def chat_with_your_doc(request: QuestionRequest):
    answer = rag_engine.ask_doc(request.question)
    if not answer:
        raise HTTPException(status_code=500, detail="Error with answer generation !")
    return {"question": request.question, "answer": answer}
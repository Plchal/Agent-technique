import os
import uvicorn

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils import UPLOAD_DIRECTORY
from backend import ingester, rag_engine


app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


app.mount("/dist", StaticFiles(directory="static/dist"), name="dist")


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.post("/ingest")
async def upload_file(file: UploadFile):
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    with open(file_location, 'wb') as buffer:
        buffer.write(await file.read())
    
    try:
        ingester.ingest_pdf(file_location)
        return {"message": f"{file.filename} saved at {file_location}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ingestion failure.")


@app.post("/ask")
async def chat_with_your_doc(request: QuestionRequest):
    try:
        answer = rag_engine.ask_doc(request.question)
        if not answer:
            raise HTTPException(status_code=404, detail="Error with answer generation.")
        return {"question": request.question, "answer": answer["answer"], "sources": answer["sources"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error with RAG engine.")
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
        
            

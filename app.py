from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os
from PyPDF2 import PdfReader

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PDF_DIR = "./uploads"
parsed_text = ""

class AskRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global parsed_text
    file_path = os.path.join(PDF_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    parsed_text = text
    return {"filename": file.filename, "parsed_chars": len(parsed_text)}

@app.get("/filters")
def get_filters():
    return {
        "tags": ["CIA", "JFK", "Cuba", "Assassination"],
        "dates": ["1963", "1975", "2023"]
    }

@app.post("/ask")
def ask_question(payload: AskRequest):
    global parsed_text
    question = payload.question.lower()
    if not parsed_text:
        return {"answer": "No document uploaded or parsed yet."}

    matches = [line for line in parsed_text.splitlines() if question in line.lower()]
    if matches:
        return {"answer": f"Found match:
{matches[0]}"}
    return {"answer": "No relevant information found in the uploaded PDF."}
from fastapi import FastAPI, UploadFile, File, Form
from solidity_parser import parser
from summarizer import summarize_code
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/parse")
async def parse_solidity(file: UploadFile = File(...)):
    content = await file.read()
    source_code = content.decode("utf-8")
    ast = parser.parse(source_code)
    return json.loads(json.dumps(ast, indent=2))

@app.post("/summarize")
async def summarize_solidity(code: str = Form(...)):
    summary = summarize_code(code)
    return {"summary": summary}

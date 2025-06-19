from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import pandas as pd
from io import BytesIO
from db import SessionLocal, engine

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
]

REQUIRED_COLUMNS = ["GENERICNAME"]  # กำหนดคอลัมน์ที่ต้องมี

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    
    # checking file
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} is not allowed.")
    
    contents = await file.read()
    try:
        df = pd.read_excel(BytesIO(contents))  # pandas จะเลือกใช้ openpyxl หรือ xlrd ให้อัตโนมัติ
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"อ่านไฟล์ไม่สำเร็จ: {str(e)}")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise HTTPException(status_code=400, detail=f"ขาดคอลัมน์: {', '.join(missing)}")
    #end checkfile
    
    for _, row in df.iterrows():
        print(row["GENERICNAME"])
    
    
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return JSONResponse(content={
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully"
    })

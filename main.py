from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from models.Supplier import Supplier
import pandas as pd
from io import BytesIO
import os
from sqlalchemy import text
import logging

app = FastAPI()

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
]

REQUIRED_COLUMNS = ["GENERICNAME"]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        yield db
    finally:
        db.close()


@app.on_event("startup")
def check_database_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # สั่งเบาๆ เช็ก DB
        print("Conncted")
        logging.info("✅ Connected to the database successfully.")
    except Exception as e:
        logging.error("❌ Cannot connect to the database!")
        logging.error(str(e))
        raise RuntimeError("Database connection failed during startup.")
    
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # ✅ ตรวจสอบชนิดไฟล์
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} is not allowed.")

    # ✅ อ่านเนื้อหาไฟล์
    contents = await file.read()

    # ✅ ตรวจสอบว่าเป็น Excel และมีคอลัมน์ที่ต้องการ
    try:
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"อ่านไฟล์ไม่สำเร็จ: {str(e)}")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"ขาดคอลัมน์: {', '.join(missing)}")

    # ✅ วนใส่ข้อมูลลง DB
    try:
        for _, row in df.iterrows():
            generic = row.get("GENERICNAME")
            if pd.isna(generic):
                continue
            member = Supplier(GENERICNAME=str(generic))
            db.add(member)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    # ✅ บันทึกไฟล์ลงดิสก์ (หลังจากใช้ .read() แล้ว ต้องใช้ contents แทน file.file)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(contents)

    return JSONResponse(content={
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded and data imported successfully"
    })

import hashlib
from jose import JWTError, jwt
from pydantic import BaseModel
import json
from passlib.context import CryptContext
import os
from fastapi import APIRouter

SECRET_KEY = "a_very_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

class User(BaseModel):
    username: str
    password: str

@router.get("/{password}")
def get_users(password : str):
    hash = get_password_hash(password)
    print("MD5 Hash:", hash)
    return {"message": hash}

@router.post("/")
def login(user: User): 
    
    print("Current working directory:", os.getcwd())
    with open("users.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    for row in data:
        # print(row["username"], row["password"])
        
        if user.username==row["username"]:
            result = verify_password(user.password,row['password'])
            if result :
                print("Match")
                return {
                    "success" : True
                }


    return {
        "success" : False
    }

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ฟังก์ชันทดสอบ hashing password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

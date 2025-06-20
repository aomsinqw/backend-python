import hashlib

from fastapi import APIRouter

router = APIRouter()

@router.get("/{password}")
def get_users(password : str):
    hash_object = hashlib.md5(password.encode())  # ต้อง encode เป็น bytes ก่อน
    md5_hash = hash_object.hexdigest()

    print("MD5 Hash:", md5_hash)
    return {"message": md5_hash}


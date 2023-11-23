import jwt
from datetime import datetime, timedelta
from typing import Any
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import json
from bson import ObjectId
from dotenv import load_dotenv
import os
from app.db.database import db
load_dotenv()
oauth = OAuth2PasswordBearer(tokenUrl='api/v1/login/')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def verify_password(password, password_db) -> bool:
    return pwd_context.verify(password + os.getenv('SALT'), password_db)

def hash_password(password) -> Any:
    return pwd_context.hash(password + os.getenv('SALT'))

def encode_jwt_token(data : dict) -> str:
    payload = data.copy()
    payload.update({'exp' : datetime.utcnow() + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))})
    return jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

def decode_jwt_token(token : str = Depends(oauth)) -> dict:
    try:
        return jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token',
            headers={'WWW-Authenticate' : 'Bearer'}

        )
def get_id_by_token(payload : dict = Depends(decode_jwt_token)) -> str:
    return payload.get('sub')

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
    
async def authenticate_user(username : str, password : str) -> bool:
    user = await db.users.find_one({'username' : username})
    if user and verify_password(password, user['password']):
        return True
    return False
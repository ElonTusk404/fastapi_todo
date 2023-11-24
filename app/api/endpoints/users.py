from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.models.user import UserCreate, User, UserResponse
from app.core.security import verify_password, hash_password, encode_jwt_token, decode_jwt_token, MongoJSONEncoder, get_id_by_token, authenticate_user
from app.db.database import db
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
router = APIRouter()

@router.post('/register/', response_model=UserResponse)
async def register(user: UserCreate):
    user = User(username=user.username, email=user.email, password=hash_password(user.password))
    user = jsonable_encoder(user)
    new_user = await db.users.insert_one(user)
    created_user = await db.users.find_one({'_id' : new_user.inserted_id}, projection = {'password' : False})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=MongoJSONEncoder().encode(created_user))
@router.post('/login/')
async def login(user_in : OAuth2PasswordRequestForm = Depends()):
    if await authenticate_user(user_in.username, user_in.password):
        return JSONResponse(status_code=status.HTTP_200_OK, content={'access_token' : encode_jwt_token({'sub' : user_in.username}), 'token_type' : 'Bearer'})
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid creditionals', headers={'WWW-Authenticate' : 'Bearer'})
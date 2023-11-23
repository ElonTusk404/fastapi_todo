from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username : str
    email : EmailStr
    password : str
class User(BaseModel):
    username : str
    email: str
    password : str
class UserResponse(BaseModel):
    username : str
    email: str
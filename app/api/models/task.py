from pydantic import BaseModel

class TaskCreate(BaseModel):
    title : str
    description : str

class Task(BaseModel):
    title : str
    description : str
    completed : bool
    owner : str 

class TaskResponse(BaseModel):
    _id : str
    title : str
    description : str
    completed : bool
    owner : str

class TaskUpdate(BaseModel):
    title : str
    description : str
    completed : bool
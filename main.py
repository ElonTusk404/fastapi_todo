from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.api.endpoints import users, tasks
from app.core.security import get_id_by_token
from app.api.middleware.middleware import logging_middleware, logger

app = FastAPI()

app.include_router(users.router, prefix='/api/v1', tags=['Users'])
app.include_router(tasks.router, prefix='/api/v1', tags=['Tasks'], dependencies=[Depends(get_id_by_token)])
app.middleware("http")(logging_middleware)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-Time Task Manager API"}
#############################

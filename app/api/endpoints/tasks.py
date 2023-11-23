from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse, Response
from app.api.models.task import Task, TaskCreate, TaskResponse, TaskUpdate
from app.core.security import get_id_by_token, MongoJSONEncoder
from app.db.database import db
from typing import Set, List
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

router = APIRouter()
active_connections : Set[WebSocket] = set()

@router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(client_id: int, websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for connection in active_connections:
                await connection.send_text(f"Client with {client_id} wrote {message}!")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.post('/tasks/', description='Create Task', response_model=TaskResponse)
async def create_task(task: TaskCreate, username : str = Depends(get_id_by_token)):
    task = Task(title=task.title, description=task.description, completed=False, owner=username)
    task = jsonable_encoder(task)
    result = await db.tasks.insert_one(task)
    added_task =  await db.tasks.find_one({'_id' : result.inserted_id})
    for connection in active_connections:
        connection.send_text(f'New task {task.title} created by {username}')
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=MongoJSONEncoder().encode(added_task))

@router.get('/tasks/{task_id}', response_model=TaskResponse)
async def get_task(task_id : str, username: str = Depends(get_id_by_token)):
    if (task := await db.tasks.find_one({'_id' : ObjectId(task_id)})) is not None:
        if task['owner'] == username:
            return JSONResponse(status_code=status.HTTP_200_OK, content=MongoJSONEncoder().encode(task))
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task {task_id} not found')

@router.put('/tasks/{task_id}', response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate, username: str = Depends(get_id_by_token)):
    if (old_task := await db.tasks.find_one({'_id': ObjectId(task_id)})) is not None:
        if old_task['owner'] == username:
            updated_task = Task(
                title=task.title,
                description=task.description,
                completed=task.completed,
                owner=username
            )
            updated_task = jsonable_encoder(updated_task)
            
            update_result = await db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': updated_task})
            
            if update_result.modified_count > 0:
                if (new_task := await db.tasks.find_one({'_id': ObjectId(task_id)})) is not None:
                    for connection in active_connections:
                        await connection.send_text(f'Task {task_id} updated by {username}')
                    
                    return JSONResponse(status_code=status.HTTP_200_OK, content=MongoJSONEncoder().encode(new_task))

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permissions")

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task {task_id} not found')

@router.delete('/tasks/{task_id}')
async def delete_task(task_id : str, username : str = Depends(get_id_by_token)):
    if (task:= await db.tasks.find_one({'_id' : ObjectId(task_id)})) is not None:
        if task['owner'] == username:
            delete_result = await db.tasks.delete_one({'_id' : ObjectId(task_id)})
            if delete_result.deleted_count == 1:
                for connection in active_connections:
                    await connection.send_text(f'Task {task_id} deleted by {username}')
                return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task {task_id} not found')




from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from typing import Annotated

from src.db.user_controller import User, UserController
from src.db import userController
from src import auth

from pydantic import BaseModel

app = FastAPI()

class Error(BaseModel):
    error: str

@app.post('/register')
async def register(user: User):
    return auth.register_user(user)

@app.post('/login')
async def login(user: User):
    return await auth.login_user(user)

@app.get('/me', response_model=User | Error)
async def get_user(current_user: Annotated[User, Depends(auth.get_current_user)]):
    if 'error' in current_user.model_fields.keys():
        return current_user
    try:
        controller = UserController('duradora.db')
        user = controller.find_user(current_user.username)
        if user is None:
            return {'error': 'No such user'}
        return user
    except Exception as e:
        return {'error': str(e)}

@app.post('/user/update')
async def update_user(user: User):
    try:
        controller = UserController('duradora.db')
        controller.update_user(user)
    except Exception as e:
        return {'error': str(e)}
    return {'success': True}

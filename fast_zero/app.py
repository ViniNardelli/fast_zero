from http import HTTPStatus
from typing import NoReturn

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root() -> dict[str, str]:
    return {'message': 'Hello World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema) -> UserDB:
    user_with_id = UserDB(id=len(database) + 1, **user.model_dump())
    database.append(user_with_id)
    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users() -> dict[str, list[UserDB]]:
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int) -> UserPublic | NoReturn:
    if not (0 < user_id <= len(database)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema) -> UserDB | NoReturn:
    if not (0 < user_id <= len(database)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    database[user_id - 1] = (
        user_with_id := UserDB(id=user_id, **user.model_dump())
    )
    return user_with_id


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(user_id: int) -> UserPublic | NoReturn:
    if not (0 < user_id <= len(database)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database.pop(user_id - 1)


@app.get('/oi', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    return """
    <!doctype html>
        <head>
            <title>Saudações</title>
        </head>
        <body>
            <h1>OLÁ MUNDO!!!</h1>
        </body>
    </html>"""

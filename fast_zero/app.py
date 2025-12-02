from http import HTTPStatus
from typing import Sequence

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root() -> dict[str, str]:
    return {'message': 'Hello World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)) -> User:
    db_user = session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    if db_user:
        if db_user.username == user.username or db_user.email == user.email:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)) -> dict[str, Sequence[User]]:
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    return user_db


@app.put('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if user_db:
        user_db.email = str(user.email)
        user_db.username = user.username
        user_db.password = user.password

        try:
            session.add(user_db)
            session.commit()
            session.refresh(user_db)
        except IntegrityError:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')

        return user_db
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if user_db:
        session.delete(user_db)
        session.commit()

        return {'message': 'User deleted successfully'}
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


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

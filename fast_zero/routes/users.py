from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import FilterPage, Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session) -> User:
    db_user = await session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    if db_user:
        if db_user.username == user.username or db_user.email == user.email:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')

    db_user = User(**user.model_dump())
    db_user.password = get_password_hash(user.password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(session: T_Session,
               current_user: T_CurrentUser,
               filter_users: T_FilterPage) -> dict[str, Sequence[User]]:
    users = await session.scalars(select(User).offset(filter_users.offset).limit(filter_users.limit))
    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def read_user(user_id: int, session: T_Session) -> User:
    user_db = await session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    return user_db


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(user_id: int, user: UserSchema, session: T_Session, current_user: T_CurrentUser) -> User:
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    try:
        current_user.email = str(user.email)
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(user_id: int, session: T_Session, current_user: T_CurrentUser) -> dict[str, str]:
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted successfully'}

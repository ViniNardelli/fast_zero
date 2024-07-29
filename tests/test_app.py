from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.models import User
from fast_zero.schemas import UserPublic


# region read_root
def test_root_deve_retornar_ok_e_ola_mundo(client: TestClient) -> None:
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


# endregion


# region read_users
def test_read_users_empty(client: TestClient) -> None:
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_not_empty(client: TestClient, user: User) -> None:
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# endregion


# region crete_user
def test_create_user(client: TestClient) -> None:
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_bad_username(client: TestClient) -> None:
    client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@wonderland.com',
            'password': 'secret',
        },
    )

    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@borderland.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_user_bad_email(client: TestClient) -> None:
    client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    response = client.post(
        '/users',
        json={
            'username': 'caterpillar',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


# endregion


# region read_user
def test_read_user(client: TestClient, user: User) -> None:
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


# endregion


# region update_user
def test_update_user(client: TestClient, user: User, token: str) -> None:
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'my_new_password',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


def test_update_invalid_user(
    client: TestClient, user: User, token: str
) -> None:
    response = client.put(
        f'/users/{user.id - 1}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'my_new_password',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


# endregion


# region delete_user
def test_delete_user(client: TestClient, user: User, token: str) -> None:
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_invalid_user(
    client: TestClient, user: User, token: str
) -> None:
    response = client.delete(
        f'/users/{user.id - 1}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


# endregion


# region token
def test_get_token(client: TestClient, user) -> None:
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert token['access_token']


# endregion

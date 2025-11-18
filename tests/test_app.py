from http import HTTPStatus
from typing import NoReturn


def test_root_deve_retornar_ok_e_ola_mundo(client) -> None | NoReturn:
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_ola_mundo_retornar_ok(client) -> None | NoReturn:
    response = client.get('/oi')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>OLÁ MUNDO!!!</h1>' in response.text


def test_create_user(client) -> None | NoReturn:
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
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_users(client) -> None | NoReturn:
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'id': 1, 'username': 'alice', 'email': 'alice@example.com'}]
    }


def test_read_user(client) -> None | NoReturn:
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_fail_read_user(client) -> None:
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client) -> None | NoReturn:
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secrets',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_fail_update_user(client) -> None | NoReturn:
    response = client.put(
        '/users/0',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secrets',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client) -> None | NoReturn:
    responde = client.delete('/users/1')

    assert responde.status_code == HTTPStatus.OK
    assert responde.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_fail_delete_user(client) -> None | NoReturn:
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

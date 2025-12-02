from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client) -> None:
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_ola_mundo_retornar_ok(client) -> None:
    response = client.get('/oi')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>OLÁ MUNDO!!!</h1>' in response.text


def test_create_user(client) -> None:
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


def test_create_user_duplicated_username(client, user) -> None:
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_create_user_duplicated_email(client, user) -> None:
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_read_users(client) -> None:
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user) -> None:
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user) -> None:
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_fail_read_user(client) -> None:
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user) -> None:
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secrets',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'username': 'bob', 'email': 'bob@example.com'}


def test_fail_update_user(client) -> None:
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


def test_delete_user(client, user) -> None:
    responde = client.delete('/users/1')

    assert responde.status_code == HTTPStatus.OK
    assert responde.json() == {'message': 'User deleted successfully'}


def test_fail_delete_user(client) -> None:
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_integrity_error(client, user) -> None:
    # Inserindo Fausto
    client.post('/users', json={'username': 'fausto', 'email': 'fausto@example.com', 'password': 'secret'})

    # Alterando o username do user da fixture para fausto
    response = client.put(
        f'/users/{user.id}', json={'username': 'fausto', 'email': 'teste@test.com', 'password': 'testtest'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}

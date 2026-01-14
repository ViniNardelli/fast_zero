from http import HTTPStatus

from fast_zero.schemas import UserPublic


# region users
def test_create_user(client) -> None:
    response = client.post('/users',
                           json={'username': 'alice',
                                 'email': 'alice@example.com',
                                 'password': 'secret'})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1,
                               'username': 'alice',
                               'email': 'alice@example.com'}


def test_create_user_duplicated_username(client, user) -> None:
    response = client.post('/users',
                           json={'username': user.username,
                                 'email': 'alice@example.com',
                                 'password': 'secret'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_create_user_duplicated_email(client, user) -> None:
    response = client.post('/users',
                           json={'username': 'alice',
                                 'email': user.email,
                                 'password': 'secret'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_read_users(client, user, token) -> None:
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
# endregion


# region users/id
def test_read_user(client, user) -> None:
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': user.id,
                               'username': user.username,
                               'email': user.email}


def test_fail_read_user(client) -> None:
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user, token) -> None:
    response = client.put(f'/users/{user.id}',
                          json={'username': 'bob',
                                'email': 'bob@example.com',
                                'password': 'secrets'},
                          headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': user.id, 'username': 'bob', 'email': 'bob@example.com'}


def test_update_user_duplicated_name(client, user, other_user, token) -> None:
    response = client.put(f'/users/{user.id}',
                          json={'username': other_user.username,
                                'email': user.email,
                                'password': user.password},
                          headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_user_duplicated_email(client, user, other_user, token) -> None:
    response = client.put(f'/users/{user.id}',
                          json={'username': user.username,
                                'email': other_user.email,
                                'password': user.password},
                          headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_user_with_wrong_user(client, other_user, token) -> None:
    response = client.put(f'/users/{other_user.id}',
                          json={'username': 'Alice',
                                'email': 'alice@example.com',
                                'password': 'secrets'},
                          headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token) -> None:
    responde = client.delete(f'/users/{user.id}',
                             headers={'Authorization': f'Bearer {token}'})

    assert responde.status_code == HTTPStatus.OK
    assert responde.json() == {'message': 'User deleted successfully'}


def test_fail_delete_user_wrong_user(client, other_user, token) -> None:
    response = client.delete(f'/users/{other_user.id}',
                             headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
# endregion

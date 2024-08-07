from http import HTTPStatus

from freezegun import freeze_time
from starlette.testclient import TestClient


def test_get_token(client: TestClient, user) -> None:
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token_type = response.json()['token_type']
    access_token = response.json()['access_token']

    assert response.status_code == HTTPStatus.OK
    assert token_type == 'Bearer'
    assert access_token


def test_token_expired_after_time(client: TestClient, user) -> None:
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        to_expire_token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {to_expire_token}'},
            json={
                'username': 'wrong wrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client: TestClient, user) -> None:
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_nonexistent_user(client, user) -> None:
    response = client.post(
        '/auth/token',
        data={'username': 'wrong@email.com',
              'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client: TestClient, user, token) -> None:
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'

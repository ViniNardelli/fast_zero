from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time

from fast_zero.settings import Settings


def test_get_token(client, user) -> None:
    response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
    access_token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert access_token['token_type'] == 'Bearer'
    assert 'access_token' in access_token


def test_incorrect_email(client) -> None:
    response = client.post('/auth/token', data={'username': 'test@example.com', 'password': 'secret'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_incorrect_password(client, user) -> None:
    response = client.post('/auth/token', data={'username': user.email, 'password': 'wrong_secret'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_expired_after_time(client, user) -> None:
    start_time = datetime.strptime('2000-01-01 12:01:00', '%Y-%m-%d %H:%M:%S')

    with freeze_time(start_time):
        response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time(start_time + timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES)):
        response = client.put(f'/users/{user.id}',
                              headers={'Authorization': f'Bearer {token}'},
                              json={'username': 'wrongwrong', 'email': 'wrong@wrong.com', 'password': 'wrong'})

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, user, token) -> None:
    response = client.post('/auth/refresh_token',
                           headers={'Authorization': f'Bearer {token}'})

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client, user) -> None:
    start_time = datetime.strptime('2000-01-01 12:01:00', '%Y-%m-%d %H:%M:%S')

    with freeze_time(start_time):
        response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time(start_time + timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES)):
        response = client.post('/auth/refresh_token',
                               headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}

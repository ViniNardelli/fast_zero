from http import HTTPStatus


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

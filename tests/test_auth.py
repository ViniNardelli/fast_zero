from http import HTTPStatus

from starlette.testclient import TestClient


def test_get_token(client: TestClient, user) -> None:
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert token['access_token']

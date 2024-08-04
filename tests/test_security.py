from http import HTTPStatus

from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient
from jwt import decode
from pytest import raises

from fast_zero.security import create_access_token, settings, get_current_user


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(token, settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM])

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client: TestClient):
    response = client.delete(
        'users/1', headers={'Authorization': 'Bearer invalidToken'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_deve_dar_erro_de_jwt():
    with raises(HTTPException):
        get_current_user()

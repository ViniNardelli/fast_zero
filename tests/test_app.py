from http import HTTPStatus
from typing import NoReturn

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo() -> None | NoReturn:
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_ola_mundo_retornar_ok() -> None | NoReturn:
    client = TestClient(app)
    response = client.get('/oi')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>OLÁ MUNDO!!!</h1>' in response.text

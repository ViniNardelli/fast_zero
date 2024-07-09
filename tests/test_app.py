from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_ex2_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)

    response = client.get('/ex2')
    title = response.text.split(' </h1>')[0].split('<h1')[1].split('> ')[1]

    assert response.status_code == HTTPStatus.OK
    assert title == 'Olá Mundo'

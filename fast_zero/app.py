from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.get('/oi', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    return """
    <!doctype html>
        <head>
            <title>Saudações</title>
        </head>
        <body>
            <h1>OLÁ MUNDO!!!</h1>
        </body>
    </html>"""

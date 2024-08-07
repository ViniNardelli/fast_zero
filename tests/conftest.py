import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n:02}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest.fixture
def client(session: Session) -> TestClient:
    def get_test_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_test_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session: Session):
    password = 'secret'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def other_user(session: Session):
    password = 'secret'
    other_user = UserFactory(password=get_password_hash(password))

    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_user.clean_password = password

    return other_user


@pytest.fixture
def token(client: TestClient, user) -> str:
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']

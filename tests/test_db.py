from fast_zero.models import User

from sqlalchemy import select


def test_create_user(session):
    user = User(username='alice', email='alice@example.com', password='secret')
    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'alice@example.com')
    )

    assert result.username == 'alice'
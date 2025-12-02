from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='test', email='test@test.com', password='secret')

        session.add(new_user)
        session.commit()

        user_saved = session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user_saved) == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }

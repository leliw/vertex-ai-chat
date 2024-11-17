import pytest

from app.user import UserService, User


@pytest.fixture
def user_service(factory):
    return UserService(factory)


def test_put_get_and_delete_user(user_service):
    # Given: A new user
    email = "jasio@wp.pl"
    user = User(email=email, password="test", name="Jasio")
    # When: The user is put into the storage
    user_service.put(email, user)
    # Then: The user can be retrieved from the storage
    assert user_service.get(email) == user
    # When: The user is deleted from the storage
    user_service.delete(email)
    # Then: The user cannot be retrieved from the storage
    assert user_service.get(email) is None

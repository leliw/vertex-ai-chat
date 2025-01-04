import pytest

from ampf.base import KeyNotExistsException

from app.user import UserService, User


@pytest.fixture
def user_service(factory):
    service = UserService(factory)
    yield service
    # Clean up
    service.storage_new.drop()


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
    with pytest.raises(KeyNotExistsException):
        user_service.get(email)


def test_upgrade_not_exists(user_service):
    # Given: A user in the old storage
    email = "jasio@wp.pl"
    user = User(email=email, password="test", name="Jasio")
    user_service.storage_old.put(email, user)
    # When: The upgrade is run
    user_service.upgrade()
    # Then: The user is in the new storage
    assert user_service.storage_new.get(email) == user
    # And: Old storage is empty
    assert user_service.storage_old.is_empty()


def test_upgrade_exists(user_service):
    # Given: A user in both storages
    email = "jasio@wp.pl"
    user_o = User(email=email, password="test", name="Jasio")
    user_service.storage_old.put(email, user_o)
    user_n = User(email=email, password="test", name="Jan")
    user_service.storage_new.put(email, user_n)
    # When: The upgrade is run
    user_service.upgrade()
    # Then: The user in the new storage is not changed
    assert user_service.storage_new.get(email) == user_n
    # And: Old storage is empty
    assert user_service.storage_old.is_empty()

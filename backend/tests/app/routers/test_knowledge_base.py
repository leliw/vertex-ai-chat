from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ampf.auth import Tokens

from app.dependencies import get_factory, get_server_config
from app.knowledge_base.knowledge_base_model import KnowledgeBaseItem
from app.routers import auth, knowledge_base
from app.user.user_service import UserService


@pytest.fixture
def client(factory, test_config):
    app = FastAPI()
    app.dependency_overrides[get_factory] = lambda: factory
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.include_router(prefix="/api", router=auth.router)
    UserService(factory).initialize_storage_with_user(test_config.default_user)
    app.include_router(prefix="/api/knowledge-base", router=knowledge_base.router)
    client = TestClient(app)
    yield client
    # Clean up
    knowledge_base.get_knowledge_base_service(None, test_config).storage.drop()


@pytest.fixture
def access_token(client):
    response = client.post(
        "/api/login",
        data={"username": "test@test.com", "password": "test"},
    )
    assert response.status_code == 200
    r = Tokens(**response.json())
    return r.access_token


def test_get_empty_list(client, access_token):
    # Given: A new empty knowledge base
    # When: A GET request is made to /api/knowledge-base
    response = client.get(
        "/api/knowledge-base", headers={"Authorization": f"Bearer {access_token}"}
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response is an empty list
    assert 0 == len(r)


def test_post_get_delete(client, access_token):
    # Step 1
    # Given: A knowledge base item
    kbi = KnowledgeBaseItem(
        item_id="", title="Test title", content="Test content", keywords=["test"]
    )
    # When: Post the item
    response = client.post(
        "/api/knowledge-base",
        headers={"Authorization": f"Bearer {access_token}"},
        json=kbi.model_dump(),
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: Id is returned
    item_id = r["item_id"]
    # Step 2
    # When: Get the item
    response = client.get(
        f"/api/knowledge-base/{item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The item is returned
    assert r["title"] == kbi.title
    assert r["content"] == kbi.content
    # Step 3
    # When: Delete the item
    response = client.delete(
        f"/api/knowledge-base/{item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Then: The response status code is 200
    assert 200 == response.status_code


def test_post_put_get_all(client, access_token):
    # Step 1
    # Given: A knowledge base item
    kbi = KnowledgeBaseItem(
        title="Test title", content="Test content", keywords=["test"]
    )
    # When: Post the item
    response = client.post(
        "/api/knowledge-base",
        headers={"Authorization": f"Bearer {access_token}"},
        json=kbi.model_dump(),
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: Id is returned
    item_id = r["item_id"]
    # Step 2
    # Given: Updated knowledge base item
    kbi.title = "Updated title"
    kbi.content = "Updated content"
    # When: Put the item
    response = client.put(
        f"/api/knowledge-base/{item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=kbi.model_dump(),
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The item is updated
    assert r["title"] == kbi.title
    assert r["content"] == kbi.content
    # Step 3
    # When: Get all items
    response = client.get(
        "/api/knowledge-base", headers={"Authorization": f"Bearer {access_token}"}
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The item is returned
    assert len(r) == 1
    assert r[0]["title"] == kbi.title


def test_find_nearest(client, access_token):
    # Given: Some knowledge base items
    kbi1 = KnowledgeBaseItem(
        title="Test title 1", content="Test content 1", keywords=["test", "one"]
    )
    kbi2 = KnowledgeBaseItem(
        title="Test title 2", content="Test content 2", keywords=["test", "two"]
    )
    client.post(
        "/api/knowledge-base",
        headers={"Authorization": f"Bearer {access_token}"},
        json=kbi1.model_dump(),
    )
    client.post(
        "/api/knowledge-base",
        headers={"Authorization": f"Bearer {access_token}"},
        json=kbi2.model_dump(),
    )
    # When: Find nearest items
    response = client.post(
        "/api/knowledge-base/find-nearest",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"text": "test", "keywords": ["test"]},
    )
    r = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: Two items are returned
    assert len(r) == 2
    titles = [item["title"] for item in r]
    # And: First item is returned
    assert kbi1.title in titles
    # And: Second item is returned
    assert kbi2.title in titles

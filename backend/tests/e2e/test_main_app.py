import os
from typing import Iterator
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def static_client(client: TestClient) -> Iterator[TestClient]:
    os.makedirs("static/browser", exist_ok=True)
    with open("static/browser/index.html", "wt", encoding="utf-8") as f:
        f.write("Hello from index.html")
    with open("static/browser/app.css", "wt", encoding="utf-8") as f:
        f.write("Hello from app.css")
    yield client
    os.remove("static/browser/index.html")
    os.remove("static/browser/app.css")


def test_get_index_html(static_client):
    # When: Browser require existing file
    response = static_client.get("/index.html")
    # Then: index.html is returned
    assert "text/html" in response.headers["content-type"]
    assert "Hello from index.html" in response.text


def test_get_main_page(static_client):
    # When: Browser require main page
    response = static_client.get("/")
    # Then: index.html is returned
    assert "text/html" in response.headers["content-type"]
    assert "Hello from index.html" in response.text


def test_get_angular_routing(static_client):
    # When: Browser require page which not exists
    response = static_client.get("/chat")
    # Then: index.html is returned
    assert "text/html" in response.headers["content-type"]
    assert "Hello from index.html" in response.text


def test_get_css(static_client):
    # When: Browser require existing file
    response = static_client.get("/app.css")
    # Then: index.html is returned
    assert "text/css" in response.headers["content-type"]
    assert "Hello from app.css" in response.text


def test_get_not_existing_api(static_client):
    # When: Browser require not existing api
    response = static_client.get("/api/blablabla_not_exists", status_code=404)
    # Then: 404 page is returned
    print(response)
    assert "Not found" in response["detail"]


def test_get_not_existing_file_without_index(client):
    # When: Browser require not existing file
    response = client.get("/blablabla_not_exists", status_code=404)
    # Then: 404 page is returned
    print(response)
    assert "Page not found" in response["detail"]

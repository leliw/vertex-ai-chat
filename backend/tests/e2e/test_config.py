import re


def test_get_client_config(client):
    response = client.get("/api/config")
    r = response.json()

    assert 200 == response.status_code
    assert 2 == len(r)
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, r["version"])
    assert "google_oauth_client_id" in r

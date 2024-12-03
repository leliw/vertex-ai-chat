def test_send_message(client):
    r = client.get("/api/chats/_NEW_")
    chat_session_id = r["chat_session_id"]
    # When: Sending a message
    r = client.post(
        f"/api/chats/{chat_session_id}/messages",
        json={"author": "user", "content": "Hello, world!"},
    )
    assert 0 < len(r)

    r = client.get(f"/api/chats/{chat_session_id}")
    # And: The response contains a chat session
    assert "chat_session_id" in r
    assert chat_session_id == r["chat_session_id"]
    assert 2 == len(r["history"])

    r = client.get("/api/chats")
    # And: The response contains a chat session
    assert 1 == len(r)
    assert chat_session_id == r[0]["chat_session_id"]

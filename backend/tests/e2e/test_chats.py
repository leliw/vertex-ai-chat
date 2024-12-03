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

def get_answer(r: dict):
    """Extract the answer from the streaming response"""
    answer = ""
    for i in r:
        answer += i["value"]
    return answer

def test_send_message_with_file(client):
    # Given: A chat session
    r = client.get("/api/chats/_NEW_")
    chat_session_id = r["chat_session_id"]
    # And: The file is uploaded
    client.post(
        "/api/files",
        files=[
            ("files", ("test4.txt", b"File content 4", "text/plain")),
        ],
    )
    # When: Sending a message
    r = client.post(
        f"/api/chats/{chat_session_id}/messages",
        json={
            "author": "user",
            "content": "What is the content of the document?",
        },
    )
    # Then: The response contains right answer
    assert "File content 4" in get_answer(r)

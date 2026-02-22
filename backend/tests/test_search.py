def test_search_requires_query(client):
    res = client.post("/api/search", json={})
    assert res.status_code == 422


def test_search_checks_quota(client, db_session):
    from app.models.search_usage import SearchUsage

    # Exhaust free searches
    for _ in range(3):
        db_session.add(SearchUsage(session_id="test-session"))
    db_session.commit()

    res = client.post(
        "/api/search",
        json={"query": "test product in test city"},
        cookies={"session_id": "test-session"},
    )
    assert res.status_code == 402
    assert "quota" in res.json()["detail"].lower() or "limit" in res.json()["detail"].lower()

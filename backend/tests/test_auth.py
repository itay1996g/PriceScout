def test_register_creates_user(client):
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email_fails(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "otherpass",
    })
    assert res.status_code == 400


def test_login_returns_token(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_me_returns_user_info(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    login_res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    token = login_res.json()["token"]

    res = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"
    assert "searches_remaining" in res.json()


def test_me_without_token_fails(client):
    res = client.get("/api/auth/me")
    assert res.status_code in (401, 403)

def test_create_checkout_requires_auth(client):
    res = client.post("/api/billing/create-checkout")
    assert res.status_code in (401, 403)


def test_create_checkout_with_auth(client):
    # Register and login
    client.post("/api/auth/register", json={
        "email": "buyer@test.com",
        "password": "pass123",
    })
    login_res = client.post("/api/auth/login", json={
        "email": "buyer@test.com",
        "password": "pass123",
    })
    token = login_res.json()["token"]

    # Mock stripe to avoid real API calls
    from unittest.mock import patch, MagicMock

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"

    with patch("stripe.checkout.Session.create", return_value=mock_session):
        res = client.post(
            "/api/billing/create-checkout",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert res.status_code == 200
    assert "url" in res.json()

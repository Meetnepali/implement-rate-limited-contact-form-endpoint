import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PROFILE_PATH = "/profiles/"

def create_profile(name="Alice", email="alice@example.com", bio="A person."):
    return client.post(
        PROFILE_PATH,
        json={"name": name, "email": email, "bio": bio}
    )

def test_create_profile_success():
    resp = create_profile()
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["name"] == "Alice"
    assert data["bio"] == "A person."
    assert data["email"] == "alice@example.com"

def test_create_profile_duplicate_email():
    create_profile(email="bob@example.com")
    r = create_profile(email="bob@example.com")
    assert r.status_code == 400
    assert "Email address must be unique" in r.json()["detail"]

def test_create_profile_bio_too_long():
    bio = "x" * 201
    r = create_profile(bio=bio)
    assert r.status_code == 422 or r.status_code == 400
    # Depending on which error layer triggers first


def test_get_profile_success():
    res = create_profile(name="Charles", email="charles@example.com")
    pid = res.json()["id"]
    r = client.get(f"{PROFILE_PATH}{pid}")
    assert r.status_code == 200
    d = r.json()
    assert d["name"] == "Charles"

def test_get_profile_not_found():
    r = client.get(f"{PROFILE_PATH}1029382")
    assert r.status_code == 404
    assert "Profile not found" in r.json()["detail"]

def test_patch_profile_success():
    res = create_profile(name="Dan", email="dan@example.com")
    pid = res.json()["id"]
    new_data = {"bio": "Updated bio."}
    r = client.patch(f"{PROFILE_PATH}{pid}", json=new_data)
    assert r.status_code == 200
    j = r.json()
    assert j["bio"] == "Updated bio."
    assert j["email"] == "dan@example.com"

def test_patch_profile_duplicate_email():
    res1 = create_profile(name="Eve", email="eve1@example.com")
    res2 = create_profile(name="Eve2", email="eve2@example.com")
    pid2 = res2.json()["id"]
    # Try to update Eve2 to Eve1's email
    r = client.patch(f"{PROFILE_PATH}{pid2}", json={"email": "eve1@example.com"})
    assert r.status_code == 400
    assert "Email address must be unique" in r.json()["detail"]

def test_patch_profile_bio_too_long():
    res = create_profile(name="Fay", email="fay@example.com")
    pid = res.json()["id"]
    long_bio = "x" * 201
    r = client.patch(f"{PROFILE_PATH}{pid}", json={"bio": long_bio})
    assert r.status_code == 422 or r.status_code == 400
    # Could fail in request validation or at endpoint level, system should not crash

def test_patch_profile_not_found():
    r = client.patch(f"{PROFILE_PATH}9977", json={"bio": "No user."})
    assert r.status_code == 404
    assert "Profile not found" in r.json()["detail"]

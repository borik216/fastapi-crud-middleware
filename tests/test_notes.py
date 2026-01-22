import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.api.deps.db import get_db
from app.main import app
import os
import time
from datetime import datetime

# 1. Setup a dedicated Test Database (In-Memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. This fixture runs before every test
@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine) # Create tables
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine) # Clean up after

# 3. Override the app's dependency to use the test DB
@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

# client = TestClient(app)

EXPECTED_API_KEY = os.getenv("API_ACCESS_TOKEN", "default-secret-change-me")
HEADERS = {"access_token": EXPECTED_API_KEY }

def test_health_check(client):
    """Test that health check is working properly and returning 200"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
def test_read_notes_unauthorized(client):
    """Test that we get a 403 if the API key is missing"""
    response = client.get("/api/v1/notes")
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized: Invalid API Key"
    
def test_read_notes_authorized(client):
    """Test that we get a list object back when authorized"""
    response = client.get("/api/v1/notes", headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_create_note(client):
    # 1. Create the note
    new_note = {"title": "Test Secret", "tags": "test", "created_by": "tester"}
    create_resp = client.post("/api/v1/notes", json=new_note, headers=HEADERS)
    assert create_resp.status_code == 200
    note_id = create_resp.json()["id"]
    
    # 2. Make sure note exists in DB
    created_note = client.get(f"/api/v1/notes/{note_id}", headers=HEADERS)
    assert created_note.json()["title"] == "Test Secret"
    assert created_note.json()["tags"] == "test"
    assert created_note.json()["created_by"] == "tester"
    
def test_update_note_timestamp(client):
    # 1. Create the note
    new_note = {"title": "Original Title", "tags": "test", "created_by": "tester"}
    create_resp = client.post("/api/v1/notes", json=new_note, headers=HEADERS)
    note_id = create_resp.json()["id"]
    initial_access_time = create_resp.json()["last_accessed_at"]

    # 2. Wait a split second to ensure the clock moves
    time.sleep(1)

    # 3. Update the note
    update_data = {"title": "Updated Title", "tags": "test", "created_by": "tester"}
    update_resp = client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=HEADERS)
    assert update_resp.status_code == 200
    
    # 4. Assert the timestamp updated
    updated_access_time = update_resp.json()["last_accessed_at"]
    assert updated_access_time > initial_access_time
    assert update_resp.json()["title"] == "Updated Title"    

def test_create_and_soft_delete(client):
    # 1. Create a note
    new_note = {"title": "Test Secret", "tags": "test", "created_by": "tester"}
    create_resp = client.post("/api/v1/notes", json=new_note, headers=HEADERS)
    assert create_resp.status_code == 200
    note_id = create_resp.json()["id"]

    # 2. Verify it's in the list
    list_resp = client.get("/api/v1/notes", headers=HEADERS)
    assert len(list_resp.json()) == 1

    # 3. Soft Delete it
    del_resp = client.delete(f"/api/v1/notes/{note_id}", headers=HEADERS)
    assert del_resp.status_code == 200

    # 4. Verify it's GONE from the active list (Soft Delete check)
    list_after_del = client.get("/api/v1/notes", headers=HEADERS)
    assert len(list_after_del.json()) == 0
    
def test_create_and_purge(client):
    # 1. Create a note
    new_note = {"title": "Test Secret", "tags": "test", "created_by": "tester"}
    create_resp = client.post("/api/v1/notes", json=new_note, headers=HEADERS)
    assert create_resp.status_code == 200
    note_id = create_resp.json()["id"]
    
    # 2. Verify it's in the list
    list_resp = client.get("/api/v1/notes", headers=HEADERS)
    assert len(list_resp.json()) == 1
    
    # 3. Soft Delete it
    del_resp = client.delete(f"/api/v1/notes/{note_id}", headers=HEADERS)
    assert del_resp.status_code == 200
    
    # 4. Make sure it is deleted (deleted_at not null)
    soft_deleted_note = client.get(f"/api/v1/notes/{note_id}", headers=HEADERS)
    assert soft_deleted_note.json()["deleted_at"] is not None
    
    # 5. Purge note
    purge_resp = client.delete(f"/api/v1/notes/purge/{note_id}", headers=HEADERS)
    assert purge_resp.status_code == 200
    
    # 6. Make sure it doesn't exist anymore
    list_resp = client.get("/api/v1/notes", headers=HEADERS)
    assert len(list_resp.json()) == 0
    
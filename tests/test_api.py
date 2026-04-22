from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

# Ensure DB is created for tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_query_endpoint():
    # Depending on whether Hugging Face token works in CI, this test might fallback to dummy data
    # or generate a real response. We test the endpoint plumbing here.
    payload = {
        "question": "How many students enrolled in Python courses in 2024?"
    }
    response = client.post("/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "sql_query" in data
    assert "result" in data
    assert "execution_time" in data

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "most_common_keywords" in data
    assert "slowest_query" in data

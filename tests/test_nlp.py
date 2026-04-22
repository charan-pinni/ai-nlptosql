import pytest
from fastapi import HTTPException
from app.utils import validate_sql_query

def test_validate_sql_query_valid():
    query = "SELECT * FROM students;"
    safe_query = validate_sql_query(query)
    assert safe_query == query

def test_validate_sql_query_invalid_delete():
    query = "DELETE FROM students;"
    with pytest.raises(HTTPException) as exc_info:
        validate_sql_query(query)
    assert exc_info.value.status_code == 400
    assert "Only SELECT queries are allowed" in exc_info.value.detail

def test_validate_sql_query_injection_attempt():
    query = "SELECT * FROM students; DROP TABLE courses;"
    with pytest.raises(HTTPException) as exc_info:
        validate_sql_query(query)
    assert exc_info.value.status_code == 400
    assert "Forbidden SQL keyword detected" in exc_info.value.detail

def test_validate_sql_query_insert():
    query = "INSERT INTO students (name, grade) VALUES ('Test', 95.0);"
    with pytest.raises(HTTPException) as exc_info:
        validate_sql_query(query)
    assert exc_info.value.status_code == 400

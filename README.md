# AI-Powered EdTech Backend System

A production-ready NLP-to-SQL backend service built with FastAPI, LangChain, Hugging Face, and SQLAlchemy. It automatically converts natural language questions into secure SQL queries against an EdTech database schema.

## Features
- **NLP to SQL**: Converts questions like "How many students enrolled in Python in 2024?" to valid SQLite queries.
- **Security Check**: Enforces SELECT-only queries and blocks SQL injection keywords.
- **Analytics**: Tracks query counts, slow queries, and keyword frequencies.
- **FastAPI**: Modern, fast API framework with automatic OpenAPI documentation.

## Setup Instructions

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The database will be automatically initialized and seeded on startup.

### Docker

1. **Build image:**
   ```bash
   docker build -t ai-nlptosql-backend .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 ai-nlptosql-backend
   ```

### Kubernetes

```bash
kubectl apply -f k8s.yaml
```

## API Usage Examples

### 1. NLP to SQL Query (`POST /query`)

**Request:**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "How many students enrolled in Python courses in 2024?"}'
```

**Response:**
```json
{
  "question": "How many students enrolled in Python courses in 2024?",
  "sql_query": "SELECT COUNT(*) FROM students JOIN enrollments ON students.id = enrollments.student_id JOIN courses ON courses.id = enrollments.course_id WHERE courses.name = 'Python' AND strftime('%Y', enrollments.enrolled_at) = '2024';",
  "result": [{"COUNT(*)": 5}],
  "execution_time": 1.2543
}
```

### 2. Analytics (`GET /stats`)

**Request:**
```bash
curl "http://localhost:8000/stats"
```

## NLP Approach & Architecture

We use **LangChain** in combination with the **Hugging Face** API (`mistralai/Mistral-7B-Instruct-v0.2`) to dynamically construct SQL. 
A rigid system prompt limits operations strictly to valid SQL syntax mapping exactly to the SQLite schemas provided (Students, Courses, Enrollments). 
Security is ensured via a custom `validate_sql_query` function which halts executions containing destructive operations like `DROP` or `DELETE`.

## Limitations & Future Improvements
- **Limitations**: The model relies on few-shot prompting/schema injection; extremely complex joins could potentially hallucinate non-existent columns.
- **Future Improvements**:
  - Implement FAISS/Vector DB for RAG-based context injection to handle massive schemas.
  - Implement full database persistence (currently uses a local lightweight `edtech.db`).
  - Cache identical queries for faster sub-100ms response times.

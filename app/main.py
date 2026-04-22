import time
import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from . import database, models, schemas, utils, analytics, nlp_to_sql

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI EdTech Backend System")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    logger.info("Initializing Database...")
    database.init_db()
    logger.info("Database Initialized with Seed Data.")

@app.post("/query", response_model=schemas.QueryResponse)
def execute_query(request: schemas.QueryRequest, db: Session = Depends(database.get_db)):
    """
    Endpoint to convert natural language question to SQL, execute it, and return results.
    """
    start_time = time.time()
    
    # 1. NLP to SQL Conversion
    try:
        sql_query = nlp_to_sql.generate_sql(request.question)
        logger.info(f"Generated SQL: {sql_query}")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"NLP error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to convert question to SQL")

    # 2. Validation / Security checks
    safe_sql = utils.validate_sql_query(sql_query)

    # 3. Execution
    try:
        result_proxy = db.execute(text(safe_sql))
        # Fetch results
        if result_proxy.returns_rows:
            results = [dict(row._mapping) for row in result_proxy]
        else:
            results = []
    except Exception as e:
        logger.error(f"SQL execution error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Database execution error: {str(e)}")

    # 4. Analytics Tracking
    execution_time = time.time() - start_time
    analytics.analytics_manager.record_query(request.question, execution_time)

    return schemas.QueryResponse(
        question=request.question,
        sql_query=safe_sql,
        result=results,
        execution_time=round(execution_time, 4)
    )

@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats():
    """
    Endpoint to retrieve system analytics (query counts, keywords, slow queries).
    """
    return schemas.StatsResponse(**analytics.analytics_manager.get_stats())

@app.get("/")
def root():
    return {"message": "Welcome to the AI EdTech Backend. Access /docs for API documentation."}

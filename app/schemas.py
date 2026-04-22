from pydantic import BaseModel
from typing import Any, List, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql_query: str
    result: Any
    execution_time: float

class StatsResponse(BaseModel):
    total_queries: int
    most_common_keywords: dict
    slowest_query: Optional[dict]

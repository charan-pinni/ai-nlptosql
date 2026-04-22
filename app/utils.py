import re
from fastapi import HTTPException

def validate_sql_query(query: str) -> str:
    """
    Validates that the SQL query only performs SELECT operations
    and does not contain potentially destructive commands.
    """
    query = query.strip()
    
    # Ensure it starts with SELECT
    if not re.match(r"^SELECT\b", query, re.IGNORECASE):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
    
    # Check for forbidden keywords (SQL injection / modification prevention)
    forbidden_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", 
        "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE"
    ]
    
    # Use word boundaries to prevent matching sub-words
    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", query, re.IGNORECASE):
            raise HTTPException(
                status_code=400, 
                detail=f"Forbidden SQL keyword detected: {keyword}. Only SELECT is allowed."
            )
            
    return query

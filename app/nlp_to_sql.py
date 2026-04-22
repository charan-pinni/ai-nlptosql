import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from fastapi import HTTPException
import logging
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
logger = logging.getLogger(__name__)

prompt_template = PromptTemplate(
    input_variables=["question"],
    template="""You are an expert SQL generator.
Convert the question into a valid SQLite SQL query using only these tables:
students(id, name, grade, created_at)
courses(id, name, category)
enrollments(id, student_id, course_id, enrolled_at)

Rules:
* Only SELECT queries allowed
* Use proper JOINs
* Use correct column names
* Do not add explanations

Example 1:
Question: How many students enrolled in Python courses in 2024?
SQL: SELECT COUNT(*) FROM students JOIN enrollments ON students.id = enrollments.student_id JOIN courses ON courses.id = enrollments.course_id WHERE courses.name = 'Python' AND strftime('%Y', enrollments.enrolled_at) = '2024';

Example 2:
Question: Show me the names of all students and their grades.
SQL: SELECT name, grade FROM students;

Question: {question}
SQL:"""
)

try:
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        huggingfacehub_api_token=HF_TOKEN,
        task="conversational",
        max_new_tokens=256,
        temperature=0.2
    )
    chat_model = ChatHuggingFace(llm=llm)
except Exception as e:
    logger.error(f"Failed to initialize HuggingFaceEndpoint: {e}")
    chat_model = None

def generate_sql(question: str) -> str:
    """
    Converts a natural language question to a SQL query using HuggingFace LLM.
    """
    if not chat_model:
        raise HTTPException(status_code=503, detail="LLM service is currently unavailable.")

    try:
        chain = prompt_template | chat_model
        response = chain.invoke({"question": question})
        
        # Clean up output
        sql_query = response.content.strip()
        
        # Strip potential markdown if any model outputs it
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        sql_query = sql_query.strip()
        
        # Additional safety check to ensure it's not empty
        if not sql_query:
            raise ValueError("LLM returned an empty response")
            
        return sql_query
    except Exception as e:
        logger.error(f"Error during LLM invocation: {e}")
        raise HTTPException(status_code=502, detail=f"Error generating SQL from LLM: {str(e)}")

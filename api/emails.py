from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from typing import Optional, List
import os
from dotenv import load_dotenv

# Neo4j connection setup
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# FastAPI app
app = FastAPI()

# Response Models
class EmailInfo(BaseModel):
    email_id: str
    subject: Optional[str] = None
    body_excerpt: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    date_sent: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    category: Optional[str] = None
    thread_id: Optional[str] = None

# Utility function
def run_query(tx, query: str, params: dict = None):
    if params is None:
        params = {}
    return tx.run(query, **params)

def format_datetime(dt_obj):
    """Convert Neo4j datetime to ISO string"""
    if dt_obj is None:
        return None
    try:
        return dt_obj.isoformat() if hasattr(dt_obj, 'isoformat') else str(dt_obj)
    except:
        return str(dt_obj)

def get_emails_data(tx):
    """Transaction function to get emails data"""
    cypher = """
    MATCH (e:Email)
    OPTIONAL MATCH (e)-[:RECEIVED_FROM]->(c:Client)
    OPTIONAL MATCH (e)-[:HAS_CATEGORY]->(cat:Category)
    OPTIONAL MATCH (e)-[:PART_OF_THREAD]->(t:Thread)
    RETURN e, c, cat, t
    ORDER BY e.date_sent DESC
    """
    
    result = tx.run(cypher)
    emails = []
    
    for record in result:
        email_data = dict(record['e'])
        client_data = dict(record['c']) if record['c'] else {}
        category_data = dict(record['cat']) if record['cat'] else {}
        thread_data = dict(record['t']) if record['t'] else {}
        
        email_info = EmailInfo(
            email_id=email_data.get('email_id', ''),
            subject=email_data.get('subject'),
            body_excerpt=email_data.get('body_excerpt'),
            direction=email_data.get('direction'),
            status=email_data.get('status'),
            date_sent=format_datetime(email_data.get('date_sent')),
            client_name=client_data.get('name'),
            client_email=client_data.get('email_address'),
            category=category_data.get('name'),
            thread_id=thread_data.get('thread_id')
        )
        emails.append(email_info)
    
    return emails

@app.get("/emails", response_model=List[EmailInfo])
async def get_all_emails():
    """
    Retrieve all emails with their related information.
    """
    
    try:
        with driver.session() as session:
            emails = session.read_transaction(get_emails_data)
            return emails
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
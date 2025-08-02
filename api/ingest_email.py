from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Neo4j connection setup
# Load from .env
load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# FastAPI app
app = FastAPI()

# Models
class EmailIn(BaseModel):
    client_id: str
    email_id: str
    subject: str
    body_excerpt: Optional[str] = None
    thread_id: str
    category: str
    name: Optional[str] = None
    email_address: Optional[str] = None

# Utility function to run Cypher
def run_tx(tx, query: str, params: dict):
    return tx.run(query, **params).single()

@app.post("/ingest_email")
async def ingest_email(data: EmailIn):
    params = {
        "client_id": data.client_id,
        "name": data.name,
        "email_address": data.email_address,
        "email_id": data.email_id,
        "subject": data.subject,
        "body_excerpt": data.body_excerpt or "",
        "thread_id": data.thread_id,
        "category": data.category,
        "now": datetime.utcnow().isoformat()
    }

    cypher = """
    // 1. Ensure Client exists, create if missing
    MERGE (c:Client {client_id: $client_id})
    ON CREATE SET c.created = datetime(),
                  c.name = $name,
                  c.email_address = $email_address
    ON MATCH SET c.name = coalesce($name, c.name),
                 c.email_address = coalesce($email_address, c.email_address)

    // 2. Create Thread if it doesn't exist
    MERGE (t:Thread {thread_id: $thread_id})
    ON CREATE SET t.created = datetime()

    // 3. Create Email
    MERGE (e:Email {email_id: $email_id})
    ON CREATE SET
        e.subject = $subject,
        e.body_excerpt = $body_excerpt,
        e.direction = "inbound",
        e.status = "To Review",
        e.date_sent = datetime($now)

    // 4. Create or link Category
    MERGE (cat:Category {name: toLower($category)})

    // 5. Relationships
    MERGE (c)<-[:RECEIVED_FROM]-(e)
    MERGE (e)-[:HAS_CATEGORY]->(cat)
    MERGE (e)-[:PART_OF_THREAD]->(t)
    """

    try:
        with driver.session() as session:
            session.write_transaction(run_tx, cypher, params)
        return {"status": "ok", "email_id": data.email_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

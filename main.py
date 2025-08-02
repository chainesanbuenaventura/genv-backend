from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from neo4j import GraphDatabase

# Neo4j connection (unchanged)
NEO4J_URI      = "neo4j+s://b01ee78e.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "muOwGwkMRs9D5VgVK7fJqgkIanuTKXlr-WFca4g1SMw"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# --- Data models with aliases ---
class Experience(BaseModel):
    company: str
    title:   str
    years:   str

class Content(BaseModel):
    candidate_name: str             = Field(..., alias="Candidate name")
    email:          str             = Field(..., alias="Email")
    skills:         List[str]       = Field(..., alias="Skills")
    experience:     List[Experience] = Field(..., alias="Experience")

    class Config:
        allow_population_by_field_name = True
        # allow using .dict(by_alias=True) if you want output with original keys

class Message(BaseModel):
    role:    str
    content: Content

class Item(BaseModel):
    index:   int
    message: Message

app = FastAPI()

@app.post("/ingest")
async def ingest(items: List[Item]):
    content = items[0].message.content
    q = """
    MERGE (c:Candidate {email:$email})
      ON CREATE SET c.name = $candidate_name
    WITH c
    UNWIND $skills AS skill
      MERGE (s:Skill {name:skill})
      MERGE (c)-[:HAS_SKILL]->(s)
    WITH c
    UNWIND $experience AS exp
      MERGE (e:Experience {
        company: exp.company,
        title: exp.title,
        years: exp.years
      })
      MERGE (c)-[:WORKED_AT]->(e)
    RETURN c.email AS ingested
    """
    params = {
      "email":           content.email,
      "candidate_name":  content.candidate_name,
      "skills":          content.skills,
      "experience":      [e.dict() for e in content.experience],
    }
    try:
        with driver.session() as session:
            rec = session.run(q, params).single()
            return {"status":"ok", "candidate":rec["ingested"]}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


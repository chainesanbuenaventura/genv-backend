from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import logging
from contextlib import asynccontextmanager

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain, GraphCypherQAChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")

settings = Settings()

# Global variables for services
kg: Optional[Neo4jGraph] = None
chain: Optional[GraphCypherQAChain] = None
llm: Optional[ChatOpenAI] = None
embedding_provider: Optional[OpenAIEmbeddings] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global kg, chain, llm, embedding_provider
    
    try:
        # Initialize services
        logger.info("Initializing Neo4j connection...")
        kg = Neo4jGraph(
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD
        )
        
        logger.info("Initializing OpenAI services...")
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        embedding_provider = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
        # Create Cypher prompt
        cypher_prompt = PromptTemplate.from_template("""
        You are an expert Cypher translator. Given a question, generate only the Cypher query needed to answer it.
        Question: {question}
        Cypher:
        """)
        
        logger.info("Initializing GraphCypherQAChain...")
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0),
            graph=kg,
            verbose=True,
            allow_dangerous_requests=True,
        )
        
        logger.info("Services initialized successfully!")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down services...")
        if kg:
            kg.close()

# Create FastAPI app
app = FastAPI(
    title="Neo4j Graph QA API",
    description="API for querying Neo4j graph database using natural language",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str = Field(..., description="Natural language question to ask the graph")
    verbose: bool = Field(default=False, description="Whether to return verbose output")

class QuestionResponse(BaseModel):
    answer: str = Field(..., description="Answer to the question")
    cypher_query: Optional[str] = Field(None, description="Generated Cypher query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class CypherRequest(BaseModel):
    query: str = Field(..., description="Cypher query to execute")

class CypherResponse(BaseModel):
    result: List[Dict[str, Any]] = Field(..., description="Query results")
    count: int = Field(..., description="Number of results returned")

class NodeUpdateRequest(BaseModel):
    node_id: Optional[int] = Field(None, description="Node ID to update")
    labels: Optional[List[str]] = Field(None, description="Node labels for matching")
    match_properties: Optional[Dict[str, Any]] = Field(None, description="Properties to match node")
    set_properties: Dict[str, Any] = Field(..., description="Properties to set/update")

class HealthResponse(BaseModel):
    status: str
    neo4j_connected: bool
    openai_configured: bool

# Dependency to get services
def get_services():
    if not kg or not chain or not llm:
        raise HTTPException(status_code=503, detail="Services not initialized")
    return kg, chain, llm

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "Neo4j Graph QA API", "status": "running"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    neo4j_connected = kg is not None
    openai_configured = os.getenv("OPENAI_API_KEY") is not None
    
    if neo4j_connected:
        try:
            # Test Neo4j connection
            kg.query("RETURN 1 as test")
        except Exception:
            neo4j_connected = False
    
    return HealthResponse(
        status="healthy" if neo4j_connected and openai_configured else "unhealthy",
        neo4j_connected=neo4j_connected,
        openai_configured=openai_configured
    )

@app.post("/chat", response_model=QuestionResponse)
async def chat(request: QuestionRequest, services=Depends(get_services)):
    """Ask a natural language question about the graph"""
    kg_service, chain_service, llm_service = services
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Run the chain
        result = chain_service.run(request.question)
        
        response = QuestionResponse(
            answer=result,
            context={"question": request.question} if request.verbose else None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/cypher", response_model=CypherResponse)
async def execute_cypher(request: CypherRequest, services=Depends(get_services)):
    """Execute a raw Cypher query"""
    kg_service, _, _ = services
    
    try:
        logger.info(f"Executing Cypher query: {request.query}")
        
        result = kg_service.query(request.query)
        
        return CypherResponse(
            result=result,
            count=len(result)
        )
        
    except Exception as e:
        logger.error(f"Error executing Cypher query: {e}")
        raise HTTPException(status_code=400, detail=f"Cypher query error: {str(e)}")

@app.post("/update-node")
async def update_node(request: NodeUpdateRequest, services=Depends(get_services)):
    """Update node properties in Neo4j"""
    kg_service, _, _ = services
    
    try:
        # Build the Cypher query
        if request.node_id:
            match_clause = f"MATCH (n) WHERE ID(n) = {request.node_id}"
        elif request.labels and request.match_properties:
            labels_str = ":".join(request.labels)
            props_str = ", ".join([f"{k}: ${k}" for k in request.match_properties.keys()])
            match_clause = f"MATCH (n:{labels_str} {{{props_str}}})"
        elif request.match_properties:
            props_str = ", ".join([f"{k}: ${k}" for k in request.match_properties.keys()])
            match_clause = f"MATCH (n {{{props_str}}})"
        else:
            raise HTTPException(status_code=400, detail="Must provide either node_id or match_properties")
        
        # Build SET clause
        set_clauses = []
        for key, value in request.set_properties.items():
            if isinstance(value, str):
                set_clauses.append(f"n.{key} = '{value}'")
            else:
                set_clauses.append(f"n.{key} = {value}")
        
        set_clause = "SET " + ", ".join(set_clauses)
        
        cypher_query = f"{match_clause} {set_clause} RETURN n"
        
        logger.info(f"Executing update query: {cypher_query}")
        
        # Execute with parameters if needed
        params = {}
        if request.match_properties:
            params.update(request.match_properties)
        
        if params:
            result = kg_service.query(cypher_query, params)
        else:
            result = kg_service.query(cypher_query)
        
        return {
            "message": "Node updated successfully",
            "updated_nodes": len(result),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error updating node: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating node: {str(e)}")

@app.get("/schema")
async def get_schema(services=Depends(get_services)):
    """Get the Neo4j database schema"""
    kg_service, _, _ = services
    
    try:
        schema = kg_service.get_schema
        return {"schema": schema}
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting schema: {str(e)}")

@app.get("/stats")
async def get_database_stats(services=Depends(get_services)):
    """Get database statistics"""
    kg_service, _, _ = services
    
    try:
        # Get node counts by label
        node_stats = kg_service.query("""
            CALL db.labels() YIELD label
            CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) YIELD value
            RETURN label, value.count as count
        """)
        
        # Get relationship counts by type
        rel_stats = kg_service.query("""
            CALL db.relationshipTypes() YIELD relationshipType
            CALL apoc.cypher.run('MATCH ()-[r:' + relationshipType + ']->() RETURN count(r) as count', {}) YIELD value
            RETURN relationshipType, value.count as count
        """)
        
        return {
            "nodes": node_stats,
            "relationships": rel_stats
        }
        
    except Exception as e:
        # Fallback if APOC is not available
        try:
            basic_stats = kg_service.query("""
                MATCH (n) 
                RETURN labels(n) as labels, count(n) as count
                ORDER BY count DESC
            """)
            
            return {
                "nodes": basic_stats,
                "relationships": [],
                "note": "Limited stats (APOC not available)"
            }
            
        except Exception as e2:
            logger.error(f"Error getting stats: {e2}")
            raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e2)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
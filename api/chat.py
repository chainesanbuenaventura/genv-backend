from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    verbose: Optional[bool] = False

class QuestionResponse(BaseModel):
    answer: str
    context: Optional[Dict] = None

@app.post("/chat", response_model=QuestionResponse)
async def chat(request: QuestionRequest):
    try:
        kg = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        llm = ChatOpenAI(model="gpt-4", temperature=0)

        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=kg,
            verbose=request.verbose,
            allow_dangerous_requests=True
        )

        result = chain.run(request.question)

        return QuestionResponse(
            answer=result,
            context={"question": request.question} if request.verbose else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

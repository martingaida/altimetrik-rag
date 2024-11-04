from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pipelines.inference import inference_pipeline
from loguru import logger

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


@app.post("/rag", response_model=QueryResponse)
async def rag_endpoint(request: QueryRequest):
    """RAG endpoint that processes queries and returns answers"""
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Run inference pipeline
        pipeline_response = inference_pipeline(request.query)
        
        # Extract answer from pipeline response
        answer = pipeline_response.steps["generate_answer"].output.load()
        
        if not answer:
            raise ValueError("No answer generated")
            
        logger.info("Successfully generated answer")
        return QueryResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Error in RAG endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
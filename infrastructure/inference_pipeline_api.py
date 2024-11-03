from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import settings
from application.rag.retriever import ContextRetriever
from application.utils import misc
from domain.embedded_chunks import EmbeddedChunk
from infrastructure.opik_utils import configure_opik
from model.inference import InferenceExecutor, LLMInferenceSagemakerEndpoint

configure_opik()

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


def call_llm_service(query: str, context: str | None) -> str:
    llm = LLMInferenceSagemakerEndpoint(
        endpoint_name=settings.SAGEMAKER_ENDPOINT_INFERENCE, inference_component_name=None
    )
    answer = InferenceExecutor(llm, query, context).execute()

    return answer


def rag(query: str) -> str:
    retriever = ContextRetriever(mock=False)
    documents = retriever.search(query, k=3)
    context = EmbeddedChunk.to_context(documents)

    answer = call_llm_service(query, context)

    return answer


@app.post("/rag", response_model=QueryResponse)
async def rag_endpoint(request: QueryRequest):
    try:
        answer = rag(query=request.query)

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

from fastapi import FastAPI, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, IngestRequest, IngestResponse
from app.services.rag_service import get_context, ingest_url
from app.services.llm_service import generate_parallel_responses


app = FastAPI(
    title="Voice-Enabled RAG Assistant API",
    description="Backend API for interacting with the AI Voice Assistant using parallel LLM responses.",
    version="1.0.0"
)

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # Retrieve context from Supabase Vector Store
        context_str = get_context(request.query)
        
        # Query LLMs in parallel with context
        responses = await generate_parallel_responses(request.query, context_str)
        
        # Return merged response
        return QueryResponse(
            responses=responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest", response_model=IngestResponse)
def ingest_website(request: IngestRequest):
    try:
        url_str = str(request.url)
        result = ingest_url(url_str)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

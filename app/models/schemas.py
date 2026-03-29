from pydantic import BaseModel, HttpUrl
from typing import List, Dict

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    responses: Dict[str, str]

class IngestRequest(BaseModel):
    url: HttpUrl

class IngestResponse(BaseModel):
    message: str
    pages_scraped: int
    chunks_created: int

import asyncio
from langchain_core.prompts import ChatPromptTemplate
from app.core.utils import kimi_llm, openai_llm, gemini_llm
from app.core.prompts import RAG_SYSTEM_PROMPT



# Create Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM_PROMPT),
    ("human", "{query}")
])

async def call_model(llm, query: str, context: str) -> str:
    """Helper function to format the prompt and call an LLM asynchronously."""
    prompt = prompt_template.format_messages(context=context, query=query)
    response = await llm.ainvoke(prompt)
    return response.content


async def generate_parallel_responses(query: str, context: str) -> dict:
    """
    Calls Gemini, DeepSeek, and Kimi concurrently using asyncio.gather.
    Instructs the models to answer strictly based on the provided context via the system prompt.
    """
    # Define tasks
    gemini_task = call_model(gemini_llm, query, context)
    openai_task = call_model(openai_llm, query, context)
    kimi_task = call_model(kimi_llm, query, context)
    
    # Execute calls concurrently
    results = await asyncio.gather(
        gemini_task,
        openai_task,
        kimi_task,
        return_exceptions=True
    )
    
    # Map results to models, handling any exceptions cleanly
    responses = {}
    models = ["gemini", "openai", "kimi"]
    for model_name, result in zip(models, results):
        if isinstance(result, Exception):
            responses[model_name] = f"Error generating response: {str(result)}"
        else:
            responses[model_name] = result
            
    return responses

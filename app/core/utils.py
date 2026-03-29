from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from app.core.config import settings


#Initialize Generation models
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GOOGLE_API_KEY,
    temperature=0.3
)

openai_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.GROQ_API_KEY,
    temperature=0.3)


kimi_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
    model="moonshotai/kimi-k2.5",
    temperature=0.3,
    max_completion_tokens=1000
)


# Initialize Google Generative AI Embeddings
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001", 
#     google_api_key=settings.GOOGLE_API_KEY
# )

#initialize Openai embeddings
embeddings=OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=settings.OPENAI_API_KEY)

#Initialize Supabase PGVector Vector Store
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="sunmarke_chunks",
    connection=settings.SUPABASE_DB_URI,
    use_jsonb=True,
)
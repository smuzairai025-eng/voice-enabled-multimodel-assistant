# ⚙️ Backend API: Sunmarke AI Voice Assistant

This repository contains the backend infrastructure for the Sunmarke AI Voice Assistant. It is a robust, asynchronous FastAPI application designed to handle Retrieval-Augmented Generation (RAG) and orchestrate simultaneous requests to three different Large Language Models (LLMs).

## 🚀 Live Deployment
* **API Base URL:** `[INSERT_YOUR_RAILWAY_BACKEND_URL]`
* **Health Check:** `[INSERT_YOUR_RAILWAY_BACKEND_URL]/`
* **Ask Endpoint:** `[INSERT_YOUR_RAILWAY_BACKEND_URL]/api/ask`

## 💻 Tech Stack
* **Framework:** FastAPI (Python 3.12+)
* **Package Manager:** `uv`
* **AI & Orchestration:** LangChain, Asyncio
* **Embeddings:** OpenAI (`text-embedding-3-small`)
* **Vector Database:** PostgreSQL + PGVector (Hosted on Supabase)
* **Web Scraping:** Firecrawl API
* **Deployment:** Railway

## 🏗️ Architecture Design

The backend is built with a clean separation of concerns:
1. **Data Ingestion (`/api/ingest`):** Takes a target URL, uses Firecrawl to scrape Markdown content (ignoring dynamic paths like `/events` or `/calendar`), chunks the text using LangChain's `RecursiveCharacterTextSplitter`, embeds it via OpenAI, and stores the vectors in Supabase PGVector.
2. **Retrieval-Augmented Generation (`/api/ask`):** * Receives the transcribed user query from the frontend.
   * Embeds the query and performs a cosine-similarity search against the PGVector database to retrieve the top 4 most relevant document chunks.
   * Uses Python's `asyncio.gather` to send the context and query to **Gemini**, **DeepSeek**, and **Kimi** concurrently.
   * Aggregates the responses into a single JSON object and returns it to the client.

## 💰 Estimated Cost Analysis (Per 1,000 Queries)

[cite_start]The architecture is heavily optimized to leverage free tiers where possible[cite: 48]. Below is the estimated operational cost for processing 1,000 standard queries (assuming ~1,000 input context tokens and ~150 output tokens per query).

| Component | Provider / Model | Est. Usage (1k queries) | Estimated Cost | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Model 1** | Google Gemini 1.5 Flash | 1M In / 150k Out | **$0.00** | Covered by the generous free tier (15 RPM). Paid equivalent: ~$0.12. |
| **Model 2** | DeepSeek (`deepseek-chat`) | 1M In / 150k Out | **$0.00** | Utilizing OpenRouter's free endpoint. Paid equivalent: ~$0.19. |
| **Model 3** | Kimi (`moonshot-v1-8k`) | 1M In / 150k Out | **$0.00** | Covered by free tier limits. Paid equivalent: ~$1.85. |
| **Embeddings**| OpenAI (`text-embedding-3-small`) | 100k query tokens | **$0.002** | Highly cost-efficient at $0.02 per 1M tokens. |
| **Database** | Supabase (PGVector) | Vector Storage | **$0.00** | Fits comfortably within the 500MB free tier allowance. |
| **Hosting** | Railway | Bandwidth/Compute | **~$0.10** | Minimal active compute time due to fast async execution. |
| **Total** | | **1,000 Queries** | **< $0.15** | Extremely cost-effective production setup. |

## 🛠️ Local Setup Instructions

### Prerequisites
* Python 3.10+
* `uv` package manager installed
* A Supabase project with PGVector enabled

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/smuzairai025-eng/voice-enabled-multimodel-assistant.git
   cd voice-enabled-assisstant'

Install dependencies:

uv sync

# Or alternatively: pip install -r requirements.txt

Set up environment variables by creating a .env file in the root directory:

SUPABASE_DB_URI=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# KIMI_API_KEY=your_kimi_key (If using native Moonshot API)

Start the development server:

uvicorn app.main:app --reload --port 8000
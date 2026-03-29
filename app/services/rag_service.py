import os
import json
from urllib.parse import urlparse
from firecrawl import Firecrawl
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.utils import embeddings,vector_store
from app.core.config import settings
from langchain_core.documents import Document



def get_context(query: str) -> str:
    """
    Embeds the user query, searches the vector store for the top 4 relevant chunks,
    and returns them formatted as a single string.
    """
    try:
        print(f"Searching vector store for query: '{query}'")
        # Using similarity_search to run the vector search synchronously
        docs = vector_store.similarity_search(query, k=4)
        
        # Format the retrieved chunks into a single context string
        context_chunks = [doc.page_content for doc in docs]
        formatted_context = "\n\n---\n\n".join(context_chunks)
        
        print(f"Successfully retrieved {len(docs)} context chunks.")
        return formatted_context
    except Exception as e:
        print(f"Error retrieving context: {e}")
        raise e

def ingest_url(url: str) -> dict:
    """
    Checks for locally cached chunks; if none exist, crawls the URL using Firecrawl, 
    cleans the markdown, chunks it, saves to JSON, and ingests into PGVector.
    """
    domain = urlparse(url).netloc.replace("www.", "")
    output_file = os.path.join("data", f"{domain}_chunks.json")
    
    try:
        # Check if the chunk file already exists
        if os.path.exists(output_file):
            print(f"Found existing chunk file for {domain} at {output_file}. Skipping Firecrawl.")
            with open(output_file, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
                
            if output_data:
                print(f"Loaded {len(output_data)} chunks from local file. Converting to Documents...")
                # Convert the raw JSON back into LangChain Document objects
                all_chunks = [Document(page_content=item["text"], metadata=item["metadata"]) for item in output_data]
                
                print("Ingesting cached chunks into PGVector...")
                vector_store.add_documents(all_chunks)
                print("Local ingestion completed successfully.")
                
                return {
                    "message": "Ingestion successful from local cache",
                    "pages_scraped": 0,
                    "chunks_created": len(all_chunks)
                }
            else:
                print("Existing file is empty. Proceeding to scrape...")

        # 1. Scrape with Firecrawl
        print(f"No local cache found. Starting Firecrawl for: {url}")
        app = Firecrawl(api_key=settings.FIRECRAWL_API_KEY)
        crawl_job = app.crawl(
            url=url, 
            limit=20,
            exclude_paths=['/news/*', '/blog/*', '/events/*', '/gallery/*', '/calendar/*'],
            scrape_options={'formats': ['markdown']},
            poll_interval=10
        )
        
        if crawl_job.status != 'completed':
            raise Exception(f"Crawl failed or timed out. Status: {crawl_job.status}")
        
        raw_data = [page if isinstance(page, dict) else page.model_dump() for page in crawl_job.data]
        print(f"Firecrawl completed. Successfully scraped {len(raw_data)} pages.")
        
        # 2. Text Splitting and Cleaning
        print("Initializing text splitting and cleaning...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        
        for page in raw_data:
            markdown_content = page.get('markdown')
            if not markdown_content:
                continue
                
            page_url = page.get('metadata', {}).get('url', url)
            title = page.get('metadata', {}).get('title', domain)
            
            if "[VLE Login]" in markdown_content:
                parts = markdown_content.split("[VLE Login]")
                markdown_content = parts[-1].strip()
                
            if len(markdown_content) < 50:
                continue
                
            chunks = text_splitter.create_documents(
                [markdown_content], 
                metadatas=[{"url": page_url, "title": title}]
            )
            all_chunks.extend(chunks)
            
        print(f"Text splitting complete. Created {len(all_chunks)} total chunks.")
            
        # 3. Save chunks to disk
        print(f"Saving chunks to disk at {output_file}...")
        os.makedirs("data", exist_ok=True)
        output_data = [{"text": chunk.page_content, "metadata": chunk.metadata} for chunk in all_chunks]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)
            
        # 4. Ingest to PGVector
        if all_chunks:
            print("Ingesting new chunks into PGVector...")
            vector_store.add_documents(all_chunks)
            print("Ingestion completed successfully.")
            
        return {
            "message": "Ingestion successful after scraping",
            "pages_scraped": len(raw_data),
            "chunks_created": len(all_chunks)
        }
        
    except Exception as e:
        print(f"CRITICAL ERROR during ingestion process: {e}")
        raise e
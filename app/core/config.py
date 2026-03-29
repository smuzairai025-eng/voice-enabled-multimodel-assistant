from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_DB_URI: str
    GOOGLE_API_KEY: str
    DEEPSEEK_API_KEY: str
    OPENROUTER_API_KEY: str
    FIRECRAWL_API_KEY: str
    OPENAI_API_KEY : str
    GROQ_API_KEY : str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

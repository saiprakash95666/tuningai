"""Configuration management for TuningAI"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    APP_NAME: str = "TuningAI"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str = ""
    
    # LLM Settings
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    # Feature Flags
    ENABLE_RAG: bool = False
    ENABLE_AGENTS: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/tuningai.db"
    
    # Vector DB (Week 2)
    VECTOR_DB_PATH: str = "./data/vectordb"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
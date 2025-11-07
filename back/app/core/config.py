from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Token Budget Configuration
    TOKEN_BUDGET_TOTAL: int = 8000
    TOKEN_BUDGET_HISTORY_PCT: float = 0.30  # 30% for history
    TOKEN_BUDGET_RAG_PCT: float = 0.70      # 70% for RAG KB
    SLIDING_WINDOW_SIZE: int = 10           # Keep last N messages
    
    @property
    def TOKEN_BUDGET_HISTORY(self) -> int:
        """Calculate history token budget."""
        return int(self.TOKEN_BUDGET_TOTAL * self.TOKEN_BUDGET_HISTORY_PCT)
    
    @property
    def TOKEN_BUDGET_RAG(self) -> int:
        """Calculate RAG KB token budget."""
        return int(self.TOKEN_BUDGET_TOTAL * self.TOKEN_BUDGET_RAG_PCT)
    
    @property
    def MODELS_DIR(self) -> Path:
        """Get path to ML models directory."""
        return Path(__file__).parent.parent / "ml" / "models"
    
    @property
    def KB_DIR(self) -> Path:
        """Get path to knowledge base directory (root kb folder)."""
        return Path(__file__).parent.parent.parent.parent / "kb"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

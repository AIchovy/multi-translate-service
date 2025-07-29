"""
Configuration module for Multi Translate Service
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration class"""
    
    # Application basic configuration
    environment: str = "development"
    debug: bool = True
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API configuration
    api_prefix: str = "/api/v1"
    
    # Whisper model
    whisper_model: str = "tiny"
    
    # OPENAI API configuration
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None

    # Database configuration
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "user"
    database_password: str = "password"
    database_name: str = "multi_translate_db"
    database_echo: bool = False  # Set to True for SQL query logging
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    @property
    def database_url(self) -> str:
        """Generate async database URL from components"""
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def sync_database_url(self) -> str:
        """Generate sync database URL for Celery tasks"""
        return f"postgresql+psycopg2://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None  # If None, only console logging
    log_max_size: int = 10  # Max log file size in MB
    log_backup_count: int = 5  # Number of backup log files
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global configuration instance
settings = Settings() 
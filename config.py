"""Configuration management for AI Streamer."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Aliyun Configuration
    aliyun_access_key_id: str
    aliyun_access_key_secret: str
    aliyun_region: str = "cn-hangzhou"
    
    # DashScope API Key
    dashscope_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

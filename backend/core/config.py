from pydantic_settings import BaseSettings
from typing import List, Union
import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv(override=True)
env_dict = dotenv_values(".env")

class Settings(BaseSettings):
    app_name: str = "AI Vision OCR Platform"
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", 8000))
    huggingface_api_token: str = env_dict.get("HUGGINGFACE_API_TOKEN", "")

    # CORS settings
    allowed_origins: Union[str, List[str]] = os.getenv("ALLOWED_ORIGINS", "*")

    # Upload settings
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", 10))

    # Frontend static files path (for serving Flutter Web build)
    frontend_path: str = os.getenv("FRONTEND_PATH", "")

    class Config:
        env_file = ".env"


settings = Settings()

# Parse allowed origins if it's a string
if isinstance(settings.allowed_origins, str):
    if settings.allowed_origins == "*":
        settings.allowed_origins = ["*"]
    else:
        settings.allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]

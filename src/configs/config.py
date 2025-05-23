"""Load environment variables."""

import logging
import os
from typing import Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel

logger = logging.getLogger(__name__)
class APISettings(BaseSettings):
    """
    Manages API configurations loaded from environment variables.
    Pydantic will automatically attempt to load these from a .env file
    or system environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Weather API KEY
    WEATHER_API_KEY: str = Field(..., description="API key for weather data")

    # Weather API Endpoints
    MAX_HOURLY_FORECAST_ITEMS: int = Field(default=24, description="Maximum number of hourly forecast items to return")

    # Model configuration
    MODEL_ID: str = Field(..., description="ID of the LLM model to use")

    # Local LLM configuration
    MODEL_HOST: str = Field(..., description="Host of the LLM model")
    MODEL_PORT: int = Field(..., description="Port of the LLM model")

# Global instance of API settings, loaded from .env
env = APISettings()


class LLMDetails(BaseModel):
    """Holds the details of the configured LLM provider."""
    model: Any
    description: str
    model_name: str
    is_direct: bool # True if using directly OpenAI or Gemini..., False for local LLM

def get_llm_model() -> LLMDetails:
    """Determines the LLM provider configuration based on environment variables.

    Returns:
        LLMDetails: An object containing the model instance,
                    UI description, model name, and configuration type.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if openai_api_key and gemini_api_key:
        logger.critical("Configuration Error: Both OPENAI_API_KEY and GEMINI_API_KEY are set. Please set only one.")
        exit(1)

    model_name = env.MODEL_ID

    if openai_api_key and openai_api_key.strip() != "":
        model = OpenAIModel(model_name=model_name)
        description = f"Powered by OpenAI LLM: [{model_name}](https://platform.openai.com/docs/models)."
        logger.info(f"Using OpenAI LLM: {model_name}")
        is_direct = True
    elif gemini_api_key and gemini_api_key.strip() != "":
        model = GeminiModel(model_name=model_name)
        description = f"Powered by Gemini LLM: [{model_name}](https://ai.google.dev/gemini-api/docs/)."
        logger.info(f"Using Gemini LLM: {model_name}")
        is_direct = True
    else:
        _provider = OpenAIProvider(base_url=f"{env.MODEL_HOST}:{env.MODEL_PORT}/v1")
        model = OpenAIModel(model_name=model_name, provider=_provider)
        logger.info(f"Using local LLM: {model_name} via {env.MODEL_HOST}:{env.MODEL_PORT}")
        description = (
            f"Powered by local LLM: [{model_name}](https://ollama.com/) via {env.MODEL_HOST}:{env.MODEL_PORT}.\n"
            f"Ensure your local LLM server (e.g., Ollama) is running and the model is available."
        )
        is_direct = False
    
    return LLMDetails(
        model=model,
        description=description,
        model_name=model_name,
        is_direct=is_direct
    )
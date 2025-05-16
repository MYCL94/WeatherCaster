from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class APISettings(BaseSettings):
    """
    Manages API configurations loaded from environment variables.
    Pydantic will automatically attempt to load these from a .env file
    or system environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Geocoding API
    GEO_API: str = Field(..., description="API for geocoding")

    # Weather API KEY
    WEATHER_API_KEY: str = Field(..., description="API key for weather data")

    # Weather API Endpoints
    WEATHER_API_CURRENT: str = Field(..., description="API for current weather forecasts")
    WEATHER_API_HOURLY: str = Field(..., description="API for hourly weather forecasts")
    WEATHER_API_DAILY: str = Field(..., description="API for daily weather forecasts")

    # Model configuration
    MODEL_ID: str = Field(..., description="ID of the LLM model to use")
    MODEL_HOST: str = Field(..., description="Host of the LLM model")
    MODEL_PORT: int = Field(..., description="Port of the LLM model")
    MODEL_API_KEY: str | None = Field(default=None, description="API key for the LLM model")

env = APISettings()



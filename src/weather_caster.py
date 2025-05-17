from typing import AsyncGenerator
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from tools.weather_tools import WeatherAPIClient
from agent_prompt import AGENT_SYSTEM_PROMPT
from config import env

class WeatherCaster:
    def __init__(self) -> None:
        load_dotenv() # Load environment variables from .env

        #   1. Setup local LLM with Config()
        #   2. The list of available tools.
        #   3. LLM configuration (using Ollama).
        model = OpenAIModel(model_name=env.MODEL_ID,
                            provider=OpenAIProvider(base_url=f"{env.MODEL_HOST}:{env.MODEL_PORT}/v1")
                            )
        weather_client = WeatherAPIClient()
        self.agent = Agent(model=model,
                           tools=[Tool(weather_client.get_weather_forecast)
                                  ],
                           system_prompt=AGENT_SYSTEM_PROMPT,
                           retries=3,
                           output_retries=3,
                           )


    async def get_response(self, user_query: str) -> AsyncGenerator:
        """
        Gets a response from the chatbot for a given user query.
        """
        yield await self.agent.run(user_query)

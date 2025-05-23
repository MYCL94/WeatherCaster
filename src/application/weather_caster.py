from typing import AsyncGenerator
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
from application.formatting import format_weather_summary
from model_definition.final_response import WeatherForecast
from tools.weather_tools import WeatherAPIClient
from configs.agent_prompt import AGENT_SYSTEM_PROMPT
from configs.config import get_llm_model

class WeatherCaster:
    def __init__(self) -> None:
        """Initializes the WeatherCaster."""
        load_dotenv()
        #   1. Setup LLM with Config()
        #   2. Enter list of available tools.
        #   3. Use system prompt.
        self.llm_model = get_llm_model()
        self.weather_client = WeatherAPIClient()
        self.agent = Agent(model=self.llm_model.model,
                           tools=[Tool(self.weather_client.get_weather_forecast)
                                  ],
                           system_prompt=AGENT_SYSTEM_PROMPT,
                           retries=3,
                           output_retries=3,
                           output_type=str | WeatherForecast # bigger models needed such as gpt-4.x or gpt-4o
                           )

    async def get_response(self, user_query: str) -> AsyncGenerator:
        """Gets a response from the chatbot for a given user query.

        Args:
            user_query (str): The user's query or question.

        Returns:
            Response from LLM
        """
        try:
            forecast_data = await self.agent.run(user_query)
            if forecast_data:
                if isinstance (forecast_data.output, WeatherForecast):
                    # if output_type is given
                    yield format_weather_summary(forecast_data.output)
                else:
                    # str response
                    yield forecast_data.output
            else:
                print("Could not retrieve weather forecast.")
        except Exception as e:
            print("Exception occurred during response generation. Error: {}".format(e))

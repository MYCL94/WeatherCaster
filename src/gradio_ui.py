import logging
import gradio as gr
from application.weather_caster import WeatherCaster
from configs.weather_questions import example_questions

logger = logging.getLogger(__name__)

class GradioWeatherUI:
    """Manages the Gradio web UI for WeatherCaster."""

    def __init__(self) -> None:
        """Initializes the GradioWeatherUI and the WeatherCaster agent."""
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.chatbot: WeatherCaster | None = None
        self._initialize_chatbot()

    def _initialize_chatbot(self) -> None:
        """Initializes the WeatherCaster agent."""
        try:
            self.logger.info("Initializing WeatherCaster for Gradio UI...")
            self.chatbot = WeatherCaster()
            self.logger.info("WeatherCaster initialized successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize WeatherCaster: {e}", exc_info=True)
            exit(1)

    async def _get_weather_response(self, user_query: str) -> str:
        """Async function to get weather response for the Gradio interface.
        It interacts with the initialized WeatherCaster agent.
        Args:
            user_query (str): The user's input query.
        Returns:
            str: The response from the WeatherCaster agent.
        """
        if self.chatbot is None:
            self.logger.error("WeatherCaster chatbot is not initialized in _get_weather_response.")
            return "Error: Chatbot is not available. Please check the application logs."

        if not user_query.strip():
            return "Please enter a query about the weather."

        try:
            async for response_obj in self.chatbot.get_response(user_query):
                return response_obj
            self.logger.warning(f"No response yielded by agent for query: '{user_query}'")
            return "No response received from the agent. This might indicate an issue."
        except Exception as e:
            self.logger.error(f"Error during agent interaction for query '{user_query}': {e}", exc_info=True)
            return f"An error occurred while processing your request: {str(e)}"

    def launch(self) -> None:
        """Sets up and launches the Gradio web UI."""
        if self.chatbot is None:
            self.logger.error("Gradio UI cannot be launched due to WeatherCaster initialization failure. Displaying error UI.")
            exit(1)

        llm_config = self.chatbot.llm_model

        iface = gr.Interface(
            fn=self._get_weather_response,
            inputs=gr.Textbox(
                lines=3,
                label="Weather Query",
                placeholder="Ask about the weather... e.g., 'What's the weather in London?' or 'Paris current weather' or 'Forecast for Berlin tomorrow'"
            ),
            outputs=gr.Textbox(label="WeatherCaster Response", lines=15),
            title="WeatherCaster 🌦️",
            description=(
                "Welcome to WeatherCaster! Ask for weather forecasts (current, hourly, daily).\n"
                + llm_config.description + "\n"
                + "Weather data provided by [OpenWeatherMap](https://openweathermap.org/)."
            ),
            flagging_mode="never",
            examples=example_questions,
            theme="soft"
        )

        self.logger.info("Launching WeatherCaster Gradio UI on http://127.0.0.1:7860 (or the next available port)...")
        if llm_config.is_direct:
            self.logger.info(f"Using LLM: {llm_config.model_name}")
        else:
            self.logger.info(f"Using local LLM: {llm_config.model_name} (via configured host/port)")
            self.logger.info("Ensure your local LLM server (e.g., Ollama) is running and the model is available.")
        iface.launch(share=False, server_name="0.0.0.0", server_port=7860, pwa=True)

def run_gradio_ui_sync_wrapper() -> None:
    """Synchronous wrapper to launch the Gradio UI.
    This function is used as an entry point in pyproject.toml's [project.scripts].
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ui = GradioWeatherUI()
    ui.launch()

if __name__ == "__main__":
    """ To run it directly with python src/gradio_ui.py during development"""
    run_gradio_ui_sync_wrapper()
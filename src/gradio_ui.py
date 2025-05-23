import gradio as gr
from application.weather_caster import WeatherCaster
from configs.weather_questions import example_questions

class GradioWeatherUI:
    """Manages the Gradio web UI for WeatherCaster."""

    def __init__(self) -> None:
        """Initializes the GradioWeatherUI and the WeatherCaster agent."""
        self.chatbot: WeatherCaster | None = None
        self._initialize_chatbot()

    def _initialize_chatbot(self) -> None:
        """Initializes the WeatherCaster agent."""
        try:
            print("Initializing WeatherCaster for Gradio UI...")
            self.chatbot = WeatherCaster()
            print("WeatherCaster initialized successfully.")
        except Exception as e:
            print(f"Critical Error: Failed to initialize WeatherCaster: {e}")
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
            exit(1)

        if not user_query.strip():
            return "Please enter a query about the weather."

        try:
            async for response_obj in self.chatbot.get_response(user_query):
                return response_obj
            return "No response received from the agent. This might indicate an issue."
        except Exception as e:
            print(f"Error during agent interaction: {e}")
            return f"An error occurred while processing your request: {str(e)}"

    def launch(self) -> None:
        """Sets up and launches the Gradio web UI."""
        if self.chatbot is None:
            print("Gradio UI cannot be launched due to WeatherCaster initialization failure.")
            gr.Interface(fn=lambda: "WeatherCaster failed to initialize. Check logs.", inputs=[], outputs="text").launch()
            return

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

        print("Launching WeatherCaster Gradio UI on http://127.0.0.1:7860 (or the next available port)...")
        if llm_config.is_direct:
            print(f"Using LLM: {llm_config.model_name}")
        else:
            print(f"Using local LLM: {llm_config.model_name} (via configured host/port)")
            print("Ensure your local LLM server (e.g., Ollama) is running and the model is available.")
        iface.launch(share=False, server_name="0.0.0.0", server_port=7860, pwa=True)

def run_gradio_ui_sync_wrapper() -> None:
    """Synchronous wrapper to launch the Gradio UI.
    This function is used as an entry point in pyproject.toml's [project.scripts].
    """
    ui = GradioWeatherUI()
    ui.launch()

if __name__ == "__main__":
    """ To run it directly with python src/gradio_ui.py during development"""
    run_gradio_ui_sync_wrapper()
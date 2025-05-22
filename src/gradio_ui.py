import gradio as gr
from application.weather_caster import WeatherCaster
from configs.config import env


# Ollama server (or other LLM provider) must be running with the specified model.
try:
    print("Initializing WeatherCaster for Gradio UI...")
    chatbot = WeatherCaster()
    print("WeatherCaster initialized successfully.")
except Exception as e:
    print(f"Critical Error: Failed to initialize WeatherCaster: {e}")
    print("The Gradio UI may not function correctly or will show an error message.")
    chatbot = None

async def get_weather_response_for_gradio(user_query: str) -> str:
    """Async function to get weather response for the Gradio interface.

    It interacts with the initialized WeatherCaster agent.

    Args:
        user_query (str): The user's input query.

    Returns:
        str: The response from the WeatherCaster agent.
    """
    if chatbot is None:
        return "Error: WeatherCaster agent could not be initialized. Please check the server logs."
    
    if not user_query.strip():
        return "Please enter a query about the weather."

    try:
        # yield response object containing the LLM's output
        async for response_obj in chatbot.get_response(user_query):
            if hasattr(response_obj, 'output'):
                return response_obj.output
            else:
                # Fallback if the response object structure is unexpected
                return "Received an unexpected response format from the agent."
        return "No response received from the agent. This might indicate an issue."
    except Exception as e:
        print(f"Error during agent interaction: {e}")
        return f"An error occurred while processing your request: {str(e)}"

def launch_gradio_interface() -> None:
    """Sets up and launches the Gradio web UI for WeatherCaster."""
    iface = gr.Interface(
        fn=get_weather_response_for_gradio,
        inputs=gr.Textbox(
            lines=3,
            label="Weather Query",
            placeholder="Ask about the weather... e.g., 'What's the weather in London?' or 'Paris current weather' or 'Forecast for Berlin tomorrow'"
        ),
        outputs=gr.Textbox(
            label="WeatherCaster Response", 
            lines=15,
        ),
        title="WeatherCaster 🌦️",
        description=(
            "Welcome to WeatherCaster! Ask for weather forecasts (current, hourly, daily).\n"
            f"Powered by LLM: [{env.MODEL_ID}](https://ollama.com/). Ensure your LLM server is running at {env.MODEL_HOST}:{env.MODEL_PORT}.\n"
            f"Weather data provided by [OpenWeatherMap](https://openweathermap.org/)."
        ),
        allow_flagging="never", # no data collection in current state
        examples=[
            ["What's the weather like in Palermo?"],
            ["Konya and Phuket"],
            ["Is it sunny in Madrid right now?"],
            ["Hourly forecast for Tokyo"],
            ["Weather in Rome tomorrow"],
            ["Daily forecast for Sydney for the next 3 days"]
        ],
        theme="soft" # other themes "default", "huggingface", "gradio/monokai"
    )
    
    print("Launching WeatherCaster Gradio UI on http://127.0.0.1:7860 (or the next available port)...")
    print(f"Using LLM: {env.MODEL_ID} from {env.MODEL_HOST}:{env.MODEL_PORT}")
    print("Ensure your LLM server (e.g., Ollama) is running and the model is available.")
    iface.launch()

def run_gradio_ui_sync_wrapper() -> None:
    """Synchronous wrapper to launch the Gradio UI.

    This function is used as an entry point in pyproject.toml's [project.scripts].
    """

    launch_gradio_interface()

if __name__ == "__main__":
    """ To run it directly with python src/gradio_ui.py during development"""
    run_gradio_ui_sync_wrapper()
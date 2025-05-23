import logging
from application.weather_caster import WeatherCaster

logger = logging.getLogger(__name__)

async def run_cli() -> None:
    """Runs the WeatherCaster Chatbot CLI."""

    logger.info("WeatherCaster Chatbot CLI")
    logger.info("Type 'quit' or 'exit' to stop.")

    # Initialize the chatbot
    # load .env and set up the agent.
    # Ensure Ollama server is running with the specified model.

    chatbot = WeatherCaster()

    while True:
        user_input = input("User Query: ")
        if user_input.lower() in ["quit", "exit"]:
            logger.info("Exiting WeatherCaster. Goodbye!")
            break

        if not user_input.strip():
            continue

        try:
            # Await the async generator and iterate over its results
            async for response in chatbot.get_response(user_input):
                logger.info(f"WeatherCaster: {response}")
        except Exception as e:
            logger.error(f"Error getting response from chatbot: {e}", exc_info=True)
            logger.info("WeatherCaster: An error occurred. Please try again.")

def run_cli_sync_wrapper() -> None:
    """Runs the WeatherCaster Chatbot CLI synchronously.
    
    Synchronous wrapper for the [project.scripts] entry point.
    """
    import asyncio
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_cli())

if __name__ == "__main__":
    """ To run it directly with python src/cli.py during development."""
    run_cli_sync_wrapper()
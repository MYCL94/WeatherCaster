from application.weather_caster import WeatherCaster

async def run_cli() -> None:
    """Runs the WeatherCaster Chatbot CLI."""

    print("WeatherCaster Chatbot CLI")
    print("Type 'quit' or 'exit' to stop.")

    # Initialize the chatbot
    # load .env and set up the agent.
    # Ensure Ollama server is running with the specified model.

    chatbot = WeatherCaster() 

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Exiting WeatherCaster. Goodbye!")
            break

        if not user_input.strip():
            continue

        # Await the async generator and iterate over its results
        async for response in chatbot.get_response(user_input):
            print(f"WeatherCaster: {response.output}")

def run_cli_sync_wrapper() -> None:
    """Runs the WeatherCaster Chatbot CLI synchronously.
    
    Synchronous wrapper for the [project.scripts] entry point.
    """
    import asyncio
    asyncio.run(run_cli())

if __name__ == "__main__":
    """ To run it directly with python src/cli.py during development."""
    run_cli_sync_wrapper()
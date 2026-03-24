import asyncio
from agentica import spawn
from dotenv import load_dotenv
import os

# Load environment variables (OPENROUTER_API_KEY)
load_dotenv()

async def main():
    # Setup a simple helper function for the agent
    def get_weather(location: str):
        return f"The weather in {location} is 22°C and sunny."

    # Spawn an agent
    # premise: The personality/role of the agent
    # model: The model to use (OpenRouter format e.g., 'openai/gpt-4o')
    # scope: Tools/functions the agent can call
    agent = await spawn(
        premise="You are a helpful assistant with access to weather tools.",
        model="google/gemini-2.0-flash-exp:free", # Change this to your preferred model
        scope={'get_weather': get_weather},
    )

    # Call the agent
    print("Calling agent...")
    result = await agent.call(
        str,
        "What's the weather like in Mumbai?",
    )

    print(f"\nAgent Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

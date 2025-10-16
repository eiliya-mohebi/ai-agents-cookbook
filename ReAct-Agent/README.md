# ReAct Agent with Structured Output

This project implements a flexible ReAct (Reasoning and Acting) agent that leverages `openai`, `instructor`, and `pydantic` to interact with user-defined tools and provide structured, reliable responses.

The agent operates in a `Thought -> Action -> Observation` loop, making it capable of complex, multi-step reasoning to answer user queries. By using `instructor` and `pydantic`, the agent ensures that all tool calls and final outputs are schema-aligned, dramatically reducing runtime errors and improving reliability.

## About The Project

This ReAct agent is designed to be a robust framework for building tool-augmented AI systems.

Key features include:

* **ReAct Logic**: Implements the `Thought -> Action -> Observation` loop for advanced reasoning.
* **Structured Data**: Uses `instructor` to extract Pydantic models directly from the OpenAI API, ensuring type safety.
* **Tool Integration**: A simple decorator (`@tool`) allows you to integrate any function as a tool for the agent.
* **Async Support**: Built with `asyncio` to handle asynchronous tools and API calls efficiently.
* **Error Handling**: Includes a graceful exit message if the agent cannot find a definitive answer after multiple attempts.

---

## Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* Python 3.7+
* An OpenAI API key

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/eiliya-mohebi/ai-agents-cookbook/
    cd React-Agent
    ```

2.  **Set up a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set your OpenAI API Key:**
    ```sh
    export OPENAI_API_KEY='your-api-key'
    ```

---

## Usage

Using the agent is straightforward. You can define your own tools and pass them to the `ReactAgent` instance.

Here's a simple example of how to define a tool and run the agent:

```python
import asyncio
from tool import tool
from react_agent import ReactAgent

# 1. Define a tool
@tool
def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Gets the current weather for a specified location.
    """
    return f"The weather in {location} is 25 degrees {unit}."

async def main():
    # 2. Initialize the agent with your tool(s)
    agent = ReactAgent(tools=[get_current_weather])

    # 3. Run the agent with a user query
    user_query = "What's the current temperature in Iran?"
    response = await agent.run(user_msg=user_query)
    
    print(f"Final Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
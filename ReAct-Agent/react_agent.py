import json
import openai
import instructor
from tool import Tool, tool, validate_arguments
from colorama import Fore
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union, Literal

REACT_SYSTEM_PROMPT = """
You operate by running a loop with the following steps: Thought, Action, Observation.
You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.

For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools / actions:

<tools>
%s
</tools>

Example session:

<question>What's the current temperature in Madrid?</question>

<tool_call>{"name": "get_current_weather","arguments": {"location": "Madrid", "unit": "celsius"}, "id": 0}</tool_call>

You will be called again with this:

<observation>{0: {"temperature": 25, "unit": "celsius"}}</observation>

You then output:

<response>The current temperature in Madrid is 25 degrees Celsius</response>

Additional constraints:

- If the user asks you something unrelated to any of the tools above, answer freely enclosing your answer with <response></response> tags.
"""


def build_prompt_structure(prompt: str, role: str, tag: str = "") -> dict:
    """
    Builds a structured prompt that includes the role and content.

    Args:
        prompt (str): The actual content of the prompt.
        role (str): The role of the speaker (e.g., user, assistant).

    Returns:
        dict: A dictionary representing the structured prompt.
    """
    if tag:
        prompt = f"<{tag}>{prompt}</{tag}>"
    return {"role": role, "content": prompt}


class RagToolArgs(BaseModel):
    """Defines the strict arguments for the rag_tool."""

    model_config = ConfigDict(extra="forbid")

    rewritten_query: str


class RagToolCall(BaseModel):
    """A structured model for a call to the 'rag_tool'."""

    name: Literal["rag_tool"]
    arguments: RagToolArgs
    id: int


class AgentStep(BaseModel):
    """
    The model representing the agent's full turn. The schema for this model
    and its nested models is now strict, preventing API validation errors.
    """

    model_config = ConfigDict(extra="forbid")

    thought: str = Field(
        ...,
        description="The agent's reasoning, analysis, and plan for the next action.",
    )
    tool_calls: Optional[List[Union[RagToolCall]]] = Field(
        None,
        description="A list of tool calls to execute. Use this when in the 'Retriever' role.",
    )
    final_response: Optional[str] = Field(
        None,
        description="The final answer. Use this only when in the 'Generator' role.",
    )


class ReactAgent:
    """
    A class that represents an agent using the ReAct logic that interacts with tools to process
    user inputs, make decisions, and execute tool calls. The agent can run interactive sessions,
    collect tool signatures, and process multiple tool calls in a given round of interaction.

    Attributes:
        client (openai.AsyncOpenAI): The OpenAI client patched by the instructor library.
        model (str): The name of the model used for generating responses.
        tools (list[Tool]): A list of Tool instances available for execution.
        tools_dict (dict): A dictionary mapping tool names to their corresponding Tool instances.
    """

    def __init__(
        self,
        tools: Tool | list[Tool],
        model: str = "gpt-4o-mini",
        custom_prompt: str = None,
    ) -> None:
        self.client = instructor.patch(openai.AsyncOpenAI())
        self.model = model
        self.system_prompt = custom_prompt or REACT_SYSTEM_PROMPT
        self.tools = tools if isinstance(tools, list) else [tools]
        self.tools_dict = {tool.name: tool for tool in self.tools}
        self.tools_list = [json.loads(tool_obj.fn_signature) for tool_obj in self.tools]
        self.meta_data = {}

    def add_tool_signatures(self) -> str:
        """
        Collects the function signatures of all available tools.

        Returns:
            str: A concatenated string of all tool function signatures in JSON format.
        """
        return "".join([tool.fn_signature for tool in self.tools])

    async def create_completion(
        self, messages: list, response_model: BaseModel, **kwargs
    ) -> BaseModel:
        """
        Creates a completion using the OpenAI API with instructor for structured output.

        Args:
            messages (list): A list of message dictionaries for the chat completion.
            response_model (BaseModel): The Pydantic model to structure the response.
            **kwargs: Additional keyword arguments to pass to the API.

        Returns:
            BaseModel: An instance of the response_model populated with the API response.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_model=response_model,
                **kwargs,
            )
            return response
        except Exception as e:
            print(Fore.RED + f"An error occurred during OpenAI API call: {e}")
            raise

    async def process_tool_calls(self, tool_calls_content: list[dict]) -> dict:
        """
        Processes each tool call, validates arguments, executes the tools, and collects results.

        Args:
            tool_calls_content (list): List of dictionaries, each representing a tool call.

        Returns:
            dict: A dictionary where keys are tool call IDs and values are the results from the tools.
        """
        observations = {}
        for tool_call_dict in tool_calls_content:
            tool_name = tool_call_dict["name"]
            tool = self.tools_dict[tool_name]

            print(Fore.GREEN + f"\nUsing Tool: {tool_name}")

            # Validate and execute the tool call
            validated_tool_call: dict = validate_arguments(
                tool_call_dict, json.loads(tool.fn_signature)
            )
            print(Fore.GREEN + f"\nTool call dict: \n{validated_tool_call}")
            if self.meta_data:
                validated_tool_call["arguments"].update(self.meta_data)

            if tool.is_async:
                result = await tool.run(**validated_tool_call["arguments"])
            else:
                result = tool.run(**validated_tool_call["arguments"])

            print(Fore.GREEN + f"\nTool result: \n{result}")

            # Store the result using the tool call ID
            observations[validated_tool_call["id"]] = result

        return observations

    async def run(self, user_msg: str, max_rounds: int = 10, func_meta_data={}) -> str:
        """
        Executes a user interaction session, where the agent processes user input, generates responses,
        handles tool calls, and updates chat history until a final response is ready or the maximum
        number of rounds is reached.

        Args:
            user_msg (str): The user's input message to start the interaction.
            max_rounds (int, optional): Maximum number of interaction rounds. Default is 10.
            func_meta_data (dict, optional): Metadata to be passed to tool functions.

        Returns:
            str: The final response generated by the agent.
        """
        self.meta_data = func_meta_data
        final_thought = ""
        try:
            user_prompt = build_prompt_structure(
                prompt=user_msg, role="user", tag="question"
            )

            chat_history = []
            if self.tools:
                self.system_prompt = (
                    "\n" + self.system_prompt % self.add_tool_signatures()
                )
                sys_prompt = build_prompt_structure(
                    prompt=self.system_prompt, role="system"
                )
                chat_history = [sys_prompt, user_prompt]

                for i in range(max_rounds):
                    print(Fore.CYAN + f"\n--- Agent Round {i + 1} ---")
                    completion: AgentStep = await self.create_completion(
                        messages=chat_history,
                        response_model=AgentStep,
                        **self.meta_data,
                    )
                    print(Fore.MAGENTA + f"\nThought: {completion.thought}")
                    assistant_turn = {
                        "role": "assistant",
                        "content": completion.model_dump_json(indent=2),
                    }
                    chat_history.append(assistant_turn)

                    # --- SCENARIO 1: Agent provides the final answer ---
                    if completion.final_response:
                        print(Fore.YELLOW + "\nAgent has provided the final answer.")
                        return completion.final_response

                    # --- SCENARIO 2: Agent calls tools ---
                    if completion.tool_calls:
                        # Convert Pydantic models to dicts for processing
                        tool_calls_as_dicts = [
                            tc.model_dump() for tc in completion.tool_calls
                        ]

                        observations = await self.process_tool_calls(
                            tool_calls_as_dicts
                        )

                        print(Fore.BLUE + f"\nObservations: {observations}")

                        context_texts = [str(v) for v in observations.values()]

                        formatted_observation = "\n\n".join(context_texts)

                        observation_prompt = {
                            "role": "user",
                            "content": f"<observation>{formatted_observation}</observation>",
                        }
                        chat_history.append(observation_prompt)
                    final_thought = completion.thought
        except Exception as e:
            print(e)
            final_thought = "خطا"
        graceful_exit_message = f"""
                متاسفانه پس از چندین تلاش، نتوانستم پاسخ دقیقی برای سوال شما پیدا کنم.

                آخرین مرحله فکری من این بود:
                -----------------------------------
                {final_thought}
                -----------------------------------

                می‌توانید سوال خود را به شکل دیگری مطرح کنید؟
                """
        return graceful_exit_message

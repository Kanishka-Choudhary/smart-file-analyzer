# agents/summarizer_agent.py

import autogen
import os
from dotenv import load_dotenv

load_dotenv()

# Load your API key
api_key = os.getenv("OPENAI_API_KEY")

config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": api_key
    }
]

# Build an assistant agent
llm_config = {
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0.5,
}

assistant = autogen.AssistantAgent(
    name="SummarizerAgent",
    llm_config=llm_config,
)

# Simple summarization function
def summarize_entity(entity):
    name = entity["name"]
    if entity["entity_type"] == "class":
        base = ", ".join(entity["base_classes"]) if entity["base_classes"] else "no base class"
        prompt = f"""Summarize the following class for documentation purposes:

Class Name: {name}
Base Classes: {base}
Methods:
"""
        for m in entity["methods"]:
            prompt += f"- {m['name']}({', '.join(m['parameters'])})\n"

    else:
        prompt = f"""Summarize the purpose of the following function:\nFunction: {name}({', '.join(entity['parameters'])})"""

    user_proxy = autogen.UserProxyAgent(
        name="UserProxy",
        code_execution_config=False,
    )

    user_proxy.initiate_chat(
        assistant,
        message=prompt,
    )

    return user_proxy.last_message()["content"]

# test_connection.py — AutoGen 0.7.x + Groq (FIXED)

import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

async def test_connection():

    # ✅ LLM Client — Groq with REQUIRED model_info
    groq_client = OpenAIChatCompletionClient(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",

        # 🔥 FIX: Add model_info (MANDATORY for non-OpenAI models)
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown"
        }
    )

    # ✅ Assistant Agent
    assistant = AssistantAgent(
        name="QA_Assistant",
        model_client=groq_client,
        system_message="You are a helpful QA Engineering assistant."
    )

    # ✅ Termination condition
    termination = TextMentionTermination("TERMINATE")

    # ✅ Team setup
    team = RoundRobinGroupChat(
        participants=[assistant],
        termination_condition=termination
    )

    # ✅ Run task
    result = await team.run(
        task="Say exactly this and nothing else: CONNECTION SUCCESSFUL — AutoGen + Groq is working. Then say TERMINATE"
    )

    # ✅ Print response
    for message in result.messages:
        print(f"\n[{message.source}]: {message.content}")


if __name__ == "__main__":
    asyncio.run(test_connection())
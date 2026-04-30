import sys, asyncio
sys.path.append('.')
from agents.script_outline_agent import (
    build_single_prompt, load_test_cases, SYSTEM_PROMPT
)
from pathlib import Path
from config.llm_config import get_client
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

async def test():
    csv_path = Path('outputs/test_cases/US_001_poc_test_cases.csv')
    tcs      = load_test_cases(csv_path)
    tc       = tcs[0]
    prompt   = build_single_prompt(
        tc,
        'https://opensource-demo.orangehrmlive.com'
        '/web/index.php/auth/login'
    )

    print("=== PROMPT SENT ===")
    print(prompt)
    print("\n=== RAW RESPONSE ===")

    client = get_client('groq')
    agent  = AssistantAgent(
        name="Test",
        model_client=client,
        system_message=SYSTEM_PROMPT
    )
    team = RoundRobinGroupChat(
        [agent],
        termination_condition=TextMentionTermination('TERMINATE'),
        max_turns=2
    )
    result = await team.run(task=prompt)
    for msg in result.messages:
        if msg.source != 'user':
            print(msg.content)
            print(f"\n=== CHAR 400-420 ===")
            print(repr(msg.content[395:425]))

asyncio.run(test())
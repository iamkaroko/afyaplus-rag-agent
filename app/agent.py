from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.tools import (
    calculate_medication_volume,
    search_afyaplus_knowledge,
)


SYSTEM_PROMPT = """
You are the AfyaPlus insurance verification and clinical
routing assistant.

You help users understand AfyaPlus insurance policies,
clinical routing guidelines, and medication calculations.

Rules:

1. Use the AfyaPlus knowledge tool for questions about
   insurance policies, coverage, clinical routing, or internal
   medication guidelines.

2. Do not invent AfyaPlus policies or clinical guidance.

3. If the knowledge tool cannot find sufficiently relevant
   information, clearly state that the available AfyaPlus
   knowledge does not contain enough information.

4. Use the medication calculation tool whenever medication
   volume arithmetic is required.

5. Never guess missing medication doses or concentrations.
   Ask the user for the missing information.

6. Do not claim that a medication calculation is a medical
   prescription or treatment recommendation.

7. Keep answers concise and grounded in tool results.
"""


def create_afyaplus_agent():
    """
    Create the AfyaPlus tool-using LangChain agent.

    Returns:
        A configured LangChain agent capable of using
        AfyaPlus knowledge retrieval and medication
        calculation tools.
    """
    model = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
    )

    tools = [
        search_afyaplus_knowledge,
        calculate_medication_volume,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.tools import (
    calculate_medication_volume,
    search_afyaplus_knowledge,
)
from app.memory import ConversationMemory



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

8. Only answer questions related to AfyaPlus insurance,
   clinical routing, or supported medication calculations.

9. If a question is outside the AfyaPlus domain, politely
   explain that it is outside the scope of this assistant.

10. Never use your general model knowledge as a substitute
    for missing AfyaPlus policy or clinical information.
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

def run_agent(
    agent,
    memory: ConversationMemory,
    user_message: str,
) -> str:
    """
    Run one conversational turn through the AfyaPlus agent.

    The existing conversation history is supplied to the agent,
    and the new user and assistant messages are persisted in
    memory after the turn.

    Args:
        agent:
            The configured AfyaPlus LangChain agent.
        memory:
            Conversation memory for the current session.
        user_message:
            The current user message.

    Returns:
        The assistant's final response.
    """
    if not user_message.strip():
        raise ValueError("User message cannot be empty.")

    messages = memory.get_messages()

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    result = agent.invoke(
        {
            "messages": messages,
        }
    )

    final_message = result["messages"][-1]
    response = str(final_message.content)

    memory.add_user_message(user_message)
    memory.add_ai_message(response)

    return response
from app.agent import (
    create_afyaplus_agent,
    run_agent,
)
from app.memory import ConversationMemory


def main() -> None:
    """
    Run a manual multi-turn test of the AfyaPlus agent.

    This verifies that the agent can use conversation
    history to understand follow-up questions.
    """
    agent = create_afyaplus_agent()
    memory = ConversationMemory()

    questions = [
        "What is the outpatient MRI co-payment?",
        "Does it require prior authorisation?",
    ]

    for question in questions:
        print("\n" + "=" * 80)
        print(f"USER: {question}")
        print("=" * 80)

        response = run_agent(
            agent=agent,
            memory=memory,
            user_message=question,
        )

        print(f"ASSISTANT: {response}")

    print("\nConversation messages stored:")
    print(len(memory.get_messages()))


if __name__ == "__main__":
    main()
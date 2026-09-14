from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

from app.memory import ConversationMemory


def test_memory_starts_empty():
    memory = ConversationMemory()

    assert memory.get_messages() == []


def test_adds_user_message():
    memory = ConversationMemory()

    memory.add_user_message(
        "What is the MRI co-payment?"
    )

    messages = memory.get_messages()

    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert (
        messages[0].content
        == "What is the MRI co-payment?"
    )


def test_adds_ai_message():
    memory = ConversationMemory()

    memory.add_ai_message(
        "The outpatient MRI co-payment is KES 2,000."
    )

    messages = memory.get_messages()

    assert len(messages) == 1
    assert isinstance(messages[0], AIMessage)


def test_preserves_conversation_order():
    memory = ConversationMemory()

    memory.add_user_message(
        "What is the MRI co-payment?"
    )
    memory.add_ai_message(
        "The outpatient MRI co-payment is KES 2,000."
    )
    memory.add_user_message(
        "Does it require authorisation?"
    )

    messages = memory.get_messages()

    assert len(messages) == 3
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert isinstance(messages[2], HumanMessage)


def test_clear_removes_messages():
    memory = ConversationMemory()

    memory.add_user_message("Hello")
    memory.add_ai_message("Hello")

    memory.clear()

    assert memory.get_messages() == []
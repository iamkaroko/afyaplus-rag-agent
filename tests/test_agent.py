from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from app.agent import run_agent
from app.memory import ConversationMemory


def test_run_agent_stores_conversation():
    """
    Verify that a completed agent turn stores both the
    user message and assistant response in memory.
    """
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content=(
                    "The outpatient MRI co-payment "
                    "is KES 2,000."
                )
            )
        ]
    }

    memory = ConversationMemory()

    response = run_agent(
        agent=agent,
        memory=memory,
        user_message=(
            "What is the outpatient MRI co-payment?"
        ),
    )

    messages = memory.get_messages()

    assert response == (
        "The outpatient MRI co-payment is KES 2,000."
    )

    assert len(messages) == 2

    assert messages[0].content == (
        "What is the outpatient MRI co-payment?"
    )

    assert messages[1].content == response


def test_run_agent_sends_existing_history():
    """
    Verify that previous conversation messages are supplied
    to the agent together with the current user message.
    """
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content=(
                    "Yes, outpatient MRI scans require "
                    "prior authorisation."
                )
            )
        ]
    }

    memory = ConversationMemory()

    memory.add_user_message(
        "What is the outpatient MRI co-payment?"
    )

    memory.add_ai_message(
        "The outpatient MRI co-payment is KES 2,000."
    )

    run_agent(
        agent=agent,
        memory=memory,
        user_message=(
            "Does it require prior authorisation?"
        ),
    )

    invocation = agent.invoke.call_args.args[0]
    sent_messages = invocation["messages"]

    assert len(sent_messages) == 3

    assert sent_messages[0].content == (
        "What is the outpatient MRI co-payment?"
    )

    assert sent_messages[1].content == (
        "The outpatient MRI co-payment is KES 2,000."
    )

    assert sent_messages[2]["content"] == (
        "Does it require prior authorisation?"
    )


def test_run_agent_appends_new_turn_to_existing_history():
    """
    Verify that a new conversation turn is appended without
    replacing the existing conversation history.
    """
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content=(
                    "Yes, outpatient MRI scans require "
                    "prior authorisation."
                )
            )
        ]
    }

    memory = ConversationMemory()

    memory.add_user_message(
        "What is the outpatient MRI co-payment?"
    )

    memory.add_ai_message(
        "The outpatient MRI co-payment is KES 2,000."
    )

    run_agent(
        agent=agent,
        memory=memory,
        user_message=(
            "Does it require prior authorisation?"
        ),
    )

    messages = memory.get_messages()

    assert len(messages) == 4

    assert messages[0].content == (
        "What is the outpatient MRI co-payment?"
    )

    assert messages[1].content == (
        "The outpatient MRI co-payment is KES 2,000."
    )

    assert messages[2].content == (
        "Does it require prior authorisation?"
    )

    assert messages[3].content == (
        "Yes, outpatient MRI scans require "
        "prior authorisation."
    )


def test_run_agent_rejects_empty_message():
    """
    Verify that empty user messages are rejected before
    invoking the language model.
    """
    agent = MagicMock()
    memory = ConversationMemory()

    with pytest.raises(
        ValueError,
        match="User message cannot be empty",
    ):
        run_agent(
            agent=agent,
            memory=memory,
            user_message="   ",
        )

    agent.invoke.assert_not_called()
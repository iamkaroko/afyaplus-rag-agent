from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from app.service import AfyaPlusService


def test_masks_pii_before_agent_invocation():
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

    service = AfyaPlusService(agent=agent)

    service.process_message(
        "My phone is 0712345678. "
        "What is the outpatient MRI co-payment?"
    )

    invocation = agent.invoke.call_args.args[0]
    sent_messages = invocation["messages"]

    user_message = sent_messages[-1]["content"]

    assert "0712345678" not in user_message
    assert "[PHONE_1]" in user_message


def test_masks_email_before_agent_invocation():
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content="Your request has been received."
            )
        ]
    }

    service = AfyaPlusService(agent=agent)

    service.process_message(
        "My email is ken@example.com."
    )

    invocation = agent.invoke.call_args.args[0]
    sent_messages = invocation["messages"]

    user_message = sent_messages[-1]["content"]

    assert "ken@example.com" not in user_message
    assert "[EMAIL_1]" in user_message


def test_demasks_pii_in_final_response():
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content=(
                    "We have recorded [PHONE_1]."
                )
            )
        ]
    }

    service = AfyaPlusService(agent=agent)

    response = service.process_message(
        "My phone is 0712345678."
    )

    assert "[PHONE_1]" not in response
    assert "0712345678" in response


def test_memory_contains_only_masked_pii():
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content=(
                    "Your phone [PHONE_1] "
                    "has been recorded."
                )
            )
        ]
    }

    service = AfyaPlusService(agent=agent)

    service.process_message(
        "My phone is 0712345678."
    )

    messages = service.memory.get_messages()

    combined_content = " ".join(
        str(message.content)
        for message in messages
    )

    assert "0712345678" not in combined_content
    assert "[PHONE_1]" in combined_content


def test_multiple_turns_use_unique_placeholders():
    agent = MagicMock()

    agent.invoke.side_effect = [
        {
            "messages": [
                AIMessage(
                    content="Recorded [PHONE_1]."
                )
            ]
        },
        {
            "messages": [
                AIMessage(
                    content="Recorded [PHONE_2]."
                )
            ]
        },
    ]

    service = AfyaPlusService(agent=agent)

    service.process_message(
        "My phone is 0711111111."
    )

    service.process_message(
        "My other phone is 0722222222."
    )

    messages = service.memory.get_messages()

    combined_content = " ".join(
        str(message.content)
        for message in messages
    )

    assert "[PHONE_1]" in combined_content
    assert "[PHONE_2]" in combined_content

    assert "0711111111" not in combined_content
    assert "0722222222" not in combined_content


def test_rejects_empty_message():
    agent = MagicMock()

    service = AfyaPlusService(agent=agent)

    with pytest.raises(
        ValueError,
        match="User message cannot be empty",
    ):
        service.process_message("   ")

    agent.invoke.assert_not_called()


def test_clear_session_removes_memory_and_pii_mapping():
    agent = MagicMock()

    agent.invoke.return_value = {
        "messages": [
            AIMessage(
                content="Recorded [PHONE_1]."
            )
        ]
    }

    service = AfyaPlusService(agent=agent)

    service.process_message(
        "My phone is 0712345678."
    )

    assert service.memory.get_messages()
    assert service.privacy.get_mapping()

    service.clear_session()

    assert service.memory.get_messages() == []
    assert service.privacy.get_mapping() == {}
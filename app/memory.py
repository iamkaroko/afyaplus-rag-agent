from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)


class ConversationMemory:
    """
    Maintain message history for an AfyaPlus conversation.
    """

    def __init__(self) -> None:
        self._messages: list[BaseMessage] = []

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the conversation.
        """
        self._messages.append(
            HumanMessage(content=content)
        )

    def add_ai_message(self, content: str) -> None:
        """
        Add an assistant message to the conversation.
        """
        self._messages.append(
            AIMessage(content=content)
        )

    def get_messages(self) -> list[BaseMessage]:
        """
        Return a copy of the conversation history.
        """
        return self._messages.copy()

    def clear(self) -> None:
        """
        Remove all messages from the conversation.
        """
        self._messages.clear()
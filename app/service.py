from typing import Any

from app.agent import create_afyaplus_agent, run_agent
from app.memory import ConversationMemory
from app.privacy import PrivacyContext


class AfyaPlusService:
    """
    Coordinate privacy masking, conversation memory,
    agent execution, and safe output de-masking.
    """

    def __init__(self, agent: Any | None = None) -> None:
        self.agent = agent or create_afyaplus_agent()
        self.memory = ConversationMemory()
        self.privacy = PrivacyContext()

    def process_message(self, user_message: str) -> str:
        """
        Process one user message through the complete
        privacy-safe AfyaPlus pipeline.

        Raw PII is masked before the message reaches the
        language model. Only the final response is de-masked
        immediately before being returned to the caller.

        Args:
            user_message:
                Raw user input, which may contain PII.

        Returns:
            The final user-facing response.

        Raises:
            ValueError:
                If the user message is empty.
        """
        if not user_message.strip():
            raise ValueError(
                "User message cannot be empty."
            )

        masked_message = self.privacy.mask(
            user_message
        )

        masked_response = run_agent(
            agent=self.agent,
            memory=self.memory,
            user_message=masked_message,
        )

        return self.privacy.unmask(
            masked_response
        )

    def clear_session(self) -> None:
        """
        Clear conversation history and PII mappings.
        """
        self.memory.clear()
        self.privacy = PrivacyContext()
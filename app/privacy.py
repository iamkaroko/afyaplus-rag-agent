import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+254|254|0)[\s-]?[17]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)"
)


class PrivacyContext:
    """
    Maintain PII placeholders and mappings for one conversation.

    Actual PII remains outside the language-model conversation.
    """

    def __init__(self) -> None:
        self._pii_mapping: dict[str, str] = {}
        self._email_counter = 0
        self._phone_counter = 0

    def mask(self, text: str) -> str:
        """
        Replace supported PII with session-unique placeholders.

        Args:
            text:
                Raw user-provided text.

        Returns:
            Text containing placeholders instead of PII.
        """

        def replace_email(match: re.Match) -> str:
            self._email_counter += 1

            placeholder = (
                f"[EMAIL_{self._email_counter}]"
            )

            self._pii_mapping[placeholder] = (
                match.group(0)
            )

            return placeholder

        def replace_phone(match: re.Match) -> str:
            self._phone_counter += 1

            placeholder = (
                f"[PHONE_{self._phone_counter}]"
            )

            self._pii_mapping[placeholder] = (
                match.group(0)
            )

            return placeholder

        masked_text = EMAIL_PATTERN.sub(
            replace_email,
            text,
        )

        masked_text = PHONE_PATTERN.sub(
            replace_phone,
            masked_text,
        )

        return masked_text

    def unmask(self, text: str) -> str:
        """
        Restore known PII placeholders to original values.
        """
        unmasked_text = text

        for placeholder, original_value in (
            self._pii_mapping.items()
        ):
            unmasked_text = unmasked_text.replace(
                placeholder,
                original_value,
            )

        return unmasked_text

    def get_mapping(self) -> dict[str, str]:
        """
        Return a copy of the current PII mapping.
        """
        return self._pii_mapping.copy()


def mask_pii(
    text: str,
) -> tuple[str, dict[str, str]]:
    """
    Mask supported PII in a single standalone message.

    This function is retained for backwards compatibility
    and simple one-off masking operations.
    """
    context = PrivacyContext()

    masked_text = context.mask(text)

    return masked_text, context.get_mapping()


def unmask_pii(
    text: str,
    pii_mapping: dict[str, str],
) -> str:
    """
    Restore placeholders using a supplied PII mapping.
    """
    unmasked_text = text

    for placeholder, original_value in (
        pii_mapping.items()
    ):
        unmasked_text = unmasked_text.replace(
            placeholder,
            original_value,
        )

    return unmasked_text
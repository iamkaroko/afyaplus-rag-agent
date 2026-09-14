import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+254|254|0)[\s-]?[17]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)"
)


def mask_pii(text: str) -> tuple[str, dict[str, str]]:
    """
    Mask email addresses and Kenyan phone numbers in user input.

    Args:
        text: Raw user input that may contain PII.

    Returns:
        A tuple containing the masked text and a mapping of
        placeholders to their original values.
    """
    pii_mapping: dict[str, str] = {}

    def replace_email(match: re.Match) -> str:
        placeholder = f"[EMAIL_{len([k for k in pii_mapping if k.startswith('[EMAIL_')]) + 1}]"
        pii_mapping[placeholder] = match.group(0)
        return placeholder

    def replace_phone(match: re.Match) -> str:
        placeholder = f"[PHONE_{len([k for k in pii_mapping if k.startswith('[PHONE_')]) + 1}]"
        pii_mapping[placeholder] = match.group(0)
        return placeholder

    masked_text = EMAIL_PATTERN.sub(replace_email, text)
    masked_text = PHONE_PATTERN.sub(replace_phone, masked_text)

    return masked_text, pii_mapping

def unmask_pii(text: str, pii_mapping: dict[str, str]) -> str:
    """
    Restore masked PII placeholders to their original values.

    Args:
        text: Text containing PII placeholders.
        pii_mapping: Mapping between placeholders and original PII.

    Returns:
        Text with the original PII restored.
    """
    unmasked_text = text

    for placeholder, original_value in pii_mapping.items():
        unmasked_text = unmasked_text.replace(
            placeholder,
            original_value,
        )

    return unmasked_text
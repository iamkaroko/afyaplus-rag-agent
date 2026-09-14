from app.privacy import mask_pii, unmask_pii


def test_masks_email():
    text = "My email is ken@example.com."

    masked, mapping = mask_pii(text)

    assert "ken@example.com" not in masked
    assert "[EMAIL_1]" in masked
    assert mapping["[EMAIL_1]"] == "ken@example.com"


def test_masks_local_kenyan_phone():
    text = "Call me on 0712345678."

    masked, mapping = mask_pii(text)

    assert "0712345678" not in masked
    assert "[PHONE_1]" in masked
    assert mapping["[PHONE_1]"] == "0712345678"


def test_masks_international_kenyan_phone():
    text = "My number is +254712345678."

    masked, mapping = mask_pii(text)

    assert "+254712345678" not in masked
    assert "[PHONE_1]" in masked


def test_masks_phone_with_spaces():
    text = "Call +254 712 345 678 for assistance."

    masked, _ = mask_pii(text)

    assert "+254 712 345 678" not in masked
    assert "[PHONE_1]" in masked


def test_masks_multiple_pii_values():
    text = (
        "Email ken@example.com or billing@example.com. "
        "Call 0712345678."
    )

    masked, mapping = mask_pii(text)

    assert "[EMAIL_1]" in masked
    assert "[EMAIL_2]" in masked
    assert "[PHONE_1]" in masked
    assert len(mapping) == 3


def test_unmasks_pii():
    original = (
        "My email is ken@example.com "
        "and my phone is 0712345678."
    )

    masked, mapping = mask_pii(original)
    restored = unmask_pii(masked, mapping)

    assert restored == original
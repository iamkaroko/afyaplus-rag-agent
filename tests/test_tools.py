import pytest

from app.tools import (
    calculate_medication_volume,
    search_afyaplus_knowledge,
)


def test_calculates_medication_volume():
    result = calculate_medication_volume.invoke(
        {
            "prescribed_dose_mg": 500,
            "concentration_mg_per_ml": 250,
        }
    )

    assert result == "Required medication volume: 2.00 mL"


def test_calculates_decimal_volume():
    result = calculate_medication_volume.invoke(
        {
            "prescribed_dose_mg": 125,
            "concentration_mg_per_ml": 50,
        }
    )

    assert result == "Required medication volume: 2.50 mL"


def test_rejects_zero_dose():
    with pytest.raises(
        ValueError,
        match="Prescribed dose must be greater than zero",
    ):
        calculate_medication_volume.invoke(
            {
                "prescribed_dose_mg": 0,
                "concentration_mg_per_ml": 250,
            }
        )


def test_rejects_negative_dose():
    with pytest.raises(
        ValueError,
        match="Prescribed dose must be greater than zero",
    ):
        calculate_medication_volume.invoke(
            {
                "prescribed_dose_mg": -500,
                "concentration_mg_per_ml": 250,
            }
        )


def test_rejects_zero_concentration():
    with pytest.raises(
        ValueError,
        match="Medication concentration must be greater than zero",
    ):
        calculate_medication_volume.invoke(
            {
                "prescribed_dose_mg": 500,
                "concentration_mg_per_ml": 0,
            }
        )

def test_searches_afyaplus_knowledge():
    result = search_afyaplus_knowledge.invoke(
        {
            "query":
                "Does an emergency MRI require prior authorisation?"
        }
    )

    assert "insurance_policy.md" in result
    assert "MRI" in result
    assert "authorisation" in result


def test_knowledge_search_rejects_irrelevant_question():
    result = search_afyaplus_knowledge.invoke(
        {
            "query": "Who won the FIFA World Cup in 2010?"
        }
    )

    assert (
        "No sufficiently relevant AfyaPlus knowledge"
        in result
    )
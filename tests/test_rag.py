import pytest

from app.rag import retrieve_context


def test_rejects_empty_query():
    """
    Empty retrieval queries should be rejected.
    """
    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        retrieve_context("")


def test_rejects_whitespace_only_query():
    """
    Queries containing only whitespace should be rejected.
    """
    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        retrieve_context("   ")


def test_retrieves_mri_policy():
    """
    MRI questions should retrieve relevant insurance
    policy information.
    """
    results = retrieve_context(
        "Does an emergency MRI require prior authorisation?"
    )

    assert results

    combined_text = " ".join(
        str(result["text"])
        for result in results
    ).lower()

    assert "mri" in combined_text
    assert "authorisation" in combined_text


def test_retrieval_contains_source_metadata():
    """
    Retrieved chunks should include metadata so answers
    can eventually provide source attribution.
    """
    results = retrieve_context(
        "What is the outpatient MRI co-payment?"
    )

    assert results

    for result in results:
        assert "metadata" in result
        assert result["metadata"]


def test_irrelevant_query_returns_no_context():
    """
    Questions unrelated to AfyaPlus should not be accepted
    as grounded knowledge.
    """
    results = retrieve_context(
        "Who won the FIFA World Cup in 2010?"
    )

    assert results == []
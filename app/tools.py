from langchain_core.tools import tool

from app.rag import retrieve_context


@tool
def calculate_medication_volume(
    prescribed_dose_mg: float,
    concentration_mg_per_ml: float,
) -> str:
    """
    Calculate the medication volume required for a prescribed dose.

    Use this tool when both the prescribed dose in milligrams
    and medication concentration in milligrams per millilitre
    are known.

    Args:
        prescribed_dose_mg:
            The prescribed medication dose in milligrams.
        concentration_mg_per_ml:
            The medication concentration in milligrams
            per millilitre.

    Returns:
        A formatted medication volume in millilitres.

    Raises:
        ValueError:
            If the dose or concentration is zero or negative.
    """
    try:
        if prescribed_dose_mg <= 0:
            raise ValueError(
                "Prescribed dose must be greater than zero."
            )

        if concentration_mg_per_ml <= 0:
            raise ValueError(
                "Medication concentration must be greater than zero."
            )

        volume_ml = (
            prescribed_dose_mg / concentration_mg_per_ml
        )

        return (
            f"Required medication volume: "
            f"{volume_ml:.2f} mL"
        )

    except TypeError as exc:
        raise ValueError(
            "Dose and concentration must be numeric values."
        ) from exc


@tool
def search_afyaplus_knowledge(query: str) -> str:
    """
    Search the AfyaPlus knowledge base for insurance,
    clinical-routing, and medication-guideline information.

    Use this tool when answering questions that require
    information from AfyaPlus policies or internal guidelines.

    Args:
        query:
            The question or topic to search for.

    Returns:
        Relevant grounded context with source information,
        or a message explaining that no sufficiently relevant
        context was found.
    """
    results = retrieve_context(query)

    if not results:
        return (
            "No sufficiently relevant AfyaPlus knowledge "
            "was found for this question."
        )

    formatted_results: list[str] = []

    for result in results:
        metadata = result["metadata"]

        source = metadata.get(
            "file_name",
            "unknown source",
        )

        formatted_results.append(
            (
                f"Source: {source}\n"
                f"Similarity score: {result['score']:.4f}\n"
                f"Context:\n{result['text']}"
            )
        )

    return "\n\n---\n\n".join(formatted_results)
from app.rag import retrieve_context


def main() -> None:
    queries = [
        "Does an emergency MRI require prior authorisation?",
        "What is the outpatient MRI co-payment?",
        "When should a patient with severe chest pain go to emergency care?",
        "How do I calculate medication volume?",
        "Who won the FIFA World Cup in 2010?",
        "What is the capital of France?",
    ]

    for query in queries:
        print("\n" + "=" * 80)
        print(f"Question: {query}")
        print("=" * 80)

        results = retrieve_context(query)

        if not results:
            print("No context found.")
            continue

        for position, result in enumerate(results, start=1):
            metadata = result["metadata"]

            print(
                f"{position}. "
                f"{metadata.get('file_name', 'unknown')} "
                f"| score={result['score']:.4f}"
            )


if __name__ == "__main__":
    main()
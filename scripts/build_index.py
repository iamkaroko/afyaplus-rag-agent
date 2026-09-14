from app.rag import build_index


def main() -> None:
    """
    Build and persist the AfyaPlus knowledge index.
    """
    print("Building AfyaPlus knowledge index...")

    build_index()

    print("Knowledge index built successfully.")


if __name__ == "__main__":
    main()
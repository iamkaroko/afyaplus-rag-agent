from pathlib import Path
from typing import Any

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config import OPENAI_API_KEY


BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
STORAGE_DIR = BASE_DIR / "storage"

MIN_SIMILARITY_SCORE = 0.40


def configure_rag() -> None:
    """
    Configure the embedding model and text splitter used
    by the RAG pipeline.
    """
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small"
    )

    Settings.text_splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=80,
    )


def load_documents():
    """
    Load all supported documents from the AfyaPlus
    knowledge directory.

    Returns:
        A list of LlamaIndex Document objects.

    Raises:
        FileNotFoundError: If the knowledge directory does not exist.
        ValueError: If no documents are found.
    """
    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: {KNOWLEDGE_DIR}"
        )

    documents = SimpleDirectoryReader(
        input_dir=str(KNOWLEDGE_DIR),
        recursive=True,
    ).load_data()

    if not documents:
        raise ValueError(
            "No knowledge documents were found."
        )

    return documents


def build_index() -> VectorStoreIndex:
    """
    Build a vector index from the local AfyaPlus knowledge
    documents and persist it to disk.

    Returns:
        The newly created vector index.
    """
    configure_rag()

    documents = load_documents()

    index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True,
    )

    index.storage_context.persist(
        persist_dir=str(STORAGE_DIR)
    )

    return index


def load_index() -> VectorStoreIndex:
    """
    Load an existing vector index from local storage.

    Returns:
        The persisted vector index.

    Raises:
        FileNotFoundError: If no persisted index exists.
    """
    configure_rag()

    if not STORAGE_DIR.exists():
        raise FileNotFoundError(
            "Vector index does not exist. "
            "Run index ingestion first."
        )

    storage_context = StorageContext.from_defaults(
        persist_dir=str(STORAGE_DIR)
    )

    return load_index_from_storage(
        storage_context
    )


def get_index() -> VectorStoreIndex:
    """
    Return the existing vector index or create one
    when no persisted index exists.

    Returns:
        An AfyaPlus vector index.
    """
    if STORAGE_DIR.exists():
        return load_index()

    return build_index()


def retrieve_context(
    query: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant AfyaPlus knowledge chunks for a query.

    Results below the configured similarity threshold are
    discarded to reduce the risk of grounding responses in
    irrelevant context.

    Args:
        query: User question to search for.
        top_k: Maximum number of candidate chunks to retrieve.

    Returns:
        Relevant chunks containing text, similarity score,
        and source metadata.

    Raises:
        ValueError: If the query is empty.
    """
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    index = get_index()

    retriever = index.as_retriever(
        similarity_top_k=top_k
    )

    nodes = retriever.retrieve(query)

    results: list[dict[str, Any]] = []

    for node in nodes:
        if (
            node.score is not None
            and node.score >= MIN_SIMILARITY_SCORE
        ):
            results.append(
                {
                    "text": node.node.get_content(),
                    "score": node.score,
                    "metadata": node.node.metadata,
                }
            )

    return results
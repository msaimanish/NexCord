from pathlib import Path

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from backend.models import KnowledgeDocument, KnowledgeChunk
from backend.repositories.knowledge_repository import (
    create_document,
    get_document_by_source,
    search_knowledge_chunks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def chunk_text(
    text: str,
    max_chars: int = 1000,
) -> list[str]:
    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = (
            paragraph
            if not current
            else f"{current}\n\n{paragraph}"
        )

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)

            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def ingest_document(
    db: Session,
    path: Path,
) -> KnowledgeDocument:
    content = path.read_text(
        encoding="utf-8",
    )

    source = path.resolve().relative_to(PROJECT_ROOT).as_posix()

    existing_document = get_document_by_source(
        db,
        source,
    )

    if existing_document is not None:
        db.delete(existing_document)
        db.flush()

    document = KnowledgeDocument(
        name=path.name,
        document_type="OPERATIONAL_KNOWLEDGE",
        source=source,
        content=content,
    )

    create_document(
        db,
        document,
    )

    chunks = chunk_text(content)

    if not chunks:
        raise ValueError(
            f"Document {path} produced no chunks."
        )

    model = get_embedding_model()

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
    )

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        knowledge_chunk = KnowledgeChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding.tolist(),
        )

        db.add(knowledge_chunk)

    db.commit()
    db.refresh(document)

    return document

def query_knowledge(
    db: Session,
    query: str,
    top_k: int = 3,
) -> dict:
    if not query.strip():
        raise ValueError(
            "query must not be empty"
        )

    if not 1 <= top_k <= 10:
        raise ValueError(
            "top_k must be between 1 and 10"
        )

    model = get_embedding_model()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    results = search_knowledge_chunks(
        db,
        query_embedding,
        top_k,
    )

    knowledge_results = []

    for chunk, distance in results:
        knowledge_results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_name": chunk.document.name,
                "source": chunk.document.source,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": float(distance),
                "similarity": float(1 - distance),
            }
        )

    return {
        "query": query,
        "result_count": len(knowledge_results),
        "results": knowledge_results,
    }
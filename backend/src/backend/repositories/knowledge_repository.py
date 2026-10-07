from backend.models import KnowledgeDocument, KnowledgeChunk
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload


def search_knowledge_chunks(
    db: Session,
    query_embedding: list[float],
    top_k: int,
) -> list[tuple[KnowledgeChunk, float]]:
    distance = (
        KnowledgeChunk.embedding
        .cosine_distance(query_embedding)
        .label("distance")
    )

    statement = (
        select(KnowledgeChunk, distance)
        .options(
            selectinload(KnowledgeChunk.document)
        )
        .order_by(distance)
        .limit(top_k)
    )

    return list(db.execute(statement).all())


def get_document_by_source(
    db: Session,
    source: str,
) -> KnowledgeDocument | None:
    statement = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.source == source)
    )

    return db.scalars(statement).one_or_none()


def create_document(
    db: Session,
    document: KnowledgeDocument,
) -> KnowledgeDocument:
    db.add(document)
    db.flush()

    return document
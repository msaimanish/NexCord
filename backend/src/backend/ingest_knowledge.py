from pathlib import Path

from backend.database import SessionLocal
from backend.services.knowledge_service import ingest_document


PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


def main() -> None:
    documents = sorted(
        KNOWLEDGE_DIR.glob("*.md")
    )

    if not documents:
        raise RuntimeError(
            f"No knowledge documents found in {KNOWLEDGE_DIR}"
        )

    db = SessionLocal()

    try:
        for document_path in documents:
            document = ingest_document(
                db,
                document_path,
            )

            print(
                f"Ingested: {document.name} "
                f"(id={document.id})"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
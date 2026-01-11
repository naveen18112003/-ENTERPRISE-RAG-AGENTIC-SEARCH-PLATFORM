"""
Data Loading & Initialization Script
FINAL VERSION (PDF ONLY – POLICY DOCS)
"""

import sys
import gc
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.services import DataIngestionPipeline, VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sample_data():
    settings = get_settings()
    logger.info("Starting data ingestion...")

    # init pipeline & vector store
    pipeline = DataIngestionPipeline()
    vector_manager = VectorStoreManager()

    # get actual vectorstore
    vectorstore = (
        vector_manager.get_vectorstore()
        if hasattr(vector_manager, "get_vectorstore")
        else vector_manager.vectorstore
    )

    logger.info("Loading policy PDF documents...")

    # 🔥 PDF ONLY INGESTION
    docs = pipeline.ingest(
        data_dir=settings.pdf_data_path,
        file_type="pdf",          # ✅ only PDFs
        access_roles=["admin"],   # ✅ generic / admin access
        category="policy",        # ✅ NOT HR
    )

    if not docs:
        logger.warning("No policy PDF documents found.")
        return

    texts = [
        doc.content
        for doc in docs
        if doc.content and doc.content.strip()
    ]

    logger.info(f"Total policy chunks: {len(texts)}")

    BATCH_SIZE = 10
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]

        logger.info(
            f"Adding batch {i // BATCH_SIZE + 1} / {total_batches}"
        )

        vectorstore.add_texts(batch)
        gc.collect()

    logger.info("✅ Data ingestion complete!")
    logger.info("✅ Vector store populated with POLICY PDFs")


if __name__ == "__main__":
    load_sample_data()

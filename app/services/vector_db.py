# services/vector_db.py

import os
import faiss
import pickle
import numpy as np
from typing import List, Dict
from app.services.llm_factory import get_embedding_model
from services.db import get_all_products
from utils.logger import logger

# Paths for prebuilt index and metadata
FAISS_INDEX_PATH = "data/faiss_index.index"
METADATA_PATH = "data/product_metadata.pkl"


class ProductVectorDB:
    """
    FAISS-based vector store for product semantic search.
    Uses LLaMA embeddings to encode product descriptions.
    Supports loading prebuilt index from disk for faster startup.
    """

    def __init__(self, embedding_dim: int = 4096):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.product_ids: List[str] = []
        self.emb_model = get_embedding_model()
        logger.info("ProductVectorDB initialized.")

        # Try loading prebuilt index
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
            self.load_index_from_disk()
        else:
            self.build_index()  # fallback if prebuilt index not found

    # -----------------------------
    # Load / Save prebuilt index
    # -----------------------------
    def load_index_from_disk(self):
        try:
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                metadata = pickle.load(f)
            self.product_ids = [p["id"] for p in metadata]
            logger.info(f"Loaded FAISS index from disk with {len(self.product_ids)} products.")
        except Exception as e:
            logger.warning(f"Failed to load FAISS index from disk: {e}")
            self.build_index()

    def save_index_to_disk(self):
        try:
            faiss.write_index(self.index, FAISS_INDEX_PATH)
            metadata = [{"id": pid} for pid in self.product_ids]
            with open(METADATA_PATH, "wb") as f:
                pickle.dump(metadata, f)
            logger.info("FAISS index and metadata saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

    # -----------------------------
    # Build index from DB
    # -----------------------------
    def build_index(self):
        """
        Load all products from DB and build FAISS index.
        """
        products = get_all_products()
        if not products:
            logger.warning("No products found to index.")
            return

        vectors = []
        for p in products:
            vec = np.array(self.emb_model.embed_text(p["description"]), dtype="float32")
            vectors.append(vec)
            self.product_ids.append(p["id"])

        vectors_np = np.vstack(vectors)
        self.index.add(vectors_np)
        logger.info(f"FAISS index built with {len(self.product_ids)} products.")
        self.save_index_to_disk()

    # -----------------------------
    # Add new products dynamically
    # -----------------------------
    def add_product(self, product: Dict):
        vec = np.array(self.emb_model.embed_text(product["description"]), dtype="float32")
        self.index.add(np.array([vec]))
        self.product_ids.append(product["id"])
        logger.info(f"Product {product['id']} added to FAISS index.")
        self.save_index_to_disk()

    # -----------------------------
    # Search
    # -----------------------------
    def search(self, query: str, top_k: int = 5) -> List[str]:
        query_vec = np.array(self.emb_model.embed_text(query), dtype="float32")
        distances, indices = self.index.search(np.array([query_vec]), top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.product_ids):
                results.append(self.product_ids[idx])
        logger.info(f"Search returned {len(results)} results for query: {query}")
        return results


# -----------------------------
# Singleton instance
# -----------------------------
vector_db_instance = ProductVectorDB()


# -----------------------------
# Convenience functions
# -----------------------------
def search_products(query: str, top_k: int = 5) -> List[str]:
    return vector_db_instance.search(query, top_k)


def add_product_to_index(product: Dict):
    return vector_db_instance.add_product(product)

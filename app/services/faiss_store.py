# vectorstore/build_faiss_index.py
"""
Builds a FAISS index from a product catalog using LLaMA embeddings.
"""

import faiss
import pickle
import numpy as np
from llama_cpp import Llama
from typing import List, Dict
from utils.logger import logger

# --------------------------
# Config
# --------------------------
PRODUCT_CATALOG_PATH = "data/products.pkl"  # Should contain List[Dict] of products
FAISS_INDEX_PATH = "data/faiss_index.index"
METADATA_PATH = "data/product_metadata.pkl"

EMBEDDING_MODEL_PATH = "models/llama-3-8b.gguf"
EMBEDDING_DIM = 4096  # Make sure this matches your LLaMA model's embedding size

# --------------------------
# Load product catalog
# --------------------------
def load_catalog(path: str) -> List[Dict]:
    with open(path, "rb") as f:
        catalog = pickle.load(f)
    logger.info(f"Loaded {len(catalog)} products from catalog")
    return catalog

# --------------------------
# Generate embeddings
# --------------------------
def embed_product_names(catalog: List[Dict], llama_model: Llama) -> np.ndarray:
    embeddings = []
    for product in catalog:
        name = product.get("name", "")
        if not name:
            embeddings.append(np.zeros(EMBEDDING_DIM, dtype=np.float32))
            continue
        result = llama_model.embed(name)
        vector = np.array(result["embedding"], dtype=np.float32)
        embeddings.append(vector)
    return np.vstack(embeddings)

# --------------------------
# Build FAISS index
# --------------------------
def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    index = faiss.IndexFlatL2(EMBEDDING_DIM)  # L2 distance
    index.add(embeddings)
    logger.info(f"FAISS index built with {index.ntotal} vectors")
    return index

# --------------------------
# Save index + metadata
# --------------------------
def save_index_and_metadata(index: faiss.Index, metadata: List[Dict]):
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    logger.info(f"FAISS index and metadata saved to disk")

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    # Initialize LLaMA
    llama = Llama(model_path=EMBEDDING_MODEL_PATH, n_ctx=EMBEDDING_DIM)

    # Load catalog
    catalog = load_catalog(PRODUCT_CATALOG_PATH)

    # Generate embeddings
    embeddings = embed_product_names(catalog, llama)

    # Build FAISS index
    index = build_faiss_index(embeddings)

    # Save index + metadata
    save_index_and_metadata(index, catalog)

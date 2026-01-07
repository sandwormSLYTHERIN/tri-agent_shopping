# tools/product_search.py
"""
Semantic product search for tri-agent e-commerce system.
Uses LLaMA embeddings and a FAISS vector store.
"""

from typing import List, Dict
import numpy as np
from llama_cpp import Llama
from services.faiss_store import load_faiss_index  # assume you have a wrapper to load FAISS index
from utils.logger import logger

# Initialize LLaMA embeddings model (ensure model_path points to GGUF file)
llama = Llama(model_path="models/llama-3-8b.gguf", n_ctx=4096)

# Load FAISS index
faiss_index, product_metadata = load_faiss_index()  # returns index and corresponding metadata list

def embed_query(query: str) -> np.ndarray:
    """
    Generate LLaMA embedding for a query.
    """
    result = llama.embed(query)
    vector = np.array(result["embedding"], dtype=np.float32)
    return vector

def semantic_product_search(user_query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top-k products semantically related to the user query.

    Args:
        user_query (str): User input text describing product need.
        top_k (int): Number of products to return.

    Returns:
        List[Dict]: List of products with metadata (id, name, price, etc.)
    """
    try:
        # 1️⃣ Compute embedding for user query
        query_vec = embed_query(user_query)

        # 2️⃣ Search FAISS index
        distances, indices = faiss_index.search(np.expand_dims(query_vec, axis=0), top_k)

        # 3️⃣ Retrieve product metadata
        results = []
        for idx in indices[0]:
            if idx < len(product_metadata):
                results.append(product_metadata[idx])
        
        logger.info(f"Product search for '{user_query}' returned {len(results)} items")
        return results

    except Exception as e:
        logger.error(f"Product search failed for query '{user_query}': {e}")
        return []


# Optional self-test
if __name__ == "__main__":
    sample_query = "wireless bluetooth headphones with noise cancellation"
    products = semantic_product_search(sample_query)
    for p in products:
        print(p)

# reranker/llama_reranker.py
"""
Rerank products using LLaMA embeddings.
"""

from typing import List, Dict
import numpy as np
from llama_cpp import Llama
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import logger

# Initialize LLaMA model for embeddings (CPU/GGUF)
llama_model = Llama(model_path="models/llama-3-8b.gguf", n_ctx=4096)

def embed_text(text: str) -> np.ndarray:
    """
    Generate embedding for given text using LLaMA.
    """
    result = llama_model.embed(text)
    vector = np.array(result["embedding"], dtype=np.float32)
    return vector

def rerank_products(user_query: str, products: List[Dict], llama_model_override: Llama | None = None) -> List[Dict]:
    """
    Rerank products based on semantic similarity to user query.

    Args:
        user_query (str): User search query
        products (List[Dict]): List of product dicts, each must contain 'name' field
        llama_model_override (Llama | None): Optional LLaMA instance for embedding

    Returns:
        List[Dict]: Products sorted by similarity (high → low)
    """
    model = llama_model_override or llama_model

    try:
        # Embed query
        query_vec = np.array(model.embed(user_query)["embedding"], dtype=np.float32).reshape(1, -1)

        # Embed product names
        product_vecs = []
        for p in products:
            name = p.get("name", "")
            if not name:
                product_vecs.append(np.zeros(query_vec.shape[1], dtype=np.float32))
            else:
                product_vecs.append(np.array(model.embed(name)["embedding"], dtype=np.float32))
        product_vecs = np.vstack(product_vecs)

        # Compute cosine similarity
        sims = cosine_similarity(query_vec, product_vecs).flatten()

        # Sort products by similarity
        sorted_products = [p for _, p in sorted(zip(sims, products), key=lambda x: x[0], reverse=True)]

        logger.info(f"Reranked {len(products)} products for query '{user_query}'")
        return sorted_products

    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        return products  # fallback: return original order

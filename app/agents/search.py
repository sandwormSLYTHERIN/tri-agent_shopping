# agents/product_agent.py
"""
Product Search Agent for Tri-Agent E-commerce System
"""

from typing import Dict, List
from llama_cpp import Llama

from services.vector_db import search_products
from services.rerank import rerank_products
from app.services.llm_factory import get_chat_llm, call_llm_with_memory
from utils.logger import logger
from utils.fallback import fallback_response
from utils.retry import retry_llm
from utils.response_schema import AgentResponse

# --------------------------
# LLaMA reranker (local)
# --------------------------
llama_reranker_model = Llama(
    model_path="models/llama-3-8b.gguf",
    n_ctx=4096
)

# --------------------------
# Product Agent
# --------------------------
@retry_llm
def invoke_product_agent(user_id: str, user_input: str) -> Dict:
    """
    Handle product discovery queries using:
    FAISS → LLaMA reranker → OpenAI LLM (with memory)
    """
    try:
        logger.info("ProductAgent invoked")

        # 1️⃣ Retrieve products via vector DB (FAISS)
        retrieved_products = search_products(user_input, top_k=5)

        if not retrieved_products:
            return fallback_response("product")

        # 2️⃣ Rerank using local LLaMA
        reranked_products = rerank_products(
            query=user_input,
            products=retrieved_products,
            llama_model=llama_reranker_model
        )

        # 3️⃣ Build structured prompt
        prompt_text = f"""
You are a PRODUCT SEARCH AGENT.

User Query:
{user_input}

Relevant Products:
{reranked_products}

Rules:
- Recommend ONLY the listed products.
- NEVER invent prices, stock, or offers.
- Respond STRICTLY in valid JSON.
"""

        # 4️⃣ Call LLM with per-user memory
        llm = get_chat_llm()
        raw_output = call_llm_with_memory(
            llm=llm,
            prompt_text=prompt_text,
            user_id=user_id
        )

        # 5️⃣ Validate & return
        response = AgentResponse.model_validate_json(raw_output).dict()
        response["products"] = reranked_products
        return response

    except Exception as e:
        logger.error(f"ProductAgent failed: {e}")
        return fallback_response("product")

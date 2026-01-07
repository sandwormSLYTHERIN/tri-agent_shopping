# llm/llm_factory.py

import os
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import LlamaCppEmbeddings
from memory.memorymanager import ConversationMemoryManager

# Load API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --------------------------
# Shared memory manager
# --------------------------
memory_manager = ConversationMemoryManager(buffer_size=3)

# --------------------------
# Chat LLM factory
# --------------------------
def get_chat_llm(model_name: str = "gpt-4o-mini", temperature: float = 0.2):
    """Returns a ChatOpenAI instance"""
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY
    )

# --------------------------
# Wrapper to call LLM with per-user memory (modern way)
# --------------------------
def call_llm_with_memory(llm: ChatOpenAI, messages: list[dict], user_id: str) -> str:
    """
    Call LLM with per-user memory.

    Args:
        llm (ChatOpenAI): LangChain ChatOpenAI instance
        messages (list[dict]): List of messages [{"role": "system|user|assistant", "content": str}]
        user_id (str): Unique user identifier

    Returns:
        str: LLM response text
    """
    # 1️⃣ Retrieve per-user memory messages
    memory_msgs = memory_manager.get_buffer_window(user_id)

    # 2️⃣ Combine memory and new messages
    full_messages = memory_msgs + messages

    # 3️⃣ Call LLM
    response = llm(full_messages)

    # 4️⃣ Store LLM response in memory
    memory_manager.update_buffer(user_id, messages + [{"role": "assistant", "content": response}])

    return response

# --------------------------
# Embedding model factory
# --------------------------
def get_embedding_model():
    """Used ONLY for product embeddings & reranking"""
    return LlamaCppEmbeddings(
        model_path="models/llama-3-8b.gguf",
        n_ctx=4096
    )

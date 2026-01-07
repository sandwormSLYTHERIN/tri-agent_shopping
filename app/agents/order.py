from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompts.order_prompt import build_order_prompt
from app.services.llm_factory import get_chat_llm
from tools.order_lookup import get_order_status
from memory.memorymanager import ConversationMemoryManager
from utils.logger import logger
from utils.fallback import fallback_response
from utils.retry import retry_llm
from utils.response_schema import AgentResponse


# Initialize shared memory manager
memory_manager = ConversationMemoryManager(buffer_size=3)


@retry_llm
def invoke_order_agent(user_id: str, user_input: str, order_context: dict | None = None):
    try:
        logger.info("OrderAgent invoked")

        # 1️⃣ Retrieve per-user memory
        memory = memory_manager.get_buffer_window(user_id)

        # 2️⃣ Fetch deterministic order context
        context = get_order_status(order_context) if order_context else "Not provided"

        # 3️⃣ Build prompt text
        prompt_text = build_order_prompt(user_input, context)

        # 4️⃣ Wrap prompt correctly
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text)
        ])

        # 5️⃣ Load memory
        memory_vars = memory.load_memory_variables({})
        messages = prompt.format_messages(**memory_vars)

        # 6️⃣ Call LLM (modern API)
        llm = get_chat_llm()
        response = llm.invoke(messages)

        raw_output = response.content

        # 7️⃣ Save memory
        memory.save_context(
            {"input": user_input},
            {"output": raw_output}
        )

        # 8️⃣ Validate JSON
        return AgentResponse.model_validate_json(raw_output).dict()

    except Exception as e:
        logger.error(f"OrderAgent failed: {e}")
        return fallback_response("order")

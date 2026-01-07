# agents/complaint_agent.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from tools.create_ticket import create_complaint_ticket, update_ticket_status
from tools.policy_lookup import fetch_policy
from app.services.llm_factory import get_chat_llm
from memory.memorymanager import ConversationMemoryManager
from utils.logger import logger
from utils.fallback import fallback_response
from utils.retry import retry_llm
from utils.response_schema import AgentResponse

# Initialize shared memory manager (window size 3)
memory_manager = ConversationMemoryManager(buffer_size=3)

prompt_template = ChatPromptTemplate.from_messages([
    ("system",
     """
You are a COMPLAINT RESOLUTION AGENT.

Rules:
- Always acknowledge the issue.
- Always reference the complaint ticket ID.
- Use ONLY retrieved policy data.
- NEVER promise refunds or timelines.
- Respond strictly in JSON matching schema.
"""),
    ("human",
     "User Complaint:\n{query}\nTicket Info:\n{ticket_info}\nPolicy Info:\n{policy_info}")
])

@retry_llm
def invoke_complaint_agent(user_id: str, user_input: str):
    try:
        logger.info("ComplaintAgent invoked")

        # 1️⃣ Retrieve per-user memory
        memory = memory_manager.get_buffer_window(user_id)

        # 2️⃣ Deterministically create ticket
        ticket_info = create_complaint_ticket(user_input, user_id)

        # 3️⃣ Move ticket to in_progress as agent starts
        ticket_info = update_ticket_status(ticket_info, "in_progress")

        # 4️⃣ Fetch relevant policy
        policy_info = fetch_policy(user_input)

        # 5️⃣ Generate response using modern ChatOpenAI interface
        llm = get_chat_llm()
        response_text = llm.generate(
            messages=[{"role": "system", "content": prompt_template.format_prompt(
                query=user_input,
                ticket_info=ticket_info,
                policy_info=policy_info
            ).to_string()}],
            memory=memory
        ).generations[0][0].text

        # 6️⃣ Mark ticket as resolved after agent generates solution
        ticket_info = update_ticket_status(ticket_info, "resolved")

        # 7️⃣ Return structured response including updated ticket
        response = AgentResponse.model_validate_json(response_text).dict()
        response["ticket_info"] = ticket_info
        return response

    except Exception as e:
        logger.error(f"ComplaintAgent failed: {e}")
        return fallback_response("complaint")

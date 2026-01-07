def fallback_response(agent_type: str):
    return {
        "type": agent_type,
        "message": "I'm unable to retrieve the required information right now. Please try again later.",
        "action_taken": "fallback",
        "confidence": "low"
    }

from langchain.memory import ConversationBufferWindowMemory
from typing import Dict

class ConversationMemoryManager:
    """
    Manages per-user conversation memory for all agents using
    ConversationBufferWindowMemory.
    """

    def __init__(self, buffer_size: int = 3):
        self.buffer_size = buffer_size
        self._user_memory: Dict[str, ConversationBufferWindowMemory] = {}

    def get_buffer_window(self, user_id: str) -> ConversationBufferWindowMemory:
        """
        Returns ConversationBufferWindowMemory for the given user.
        Creates a new buffer window if it doesn't exist.
        """
        if user_id not in self._user_memory:
            self._user_memory[user_id] = ConversationBufferWindowMemory(
                k=self.buffer_size,
                return_messages=True
            )
        return self._user_memory[user_id]

    def reset_user_buffer(self, user_id: str):
        """
        Resets memory buffer for a single user.
        """
        self._user_memory[user_id] = ConversationBufferWindowMemory(
            k=self.buffer_size,
            return_messages=True
        )

    def reset_all_buffers(self):
        """
        Clears all user memories.
        """
        self._user_memory = {}

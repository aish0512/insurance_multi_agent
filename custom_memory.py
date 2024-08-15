from langchain.memory import ConversationBufferMemory
from typing import Dict, Any

class CustomMemory(ConversationBufferMemory):
    def save_context(self, inputs, outputs):
        input_str = str(inputs["input"]) if isinstance(inputs, dict) else str(inputs)
        output_str = str(outputs["output"]) if isinstance(outputs, dict) else str(outputs)
        self.chat_memory.add_user_message(input_str)
        self.chat_memory.add_ai_message(output_str)

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {self.memory_key: self.chat_memory.messages}

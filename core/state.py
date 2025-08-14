from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatState:
    username: str = "user"
    messages: list = field(default_factory=list)
    config: dict = field(
        default_factory=lambda: {
            "model": "llama3.2:3b",
            "temperature": 0.6,
            "use_memory": True,
            "use_web": False,  # web tool (Tavily) kapalı başlasın
            "stream": True,
        }
    )

    def append_message(self, role: str, content: str):

        self.messages.append({"role": role, "content": content, "ts": datetime.now()})

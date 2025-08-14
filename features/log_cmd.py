from core.io import Console
from core.state import ChatState


def log_handle(state: ChatState, console: Console, args: list[str]) -> None:

    console.print_sys("Mesaj Geçmişi:")
    for message in state.messages:
        role = message["role"]
        ts = message["ts"]  # datetime ise formatlayalım:
        tstr = ts.strftime("%H:%M:%S") if hasattr(ts, "strftime") else str(ts)

        # Content'i parse et
        content = message["content"]

        # Eğer content bir LangChain message objeyse content attribute'unu kullan
        if hasattr(content, "content"):
            text = content.content
        # Diğer durumlarda (string) direkt kullan
        else:
            text = str(content)

        console.print_sys(f"  [{tstr}] {role}: {text}")

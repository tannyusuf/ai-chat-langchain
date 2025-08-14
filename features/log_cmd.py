from core.io import Console
from core.state import ChatState


def log_handle(state: ChatState, console: Console, args: list[str]) -> None:

    console.print_sys("Mesaj Geçmişi:")
    for message in state.messages:
        role = message["role"]
        ts = message["ts"]
        tstr = ts.strftime("%H:%M:%S") if hasattr(ts, "strftime") else str(ts)

        content = message["content"]

        if hasattr(content, "content"):
            text = content.content

        else:
            text = str(content)

        console.print_sys(f"  [{tstr}] {role}: {text}")

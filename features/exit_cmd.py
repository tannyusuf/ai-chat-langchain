from core.io import Console
from core.state import ChatState


def exit_handle(state: ChatState, console: Console, args: list[str]) -> None:

    console.print_sys("Görüşürüz! 👋")
    raise SystemExit(0)

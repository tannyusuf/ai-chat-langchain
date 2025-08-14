# features/username_cmd.py
from core.io import Console
from core.state import ChatState


def show_handle(state: ChatState, console: Console, args: list[str]) -> None:

    console.print_sys(f"Kullanıcı adı: {state.username}")


def change_handle(state: ChatState, console: Console, args: list[str]) -> None:

    if args:
        new_name = " ".join(args).strip()
    else:

        new_name = console.read_line("Yeni kullanıcı adı").strip()

    if not new_name:
        console.print_sys("Uyarı: Boş kullanıcı adı kabul edilmedi.")
        return
    old = state.username
    state.username = new_name
    console.print_sys(f"Kullanıcı adı değiştirildi: {old} → {state.username}")

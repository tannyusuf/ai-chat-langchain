from prompt_toolkit.patch_stdout import patch_stdout

from core.ai import AIError, chat_sync, to_ollama_messages
from core.brain import Brain
from core.io import Console
from core.router import CommandRouter
from core.spinner import Spinner
from core.state import ChatState
from features.exit_cmd import exit_handle
from features.help_cmd import help_handle
from features.log_cmd import log_handle
from features.settings_cmd import make_handlers
from features.username_cmd import change_handle, show_handle

MODEL = "llama3.2:3b"


def main():
    name = input("Kullanıcı adını gir : ").strip()
    state = ChatState(username=name)
    commands = ["/help", "/exit", "/log", "--username", "--change_username"]

    console = Console(commands=commands)
    router = CommandRouter()
    router.register("/help", help_handle)
    router.register("/log", log_handle)
    router.register("--username", show_handle)
    router.register("--change_username", change_handle)
    router.register("/exit", exit_handle)

    brain = Brain(state)
    set_handle, show_cfg_handle = make_handlers(brain)
    router.register("/set", set_handle)
    router.register("/show_config", show_cfg_handle)

    router.add_alias(":q", "/exit")
    router.add_alias("exit", "/exit")
    router.add_alias("help", "/help")

    console.print_sys("Yardım: /help — Çıkış: /exit veya :q")
    console.print_sys("Ayarlar: /show_config — Değiştir: /set <key> <value>")

    while True:
        try:
            line = console.read_line(state.username).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not line:
            continue

        if router.dispatch(line, state, console):
            continue

        state.append_message("user", line)

        spinner = Spinner("Bot düşünüyor")
        try:
            if state.config.get("stream", True):
                spinner.start()
                with patch_stdout():
                    reply = brain.generate_stream(state, line, console, spinner=spinner)
                spinner.stop()
            else:
                spinner.start()
                reply = brain.generate_sync(state, line, console=None)
                spinner.stop()
        except Exception as e:
            spinner.stop()
            console.print_sys(f"[Hata] {e}")
            continue

        state.append_message("bot", reply)


if __name__ == "__main__":
    main()

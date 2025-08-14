import shlex


class CommandRouter:

    def __init__(self):
        self.handlers = {}
        self.aliases = {}

    def register(self, command: str, handler):
        self.handlers[command] = handler

    def add_alias(self, alias: str, target: str):
        self.aliases[alias] = target

    def dispatch(self, line: str, state, console) -> bool:
        if not line or not (line.startswith("/") or line.startswith("--")):
            return False

        parts = shlex.split(line)
        cmd = parts[0]
        args = parts[1:]

        cmd = self.aliases.get(cmd, cmd)
        handler = self.handlers.get(cmd)
        if not handler:
            console.print_sys(f"Bilinmeyen komut: {cmd}")
            return True  # Komut denendi ama bulunamadı

        handler(state, console, args)
        return True

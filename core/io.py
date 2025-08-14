import sys
import threading
import time

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory


class Console:

    def __init__(self, commands: list[str]):
        self.history = InMemoryHistory()
        self.session = PromptSession(history=self.history)
        self.completer = WordCompleter(commands, ignore_case=True)
        self.loading_animation = None

    def read_line(self, username: str) -> str:
        prompt_text = f"{username} > "
        return self.session.prompt(prompt_text, completer=self.completer)

    # def print_user(self, text: str):
    #    print(f"You > {text}")

    # def print_bot(self, text: str):
    #    print(f"Bot > {text}")

    def print_sys(self, text: str):
        print(f"System > {text}")

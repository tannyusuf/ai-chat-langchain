# utils/callbacks.py

from langchain.callbacks.base import BaseCallbackHandler


class ConsoleStreamCallback(BaseCallbackHandler):
    def __init__(self, console, spinner=None):
        self.console = console
        self.spinner = spinner
        self._printed_header = False

    def on_llm_new_token(self, token, **kwargs):
        # İlk token geldiyse spinner'ı durdur
        if self.spinner and getattr(self.spinner, "running", False):
            self.spinner.stop()
        # Akış başlığını bir kere yaz
        if not self._printed_header:
            print("\rBot  > ", end="", flush=True)
            self._printed_header = True
        # Token'ı ekle
        print(token, end="", flush=True)

    def on_llm_end(self, *args, **kwargs):
        # Akış biterken satırı kapat
        if self._printed_header:
            print()
        self._printed_header = False

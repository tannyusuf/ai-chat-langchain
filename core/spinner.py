import sys
import threading
import time


class Spinner:
    def __init__(self, message="Düşünüyor"):
        self.message = message
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def _animate(self):
        symbols = ["|", "/", "-", "\\"]
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{self.message}... {symbols[idx]}")
            sys.stdout.flush()
            idx = (idx + 1) % len(symbols)
            time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.1)
        # Satırı temizle
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

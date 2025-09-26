from __future__ import annotations

import logging
import threading
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "app.log"


class TkTextHandler(logging.Handler):
    """Logging handler that writes messages to a Tkinter Text widget."""

    def __init__(self, widget):  # type: ignore[override]
        super().__init__()
        self.widget = widget
        self.widget.configure(state="disabled")
        self.lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        with self.lock:
            def append() -> None:
                self.widget.configure(state="normal")
                self.widget.insert("end", msg + "\n")
                self.widget.see("end")
                self.widget.configure(state="disabled")

            self.widget.after(0, append)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("cenet")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def attach_text_handler(logger: logging.Logger, widget) -> None:
    handler = TkTextHandler(widget)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

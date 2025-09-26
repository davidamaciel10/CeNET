from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import config as config_module
from .flows.certificates import CertificateWindow
from .flows.records import RecordsWindow
from .logger import attach_text_handler, configure_logging


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CeNET - Gestión de certificados y actas")
        self.geometry("760x600")
        self.resizable(False, False)

        self.config_manager = config_module.load_config()
        self.logger = configure_logging()
        self._build_styles()
        self._build_layout()

    def _build_styles(self):
        style = ttk.Style(self)
        style.configure("Card.TFrame", background="#F5F7FA", relief="ridge", padding=15)
        style.configure(
            "Card.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=20,
        )

    def _build_layout(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = ttk.Label(
            container,
            text="Seleccione una opción",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(pady=(0, 10))

        cards = ttk.Frame(container)
        cards.pack(fill="x", pady=10)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        cert_button = ttk.Button(
            cards,
            text="Descargar certificados",
            style="Card.TButton",
            command=self.open_certificates,
        )
        cert_button.grid(row=0, column=0, padx=10, sticky="ew")

        records_button = ttk.Button(
            cards,
            text="Exportar actas",
            style="Card.TButton",
            command=self.open_records,
        )
        records_button.grid(row=0, column=1, padx=10, sticky="ew")

        log_frame = ttk.LabelFrame(container, text="Registro de eventos")
        log_frame.pack(fill="both", expand=True, pady=(20, 0))

        self.log_text = tk.Text(log_frame, height=14, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True)
        attach_text_handler(self.logger, self.log_text)

    def open_certificates(self):
        CertificateWindow(self, self.config_manager, self.logger)

    def open_records(self):
        RecordsWindow(self, self.config_manager, self.logger)


def run_app():
    app = Application()
    app.mainloop()

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional

from .. import config as config_module


class BaseFlowWindow(tk.Toplevel):
    def __init__(self, master, config, logger, title: str):
        super().__init__(master)
        self.config_manager = config
        self.logger = logger
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._thread = None
        self._build_common_variables()
        self.columnconfigure(0, weight=1)

    def _build_common_variables(self):
        year, cohort, modality, last_output, url = config_module.read_common_parameters(
            self.config_manager
        )
        self.year_var = tk.StringVar(value=str(year))
        self.cohort_var = tk.StringVar(value=cohort)
        self.modality_var = tk.StringVar(value=modality)
        self.url_moodle_var = tk.StringVar(value=url)
        self.output_dir_var = tk.StringVar(value=str(last_output))
        self.status_var = tk.StringVar(value="Listo")
        self.progress_var = tk.IntVar(value=0)
        self.progress_total = 0

    def build_common_section(self, container: tk.Widget, modalities: list[str]):
        section = ttk.LabelFrame(container, text="Parámetros comunes")
        section.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        for i in range(2):
            section.columnconfigure(i, weight=1)
        ttk.Label(section, text="Año").grid(row=0, column=0, sticky="w")
        ttk.Entry(section, textvariable=self.year_var, width=10).grid(
            row=1, column=0, sticky="ew"
        )
        ttk.Label(section, text="Cohorte").grid(row=0, column=1, sticky="w")
        ttk.Entry(section, textvariable=self.cohort_var).grid(
            row=1, column=1, sticky="ew"
        )
        ttk.Label(section, text="Modalidad").grid(row=2, column=0, sticky="w")
        modality_combo = ttk.Combobox(
            section, textvariable=self.modality_var, values=modalities, state="readonly"
        )
        modality_combo.grid(row=3, column=0, sticky="ew")
        modality_combo.set(self.modality_var.get())
        ttk.Label(section, text="URL base Moodle").grid(row=2, column=1, sticky="w")
        ttk.Entry(section, textvariable=self.url_moodle_var).grid(
            row=3, column=1, sticky="ew"
        )
        return section

    def build_progress_section(self, container: tk.Widget):
        progress_frame = ttk.Frame(container)
        progress_frame.grid(row=99, column=0, sticky="ew", padx=10, pady=5)
        progress_frame.columnconfigure(0, weight=1)
        ttk.Label(progress_frame, textvariable=self.status_var).grid(
            row=0, column=0, sticky="w"
        )
        progress = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100, mode="determinate"
        )
        progress.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.counter_label = ttk.Label(progress_frame, text="0/0")
        self.counter_label.grid(row=2, column=0, sticky="w")
        return progress

    def set_progress(self, current: int, total: int) -> None:
        self.progress_total = max(total, 1)
        self.progress_var.set(int((current / self.progress_total) * 100))
        self.counter_label.configure(text=f"{current}/{total}")

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _on_close(self):
        if self._thread and self._thread.is_alive():
            self.logger.warning("La tarea sigue en ejecución. Espere a que finalice.")
            return
        self.destroy()

    def disable_inputs(self, widgets: list[tk.Widget]):
        for widget in widgets:
            widget.configure(state="disabled")

    def enable_inputs(self, widgets: list[tk.Widget]):
        for widget in widgets:
            widget.configure(state="normal")

    def run_in_thread(self, target: Callable, on_finish: Optional[Callable] = None):
        def wrapper():
            try:
                target()
            finally:
                self.after(0, lambda: on_finish() if on_finish else None)

        self._thread = threading.Thread(target=wrapper, daemon=True)
        self._thread.start()

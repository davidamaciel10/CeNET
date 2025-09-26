from __future__ import annotations

import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional
from urllib.parse import urlparse
from zipfile import ZipFile

import os
import pandas as pd
import requests

from .. import config as config_module
from ..utils import csv_utils
from ..utils.paths import ensure_directory, safe_filename, unique_path
from .base import BaseFlowWindow

REQUIRED_COLUMNS = {"dni", "nombre_completo", "provincia", "curso"}
LOG_HEADERS = [
    "timestamp",
    "dni",
    "curso",
    "provincia",
    "url",
    "resultado",
    "ruta_archivo",
]


class CertificateWindow(BaseFlowWindow):
    def __init__(self, master, config, logger):
        super().__init__(master, config, logger, "Descargar certificados")
        self.modalities = config_module.get_modalities(self.config_manager)
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        self.build_common_section(container, self.modalities)

        # Database file
        db_frame = ttk.LabelFrame(container, text="Base de datos")
        db_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        db_frame.columnconfigure(1, weight=1)
        ttk.Label(db_frame, text="CSV base").grid(row=0, column=0, sticky="w")
        self.db_path_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_path_var).grid(
            row=0, column=1, sticky="ew"
        )
        ttk.Button(db_frame, text="Seleccionar", command=self.select_db_file).grid(
            row=0, column=2, padx=5
        )
        self.db_error = ttk.Label(db_frame, foreground="red")
        self.db_error.grid(row=1, column=0, columnspan=3, sticky="w")

        # Credentials
        cred_frame = ttk.LabelFrame(container, text="Credenciales Moodle")
        cred_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        cred_frame.columnconfigure(1, weight=1)
        ttk.Label(cred_frame, text="Usuario").grid(row=0, column=0, sticky="w")
        self.user_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.user_var).grid(row=0, column=1, sticky="ew")
        ttk.Label(cred_frame, text="Contraseña").grid(row=1, column=0, sticky="w")
        self.password_var = tk.StringVar()
        ttk.Entry(
            cred_frame,
            textvariable=self.password_var,
            show="*",
        ).grid(row=1, column=1, sticky="ew")

        # Output folder
        output_frame = ttk.LabelFrame(container, text="Salida")
        output_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(1, weight=1)
        ttk.Label(output_frame, text="Carpeta destino").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(
            row=0, column=1, sticky="ew"
        )
        ttk.Button(output_frame, text="Seleccionar", command=self.select_output_dir).grid(
            row=0, column=2, padx=5
        )
        self.output_error = ttk.Label(output_frame, foreground="red")
        self.output_error.grid(row=1, column=0, columnspan=3, sticky="w")

        # Links section
        links_frame = ttk.LabelFrame(container, text="Links de certificados")
        links_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        ttk.Label(links_frame, text="Pegue los links (uno por línea)").grid(
            row=0, column=0, sticky="w"
        )
        self.links_text = tk.Text(links_frame, width=60, height=6)
        self.links_text.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.links_error = ttk.Label(links_frame, foreground="red")
        self.links_error.grid(row=2, column=0, columnspan=3, sticky="w")

        self.mapping_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            links_frame,
            text="Usar CSV de mapeo por DNI",
            variable=self.mapping_var,
            command=self._toggle_mapping,
        ).grid(row=3, column=0, sticky="w")
        self.mapping_path_var = tk.StringVar()
        self.mapping_entry = ttk.Entry(links_frame, textvariable=self.mapping_path_var)
        self.mapping_button = ttk.Button(
            links_frame, text="Seleccionar CSV", command=self.select_mapping_file
        )
        self.mapping_error = ttk.Label(links_frame, foreground="red")
        self.mapping_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0))
        self.mapping_button.grid(row=3, column=2, padx=5)
        self.mapping_error.grid(row=4, column=0, columnspan=3, sticky="w")
        self._toggle_mapping()

        # Controls
        control_frame = ttk.Frame(container)
        control_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=10)
        control_frame.columnconfigure(0, weight=1)
        self.start_button = ttk.Button(
            control_frame, text="Iniciar descarga", command=self.start_download
        )
        self.start_button.grid(row=0, column=0, sticky="ew")
        self.open_output_button = ttk.Button(
            control_frame,
            text="Abrir carpeta de salida",
            command=self.open_output_folder,
            state="disabled",
        )
        self.open_output_button.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        self.build_progress_section(container)

    def _toggle_mapping(self):
        state = "normal" if self.mapping_var.get() else "disabled"
        self.mapping_entry.configure(state=state)
        self.mapping_button.configure(state=state)

    def select_db_file(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
        )
        if filename:
            self.db_path_var.set(filename)

    def select_mapping_file(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar CSV de mapeo",
            filetypes=[("CSV", "*.csv")],
        )
        if filename:
            self.mapping_path_var.set(filename)

    def select_output_dir(self):
        directory = filedialog.askdirectory(parent=self, title="Seleccionar carpeta de salida")
        if directory:
            self.output_dir_var.set(directory)

    def open_output_folder(self):
        path = self.output_dir_var.get()
        if path:
            import subprocess
            import sys

            folder = Path(path)
            if folder.exists():
                if sys.platform == "win32":
                    os.startfile(str(folder))  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    subprocess.call(["open", str(folder)])
                else:
                    subprocess.call(["xdg-open", str(folder)])

    def _validate_inputs(self) -> Optional[dict]:
        errors = False
        self.db_error.configure(text="")
        self.output_error.configure(text="")
        self.links_error.configure(text="")
        self.mapping_error.configure(text="")

        try:
            year = int(self.year_var.get())
        except ValueError:
            self.logger.error("El año debe ser un número entero")
            return None
        cohort = self.cohort_var.get().strip()
        modality = self.modality_var.get().strip()
        output_dir = Path(self.output_dir_var.get()).expanduser()
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                self.output_error.configure(text=str(exc))
                errors = True
        db_path = Path(self.db_path_var.get())
        if not db_path.exists():
            self.db_error.configure(text="Seleccione un CSV válido")
            errors = True
        links = [line.strip() for line in self.links_text.get("1.0", "end").splitlines() if line.strip()]
        for link in links:
            parsed = urlparse(link)
            if parsed.scheme not in {"http", "https"}:
                self.links_error.configure(text=f"URL inválida: {link}")
                errors = True
                break
        mapping_path = None
        if self.mapping_var.get():
            mapping_path = Path(self.mapping_path_var.get())
            if not mapping_path.exists():
                self.mapping_error.configure(text="Archivo de mapeo requerido")
                errors = True
        if errors:
            return None
        if not self.user_var.get().strip() or not self.password_var.get():
            messagebox.showerror(
                "Credenciales requeridas",
                "Ingrese usuario y contraseña de Moodle",
            )
            return None
        return {
            "year": year,
            "cohort": cohort,
            "modality": modality,
            "output_dir": output_dir,
            "db_path": db_path,
            "links": links,
            "mapping_path": mapping_path,
            "url_moodle": self.url_moodle_var.get().strip(),
            "username": self.user_var.get().strip(),
            "password": self.password_var.get(),
        }

    def start_download(self):
        params = self._validate_inputs()
        if not params:
            return
        widgets = [self.start_button]
        self.disable_inputs(widgets)
        self.open_output_button.configure(state="disabled")
        self.set_status("Descargando certificados...")
        self.run_in_thread(lambda: self._process(params), on_finish=lambda: self.enable_inputs(widgets))

    def _process(self, params: dict):
        try:
            output_dir = params["output_dir"]
            csv_path = params["db_path"]
            modality = params["modality"]
            year = params["year"]
            cohort = params["cohort"]
            url_base = params["url_moodle"]
            username = params["username"]
            password = params["password"]
            mapping_path = params.get("mapping_path")
            links = list(params.get("links", []))

            csv_df = pd.read_csv(csv_path, dtype=str).fillna("")
            lower_columns = {col.lower() for col in csv_df.columns}
            missing_cols = REQUIRED_COLUMNS - lower_columns
            if missing_cols:
                msg = f"Faltan columnas obligatorias: {', '.join(missing_cols)}"
                self.logger.error(msg)
                self.after(0, lambda: messagebox.showerror("Error", msg))
                return
            csv_df.columns = [col.lower() for col in csv_df.columns]

            mapping: Dict[str, str] = {}
            if mapping_path:
                mapping_df = pd.read_csv(mapping_path, dtype=str).fillna("")
                if "dni" in [c.lower() for c in mapping_df.columns]:
                    dni_col = next(col for col in mapping_df.columns if col.lower() == "dni")
                    url_col = next(
                        (
                            col
                            for col in mapping_df.columns
                            if col.lower() in {"url", "link", "certificado"}
                        ),
                        None,
                    )
                    if url_col:
                        mapping = dict(
                            zip(
                                mapping_df[dni_col].astype(str),
                                mapping_df[url_col].astype(str),
                            )
                        )

            records = csv_df.to_dict("records")
            total = len(records)
            self.after(0, lambda: self.set_progress(0, total))
            self.after(0, lambda: self.set_status("Iniciando sesión en Moodle"))

            session = requests.Session()
            login_url = url_base.rstrip("/") + "/login/index.php"
            try:
                login_resp = session.post(
                    login_url,
                    data={"username": username, "password": password},
                    timeout=20,
                )
            except requests.RequestException as exc:
                self.logger.error("Error al conectarse a Moodle: %s", exc)
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"No fue posible conectar a Moodle: {exc}"
                    ),
                )
                return
            if login_resp.status_code != 200:
                self.logger.error(
                    "Credenciales inválidas o error de login (%s)", login_resp.status_code
                )
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", "No se pudo iniciar sesión en Moodle."
                    ),
                )
                return

            temp_root = ensure_directory(output_dir / "_temp_certificados")
            log_rows = []
            successes = 0
            failures = 0

            for index, record in enumerate(records, start=1):
                dni = str(record.get("dni", "")).strip()
                course = record.get("curso", "")
                province = record.get("provincia", "Provincia")
                name = record.get("nombre_completo", "")
                url = mapping.get(dni) or (links.pop(0) if links else "")
                if not url:
                    self.logger.warning("No se encontró URL para DNI %s", dni)
                    log_rows.append(
                        [
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            dni,
                            course,
                            province,
                            "",
                            "URL no disponible",
                            "",
                        ]
                    )
                    failures += 1
                    self.after(0, lambda idx=index: self.set_progress(idx, total))
                    continue

                province_dir = ensure_directory(temp_root / safe_filename(province))
                course_dir = ensure_directory(province_dir / safe_filename(course))
                base_filename = f"{safe_filename(dni or 'sin_dni')}_{safe_filename(course)}.pdf"
                output_file = course_dir / base_filename
                output_file = unique_path(output_file)

                content = self._download_pdf(session, url)
                if content is None:
                    self.logger.error("No se pudo descargar el certificado para %s", dni or name)
                    log_rows.append(
                        [
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            dni,
                            course,
                            province,
                            url,
                            "Fallo",
                            "",
                        ]
                    )
                    failures += 1
                else:
                    with output_file.open("wb") as f:
                        f.write(content)
                    log_rows.append(
                        [
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            dni,
                            course,
                            province,
                            url,
                            "OK",
                            str(output_file),
                        ]
                    )
                    successes += 1
                self.after(0, lambda idx=index: self.set_progress(idx, total))

            self._create_zip_structure(temp_root, output_dir, modality, year, cohort)
            log_path = output_dir / "log_descargas.csv"
            if log_rows:
                csv_utils.append_csv(log_path, LOG_HEADERS, log_rows)
            elif not log_path.exists():
                csv_utils.write_csv(log_path, LOG_HEADERS, [])
            self.after(0, lambda: self.open_output_button.configure(state="normal"))
            self.after(
                0,
                lambda: self.set_status(
                    f"Finalizado. OK: {successes} - Errores: {failures}"
                ),
            )
            config_module.update_common_parameters(
                self.config_manager,
                year=params["year"],
                cohort=params["cohort"],
                modality=params["modality"],
                output_dir=output_dir,
                url_moodle_base=url_base,
            )
        except Exception as exc:
            self.logger.exception("Error inesperado durante la descarga de certificados", exc_info=exc)
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))

    def _download_pdf(self, session: requests.Session, url: str) -> Optional[bytes]:
        for attempt in range(1, 4):
            try:
                response = session.get(url, timeout=30)
            except requests.RequestException as exc:
                self.logger.warning("Intento %s fallido para %s: %s", attempt, url, exc)
                time.sleep(attempt)
                continue
            if response.status_code == 200 and "pdf" in response.headers.get("Content-Type", "").lower():
                return response.content
            self.logger.warning(
                "Intento %s fallido para %s: status %s", attempt, url, response.status_code
            )
            time.sleep(attempt)
        return None

    def _create_zip_structure(self, temp_root: Path, output_dir: Path, modality: str, year: int, cohort: str):
        jurisd_dir = ensure_directory(output_dir / "jurisdicciones")
        for province_dir in temp_root.iterdir():
            if not province_dir.is_dir():
                continue
            zip_name = f"{safe_filename(modality)}_{year}_{safe_filename(cohort)}.zip"
            province_zip_dir = ensure_directory(jurisd_dir / province_dir.name)
            zip_path = province_zip_dir / zip_name
            with ZipFile(zip_path, "w") as zipf:
                for file in province_dir.rglob("*.pdf"):
                    arcname = Path(file.relative_to(province_dir))
                    zipf.write(file, arcname=arcname)
        # Clean temp directory
        import shutil

        shutil.rmtree(temp_root, ignore_errors=True)

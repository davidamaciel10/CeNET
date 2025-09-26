from __future__ import annotations

import os
import re
import shutil
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Tuple
from zipfile import ZipFile

import pandas as pd
import pdfplumber

from .. import config as config_module
from ..utils import csv_utils, pdf
from ..utils.paths import ensure_directory, safe_filename, unique_path
from .base import BaseFlowWindow

REQUIRED_COLUMNS = {"dni", "nombre_completo", "provincia", "curso", "comision", "estado"}
APPROVED_KEYWORDS = ("aproba", "promo")


class RecordsWindow(BaseFlowWindow):
    def __init__(self, master, config, logger):
        super().__init__(master, config, logger, "Exportar actas")
        self.modalities = config_module.get_modalities(self.config_manager)
        self.files: List[str] = []
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        self.build_common_section(container, self.modalities)

        files_frame = ttk.LabelFrame(container, text="Actas de origen")
        files_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        files_frame.columnconfigure(0, weight=1)
        self.files_list = tk.Listbox(files_frame, height=6, selectmode=tk.EXTENDED)
        self.files_list.grid(row=0, column=0, sticky="nsew")
        button_column = ttk.Frame(files_frame)
        button_column.grid(row=0, column=1, padx=5, sticky="ns")
        ttk.Button(button_column, text="Agregar", command=self.add_files).grid(
            row=0, column=0, sticky="ew", pady=(0, 5)
        )
        ttk.Button(button_column, text="Quitar", command=self.remove_selected).grid(
            row=1, column=0, sticky="ew"
        )
        self.files_error = ttk.Label(files_frame, foreground="red")
        self.files_error.grid(row=1, column=0, columnspan=2, sticky="w")

        output_frame = ttk.LabelFrame(container, text="Salida")
        output_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
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

        control_frame = ttk.Frame(container)
        control_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        control_frame.columnconfigure(0, weight=1)
        self.start_button = ttk.Button(control_frame, text="Exportar", command=self.start_export)
        self.start_button.grid(row=0, column=0, sticky="ew")
        self.open_output_button = ttk.Button(
            control_frame,
            text="Abrir carpeta de salida",
            command=self.open_output_folder,
            state="disabled",
        )
        self.open_output_button.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        self.build_progress_section(container)

    def add_files(self):
        filenames = filedialog.askopenfilenames(
            parent=self,
            title="Seleccionar actas",
            filetypes=[("Archivos permitidos", "*.csv *.pdf"), ("CSV", "*.csv"), ("PDF", "*.pdf")],
        )
        for name in filenames:
            if name not in self.files:
                self.files.append(name)
                self.files_list.insert("end", name)

    def remove_selected(self):
        selection = list(self.files_list.curselection())
        selection.reverse()
        for index in selection:
            self.files_list.delete(index)
            del self.files[index]

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
        self.files_error.configure(text="")
        self.output_error.configure(text="")
        if not self.files:
            self.files_error.configure(text="Seleccione al menos un archivo")
            return None
        try:
            year = int(self.year_var.get())
        except ValueError:
            self.logger.error("El año debe ser numérico")
            return None
        cohort = self.cohort_var.get().strip()
        modality = self.modality_var.get().strip()
        output_dir = Path(self.output_dir_var.get()).expanduser()
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                self.output_error.configure(text=str(exc))
                return None
        return {
            "year": year,
            "cohort": cohort,
            "modality": modality,
            "output_dir": output_dir,
            "files": list(self.files),
        }

    def start_export(self):
        params = self._validate_inputs()
        if not params:
            return
        widgets = [self.start_button]
        self.disable_inputs(widgets)
        self.open_output_button.configure(state="disabled")
        self.set_status("Procesando actas...")
        self.run_in_thread(lambda: self._process(params), on_finish=lambda: self.enable_inputs(widgets))

    def _process(self, params: dict):
        try:
            output_dir: Path = params["output_dir"]
            files: List[str] = params["files"]
            year = params["year"]
            cohort = params["cohort"]
            modality = params["modality"]

            actas_temp = ensure_directory(output_dir / "_temp_actas")
            jurisd_temp = ensure_directory(output_dir / "_temp_jurisdicciones")
            parse_errors: List[str] = []
            summary_rows: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
            totals: Dict[Tuple[str, str], Dict[str, object]] = defaultdict(
                lambda: {"aprobados": 0, "no_aprobados": 0, "comisiones": set()}
            )
            total_files = len(files)
            self.after(0, lambda: self.set_progress(0, total_files))

            for index, file_path in enumerate(files, start=1):
                path = Path(file_path)
                suffix = path.suffix.lower()
                if suffix == ".csv":
                    result = self._process_csv(path, actas_temp, year, cohort, modality)
                    if result is None:
                        return
                    records, pdf_path, course, comision = result
                elif suffix == ".pdf":
                    result = self._process_pdf(path, actas_temp)
                    if result is None:
                        parse_errors.append(f"No se pudo parsear {path.name}")
                        continue
                    records, pdf_path, course, comision = result
                else:
                    self.logger.warning("Formato no soportado: %s", path)
                    continue

                for row in records:
                    province = row.get("provincia", "Provincia")
                    course_name = row.get("curso", course)
                    key = (province, course_name)
                    estado = str(row.get("estado", "")).lower()
                    aprobado = any(keyword in estado for keyword in APPROVED_KEYWORDS)
                    if aprobado:
                        summary_rows[key].append(row)
                        totals[key]["aprobados"] = totals[key]["aprobados"] + 1
                    else:
                        totals[key]["no_aprobados"] = totals[key]["no_aprobados"] + 1
                    totals[key]["comisiones"].add(row.get("comision", comision))
                self.after(0, lambda idx=index: self.set_progress(idx, total_files))

            resumen_path = output_dir / "resumen_exportacion.csv"
            resumen_rows = []
            for (province, course_name), data in totals.items():
                aprobados = int(data["aprobados"])
                no_aprobados = int(data["no_aprobados"])
                comisiones = len(data["comisiones"])
                resumen_rows.append(
                    [province, course_name, aprobados, no_aprobados, comisiones]
                )
                province_dir = ensure_directory(jurisd_temp / safe_filename(province))
                pdf_name = f"{safe_filename(course_name)}_aprobados.pdf"
                pdf_path = province_dir / pdf_name
                metadata = {
                    "Año": str(year),
                    "Cohorte": cohort,
                    "Modalidad": modality,
                    "Provincia": province,
                    "Curso": course_name,
                    "Fecha de exportación": pdf.timestamp_now(),
                    "Total aprobados": str(aprobados),
                }
                pdf.create_aprobados_pdf(
                    pdf_path,
                    summary_rows.get((province, course_name), []),
                    metadata,
                )

            csv_utils.write_csv(
                resumen_path,
                ["Provincia", "Curso", "Aprobados", "No Aprobados", "Comisiones procesadas"],
                resumen_rows,
            )

            self._zip_jurisdicciones(jurisd_temp, output_dir, modality, year, cohort)
            self._zip_actas(actas_temp, output_dir, modality, year, cohort)

            if parse_errors:
                log_path = output_dir / "log_parseo.txt"
                ensure_directory(log_path.parent)
                log_path.write_text("\n".join(parse_errors), encoding="utf-8")

            self.after(0, lambda: self.open_output_button.configure(state="normal"))
            self.after(0, lambda: self.set_status("Exportación finalizada"))
            config_module.update_common_parameters(
                self.config_manager,
                year=year,
                cohort=cohort,
                modality=modality,
                output_dir=output_dir,
            )
        except Exception as exc:
            self.logger.exception("Error durante la exportación", exc_info=exc)
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            shutil.rmtree(output_dir / "_temp_actas", ignore_errors=True)
            shutil.rmtree(output_dir / "_temp_jurisdicciones", ignore_errors=True)

    def _process_csv(
        self,
        path: Path,
        actas_temp: Path,
        year: int,
        cohort: str,
        modality: str,
    ) -> Optional[Tuple[List[dict], Path, str, str]]:
        df = pd.read_csv(path, dtype=str).fillna("")
        lower_columns = {col.lower() for col in df.columns}
        missing = REQUIRED_COLUMNS - lower_columns
        if missing:
            msg = f"El archivo {path.name} no tiene columnas: {', '.join(missing)}"
            self.logger.error(msg)
            self.after(0, lambda: messagebox.showerror("Error", msg))
            return None
        df.columns = [col.lower() for col in df.columns]
        records = df.to_dict("records")
        course = records[0].get("curso", path.stem) if records else path.stem
        comision = records[0].get("comision", "Comision") if records else "Comision"
        course_dir = ensure_directory(actas_temp / safe_filename(course))
        comision_dir = ensure_directory(course_dir / safe_filename(comision))
        pdf_name = f"{safe_filename(course)}_{safe_filename(comision)}.pdf"
        output_pdf = unique_path(comision_dir / pdf_name)
        metadata = {
            "Titulo": f"Acta {course} - {comision}",
            "Año": str(year),
            "Cohorte": cohort,
            "Modalidad": modality,
        }
        pdf.convert_csv_to_pdf(records, df.columns, output_pdf, metadata)
        return records, output_pdf, course, comision

    def _process_pdf(self, path: Path, actas_temp: Path):
        try:
            with pdfplumber.open(path) as pdf_file:
                pages_text = [page.extract_text() or "" for page in pdf_file.pages]
        except Exception as exc:
            self.logger.warning("No se pudo abrir %s: %s", path, exc)
            destination = self._copy_original_pdf(path, actas_temp)
            return None
        text = "\n".join(pages_text)
        rows = self._extract_rows_from_text(text)
        if not rows:
            destination = self._copy_original_pdf(path, actas_temp)
            return None
        course = rows[0].get("curso", path.stem)
        comision = rows[0].get("comision", "Comision")
        destination_dir = ensure_directory(actas_temp / safe_filename(course) / safe_filename(comision))
        destination = unique_path(destination_dir / path.name)
        shutil.copy2(path, destination)
        return rows, destination, course, comision

    def _copy_original_pdf(self, path: Path, actas_temp: Path) -> Path:
        destination_dir = ensure_directory(actas_temp / "sin_identificar")
        destination = unique_path(destination_dir / path.name)
        shutil.copy2(path, destination)
        return destination

    def _extract_rows_from_text(self, text: str) -> List[dict]:
        rows: List[dict] = []
        for line in text.splitlines():
            parts = [part.strip() for part in re.split(r"[;,\t]", line) if part.strip()]
            if len(parts) < 6:
                continue
            dni, nombre, provincia, curso, comision, estado, *rest = parts
            nota = rest[0] if rest else ""
            if not re.fullmatch(r"\d{6,}", dni):
                continue
            rows.append(
                {
                    "dni": dni,
                    "nombre_completo": nombre,
                    "provincia": provincia,
                    "curso": curso,
                    "comision": comision,
                    "estado": estado,
                    "nota": nota,
                }
            )
        return rows

    def _zip_jurisdicciones(
        self,
        temp_dir: Path,
        output_dir: Path,
        modality: str,
        year: int,
        cohort: str,
    ) -> None:
        jurisd_dir = ensure_directory(output_dir / "jurisdicciones")
        zip_name = f"{safe_filename(modality)}_{year}_{safe_filename(cohort)}.zip"
        for province_dir in temp_dir.iterdir():
            if not province_dir.is_dir():
                continue
            province_zip_dir = ensure_directory(jurisd_dir / province_dir.name)
            zip_path = province_zip_dir / zip_name
            with ZipFile(zip_path, "w") as zipf:
                for file in province_dir.rglob("*.pdf"):
                    arcname = Path(file.relative_to(province_dir))
                    zipf.write(file, arcname)

    def _zip_actas(
        self,
        temp_dir: Path,
        output_dir: Path,
        modality: str,
        year: int,
        cohort: str,
    ) -> None:
        actas_dir = ensure_directory(output_dir / "actas")
        zip_name = f"{safe_filename(modality)}_{year}_{safe_filename(cohort)}.zip"
        zip_path = actas_dir / zip_name
        with ZipFile(zip_path, "w") as zipf:
            for file in temp_dir.rglob("*.pdf"):
                arcname = Path(file.relative_to(temp_dir))
                zipf.write(file, arcname)

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Iterable, List, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .paths import ensure_directory

TZ = dt.timezone(dt.timedelta(hours=-3), name="America/Argentina/Buenos_Aires")


def _default_styles():
    styles = getSampleStyleSheet()
    title = styles["Heading2"].clone("CustomTitle")
    title.alignment = 1
    body = styles["BodyText"]
    return title, body


def render_table_pdf(
    output_path: Path,
    title_text: str,
    headers: Sequence[str],
    rows: Iterable[Sequence[str]],
    metadata: dict[str, str] | None = None,
    landscape_mode: bool = False,
) -> None:
    ensure_directory(output_path.parent)
    pagesize = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(str(output_path), pagesize=pagesize)
    story: List = []
    title_style, body_style = _default_styles()
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.25 * cm))
    if metadata:
        for key, value in metadata.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", body_style))
        story.append(Spacer(1, 0.25 * cm))
    data = [list(headers)] + [list(row) for row in rows]
    if len(data) == 1:
        data.append(["Sin datos"] + [""] * (len(headers) - 1))
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B6E99")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ]
        )
    )
    story.append(table)
    doc.build(story)


def convert_csv_to_pdf(csv_rows: List[dict], headers: Sequence[str], output_pdf: Path, metadata: dict[str, str]) -> None:
    rows = [[str(row.get(header, "")) for header in headers] for row in csv_rows]
    render_table_pdf(
        output_pdf,
        title_text=metadata.get("Titulo", "Acta"),
        headers=headers,
        rows=rows,
        metadata={k: v for k, v in metadata.items() if k != "Titulo"},
        landscape_mode=True,
    )


def create_aprobados_pdf(
    output_path: Path,
    rows: List[dict],
    metadata: dict[str, str],
) -> None:
    headers = ["DNI", "Nombre", "Curso", "Comisión", "Nota"]
    formatted_rows = []
    for row in rows:
        formatted_rows.append(
            [
                str(row.get("dni", "")),
                str(row.get("nombre_completo", "")),
                str(row.get("curso", "")),
                str(row.get("comision", "")),
                str(row.get("nota", "")),
            ]
        )
    render_table_pdf(output_path, "Aprobados", headers, formatted_rows, metadata)


def timestamp_now() -> str:
    now = dt.datetime.now(tz=TZ)
    return now.strftime("%d/%m/%Y %H:%M")

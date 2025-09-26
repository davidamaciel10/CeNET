from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile


def validate_certificates_structure(output_dir: Path) -> dict[str, bool]:
    result = {
        "jurisdicciones": False,
        "log_descargas": False,
    }
    output_dir = Path(output_dir)
    jurisd_dir = output_dir / "jurisdicciones"
    if jurisd_dir.exists() and any(jurisd_dir.iterdir()):
        result["jurisdicciones"] = True
        for province in jurisd_dir.iterdir():
            if province.is_dir():
                for zip_file in province.glob("*.zip"):
                    with ZipFile(zip_file) as zf:
                        if not any(name.lower().endswith(".pdf") for name in zf.namelist()):
                            raise AssertionError(f"El zip {zip_file} no contiene PDFs")
    log_file = output_dir / "log_descargas.csv"
    result["log_descargas"] = log_file.exists()
    return result


def validate_actas_structure(output_dir: Path) -> dict[str, bool]:
    result = {
        "jurisdicciones": False,
        "actas_zip": False,
        "resumen": False,
    }
    output_dir = Path(output_dir)
    jurisd_dir = output_dir / "jurisdicciones"
    actas_dir = output_dir / "actas"
    resumen = output_dir / "resumen_exportacion.csv"
    if jurisd_dir.exists() and any(jurisd_dir.iterdir()):
        result["jurisdicciones"] = True
    if actas_dir.exists():
        zip_files = list(actas_dir.glob("*.zip"))
        if zip_files:
            result["actas_zip"] = True
            for zip_path in zip_files:
                with ZipFile(zip_path) as zf:
                    if not any(name.lower().endswith(".pdf") for name in zf.namelist()):
                        raise AssertionError(f"El zip {zip_path} no contiene PDFs")
    result["resumen"] = resumen.exists()
    return result


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Valida la estructura de salida generada por la app")
    parser.add_argument("tipo", choices=["certificados", "actas"], help="Tipo de validación")
    parser.add_argument("directorio", help="Ruta a la carpeta de salida")
    args = parser.parse_args()

    output = (
        validate_certificates_structure(Path(args.directorio))
        if args.tipo == "certificados"
        else validate_actas_structure(Path(args.directorio))
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))

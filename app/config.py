from __future__ import annotations

import configparser
from pathlib import Path
from typing import List, Tuple

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.ini"
DEFAULT_MODALITIES = ["Virtual", "Presencial", "Bimodal"]
_DEFAULTS = {
    "general": {
        "url_moodle_base": "https://campus.ejemplo.edu",
        "ultima_salida": str(Path.home()),
        "anio": "2025",
        "cohorte": "Cohorte 1",
        "modalidad": DEFAULT_MODALITIES[0],
        "modalidades": ",".join(DEFAULT_MODALITIES),
    }
}


def load_config() -> configparser.ConfigParser:
    """Load configuration from disk, creating defaults if necessary."""
    config = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        config.read(CONFIG_PATH, encoding="utf-8")
    for section, values in _DEFAULTS.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in values.items():
            if not config.has_option(section, key):
                config.set(section, key, value)
    save_config(config)
    return config


def save_config(config: configparser.ConfigParser) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        config.write(f)


def get_modalities(config: configparser.ConfigParser) -> List[str]:
    raw = config.get("general", "modalidades", fallback=",")
    modalities = [item.strip() for item in raw.split(",") if item.strip()]
    return modalities or DEFAULT_MODALITIES


def update_common_parameters(
    config: configparser.ConfigParser,
    year: int,
    cohort: str,
    modality: str,
    output_dir: Path | None = None,
    url_moodle_base: str | None = None,
) -> None:
    config.set("general", "anio", str(year))
    config.set("general", "cohorte", cohort)
    config.set("general", "modalidad", modality)
    if output_dir is not None:
        config.set("general", "ultima_salida", str(output_dir))
    if url_moodle_base:
        config.set("general", "url_moodle_base", url_moodle_base)
    save_config(config)


def read_common_parameters(
    config: configparser.ConfigParser,
) -> Tuple[int, str, str, Path, str]:
    year = config.getint("general", "anio", fallback=2025)
    cohort = config.get("general", "cohorte", fallback="Cohorte 1")
    modality = config.get("general", "modalidad", fallback=DEFAULT_MODALITIES[0])
    last_output = Path(config.get("general", "ultima_salida", fallback=str(Path.home())))
    url_moodle = config.get("general", "url_moodle_base", fallback=_DEFAULTS["general"]["url_moodle_base"])
    return year, cohort, modality, last_output, url_moodle


def update_modalities(config: configparser.ConfigParser, modalities: List[str]) -> None:
    config.set("general", "modalidades", ",".join(modalities))
    save_config(config)

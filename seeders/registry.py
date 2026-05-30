from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
SEEDERS_DIR = Path(__file__).resolve().parent
SEEDER_LOG_FILE = ROOT / "seeders" / "executed_seeders.log"
SEEDER_MODULE_PREFIX = "seed_"


@dataclass(frozen=True)
class SeederDefinition:
    key: str
    title: str
    description: str
    runner: Callable[[], None]
    module_name: str


def ensure_log_file() -> None:
    SEEDER_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEDER_LOG_FILE.touch(exist_ok=True)


def read_executed_seeders() -> set[str]:
    ensure_log_file()
    executed: set[str] = set()

    with SEEDER_LOG_FILE.open("r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            if not line:
                continue

            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 3 and parts[2].lower() == "success":
                executed.add(parts[1])

    return executed


def append_seed_log(seeder_key: str, status: str, message: str = "") -> None:
    ensure_log_file()
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} | {seeder_key} | {status} | {message}".rstrip() + "\n"
    with SEEDER_LOG_FILE.open("a", encoding="utf-8") as file_handle:
        file_handle.write(line)


def _format_title(module_name: str) -> str:
    cleaned = module_name.removeprefix(SEEDER_MODULE_PREFIX)
    words = [part for part in cleaned.replace("_", " ").split(" ") if part]
    return " ".join(word.capitalize() for word in words) or module_name


def _load_seeder_from_module(module_name: str) -> SeederDefinition | None:
    module = importlib.import_module(f"seeders.{module_name}")
    runner = getattr(module, "run", None) or getattr(module, "seed", None)
    if not callable(runner):
        return None

    title = getattr(module, "SEEDER_TITLE", None) or _format_title(module_name)
    description = getattr(module, "SEEDER_DESCRIPTION", None) or (inspect.getdoc(module) or "")
    return SeederDefinition(
        key=module_name,
        title=title,
        description=description.strip(),
        runner=runner,
        module_name=module_name,
    )


def discover_seeders() -> list[SeederDefinition]:
    seeders: list[SeederDefinition] = []
    for module_info in pkgutil.iter_modules([str(SEEDERS_DIR)]):
        if module_info.name == "registry" or not module_info.name.startswith(SEEDER_MODULE_PREFIX):
            continue

        try:
            seeder = _load_seeder_from_module(module_info.name)
        except Exception as exc:  # noqa: BLE001
            append_seed_log(module_info.name, "error", f"Import error: {exc}")
            continue

        if seeder:
            seeders.append(seeder)

    return sorted(seeders, key=lambda seeder: (seeder.title.lower(), seeder.key.lower()))


def get_seeder_by_key(seeder_key: str) -> SeederDefinition | None:
    return next((seeder for seeder in discover_seeders() if seeder.key == seeder_key), None)


def get_seeder_conflicts(seeder_key: str) -> list[str]:
    try:
        module = importlib.import_module(f"seeders.{seeder_key}")
    except Exception as exc:  # noqa: BLE001
        return [f"No se pudo cargar el seeder: {exc}"]

    preview = getattr(module, "preview_conflicts", None)
    if not callable(preview):
        return []

    try:
        conflicts = preview()
    except Exception as exc:  # noqa: BLE001
        return [f"No se pudieron evaluar conflictos: {exc}"]

    if not conflicts:
        return []

    return [str(conflict) for conflict in conflicts]


def run_seeder(seeder_key: str, *, force: bool = False) -> tuple[bool, str]:
    seeder = get_seeder_by_key(seeder_key)
    if not seeder:
        return False, f"Seeder no encontrado: {seeder_key}"

    executed = read_executed_seeders()
    if seeder.key in executed and not force:
        return False, f"El seeder '{seeder.key}' ya fue ejecutado. Usa force si deseas repetirlo."

    try:
        seeder.runner()
        append_seed_log(seeder.key, "success", seeder.title)
        return True, f"Seeder ejecutado correctamente: {seeder.key}"
    except Exception as exc:  # noqa: BLE001
        append_seed_log(seeder.key, "error", str(exc))
        return False, f"Error ejecutando {seeder.key}: {exc}"


def run_pending_seeders() -> list[tuple[str, bool, str]]:
    executed = read_executed_seeders()
    results: list[tuple[str, bool, str]] = []

    for seeder in discover_seeders():
        if seeder.key in executed:
            results.append((seeder.key, False, "Ya ejecutado"))
            continue

        success, message = run_seeder(seeder.key)
        results.append((seeder.key, success, message))

    return results


def get_seeders_summary() -> list[dict[str, str]]:
    return [
        {
            "key": seeder.key,
            "title": seeder.title,
            "description": seeder.description,
        }
        for seeder in discover_seeders()
    ]

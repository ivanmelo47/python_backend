#!/usr/bin/env python3
"""Create the project .venv with an overwrite confirmation if it already exists."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def prompt_yes_no(message: str) -> bool:
    answer = input(f"{message} (s/N): ").strip().lower()
    return answer in {"s", "si", "y", "yes"}


def remove_existing_venv() -> None:
    if VENV_DIR.is_dir():
        shutil.rmtree(VENV_DIR)
    elif VENV_DIR.exists():
        VENV_DIR.unlink()


def get_existing_venv_python() -> Path | None:
    candidates = [
        VENV_DIR / "Scripts" / "python.exe",
        VENV_DIR / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def show_existing_venv_details() -> None:
    python_executable = get_existing_venv_python()
    if python_executable is None:
        print("[!] No se encontró el ejecutable de Python dentro de .venv")
        return

    print(f"[INFO] Python del entorno: {python_executable}")

    version_result = subprocess.run(
        [str(python_executable), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    version_output = (version_result.stdout or version_result.stderr).strip()
    if version_output:
        print(f"[INFO] {version_output}")

    pip_result = subprocess.run(
        [str(python_executable), "-m", "pip", "list", "--format=freeze"],
        capture_output=True,
        text=True,
        check=False,
    )
    packages = [line.strip() for line in pip_result.stdout.splitlines() if line.strip()]
    if packages:
        print("[INFO] Dependencias instaladas:")
        for package in packages:
            print(f"  - {package}")
    else:
        print("[INFO] No se pudieron leer dependencias instaladas o el entorno está vacío.")


def candidate_python_commands() -> list[list[str]]:
    candidates: list[list[str]] = []

    if os.name == "nt":
        candidates.extend([["py", "-3.13"], ["py", "-3"], [sys.executable]])
    else:
        candidates.extend([["python3"], [sys.executable]])

    unique_candidates: list[list[str]] = []
    seen: set[str] = set()
    for candidate in candidates:
        command = candidate[0]
        if command in seen:
            continue
        seen.add(command)
        unique_candidates.append(candidate)

    return unique_candidates


def create_venv() -> None:
    for candidate in candidate_python_commands():
        try:
            subprocess.run([*candidate, "-m", "venv", str(VENV_DIR)], check=True)
            return
        except FileNotFoundError:
            continue
        except subprocess.CalledProcessError:
            raise

    print("[!] No se encontró un intérprete de Python adecuado para crear .venv.")
    sys.exit(1)


def main() -> None:
    if VENV_DIR.exists():
        print(f"[!] Ya existe {VENV_DIR}")
        show_existing_venv_details()
        if not prompt_yes_no("¿Quieres rehacerlo?"):
            print("[OK] No se hicieron cambios.")
            return

        print("[OK] Eliminando el entorno virtual existente...")
        remove_existing_venv()

    print("[OK] Creando .venv...")
    create_venv()
    print(f"[OK] Entorno virtual creado en {VENV_DIR}")


if __name__ == "__main__":
    main()
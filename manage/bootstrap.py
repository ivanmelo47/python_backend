from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"


def ensure_venv_and_restart() -> None:
    current_python = Path(sys.executable).resolve()

    candidates = [
        VENV_DIR / "Scripts" / "python.exe",
        VENV_DIR / "bin" / "python",
    ]
    venv_python = None
    for candidate in candidates:
        if candidate.exists():
            venv_python = candidate.resolve()
            break

    if not venv_python:
        print("[!] No se encontro el entorno virtual (.venv).")
        ans = input("¿Deseas crearlo usando create_venv.py? (s/N): ").strip().lower()
        if ans in {"s", "si", "y", "yes"}:
            try:
                subprocess.run([sys.executable, "create_venv.py"], check=True)
                for candidate in candidates:
                    if candidate.exists():
                        venv_python = candidate.resolve()
                        break
                if venv_python:
                    print("\n[INFO] Recuerda instalar las dependencias si es un entorno nuevo.")
                    print("[INFO] Comando: pip install -r requirements.txt")
                    input("Presiona Enter para continuar...")
            except subprocess.CalledProcessError:
                print("[!] Error al crear el entorno virtual.")
                sys.exit(1)

        if not venv_python:
            print("[!] Se requiere un entorno virtual. Saliendo.")
            sys.exit(1)

    def is_same_path(p1: Path, p2: Path) -> bool:
        try:
            if os.name == "nt":
                return str(p1).lower() == str(p2).lower()
            return p1 == p2
        except Exception:
            return False

    if not is_same_path(current_python, venv_python):
        print(f"[INFO] Reiniciando manage.py usando {venv_python}")
        sys.exit(subprocess.run([str(venv_python), *sys.argv]).returncode)

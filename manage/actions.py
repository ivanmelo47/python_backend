from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from app.core.settings import settings

ROOT = Path(__file__).resolve().parent.parent


def run_alembic(args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        check=True,
        capture_output=capture_output,
        text=True,
    )


def generate_jwt_secret() -> None:
    new_key = secrets.token_hex(32)
    print(f"\nNuevo JWT Secret Key generado: {new_key}")

    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            key_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith("JWT_SECRET_KEY="):
                    newline = "\n" if line.endswith("\n") else ""
                    lines[i] = f"JWT_SECRET_KEY={new_key}{newline}"
                    key_found = True
                    break

            if not key_found:
                if lines and not lines[-1].endswith("\n"):
                    lines.append("\n")
                lines.append(f"JWT_SECRET_KEY={new_key}\n")

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            print(f"[OK] Se ha actualizado '{env_path}' con el nuevo JWT_SECRET_KEY.")
        except Exception as exc:
            print(f"[!] Error al actualizar el archivo '{env_path}': {exc}")
    else:
        print(f"[!] No se encontro el archivo '{env_path}'.")
        print("Puedes copiar el valor de arriba y agregarlo a tu configuracion manualmente.")


def run_app(*, host: str, port: int, reload_enabled: bool) -> None:
    args = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]
    if reload_enabled:
        args.append("--reload")
    subprocess.run(args, check=True)


def run_frontend() -> None:
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        print("[!] No se encontro la carpeta 'frontend'.")
        return

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    try:
        subprocess.run([npm_cmd, "run", "dev"], cwd=frontend_dir, check=True)
    except FileNotFoundError:
        print("[!] Node.js o npm no estan instalados o no estan en el PATH.")
    except KeyboardInterrupt:
        pass


def run_fullstack(*, host: str, port: int, reload_enabled: bool) -> None:
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        print("[!] No se encontro la carpeta 'frontend'. Solo se iniciara el backend.")
        run_app(host=host, port=port, reload_enabled=reload_enabled)
        return

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    print("[INFO] Iniciando Frontend (Vue) y Backend (FastAPI)...")

    backend_args = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]
    if reload_enabled:
        backend_args.append("--reload")

    try:
        backend_process = subprocess.Popen(backend_args)
        frontend_process = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)

        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidores...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()


def reset_database() -> None:
    if not all([settings.db_host, settings.db_port, settings.db_database, settings.db_username, settings.db_password]):
        raise RuntimeError("Faltan credenciales DB_* para reiniciar la base de datos.")

    admin_url = (
        f"{settings.db_scheme}://{settings.db_username}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/"
    )
    engine = create_engine(admin_url)

    with engine.begin() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS `{settings.db_database}`"))
        connection.execute(
            text(
                f"CREATE DATABASE `{settings.db_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
            )
        )


def reset_database_and_migrate() -> None:
    reset_database()
    run_alembic(["upgrade", "head"])

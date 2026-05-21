#!/usr/bin/env python3
"""Herramienta mínima de despliegue para este proyecto.

Comandos:
  init   - despliegue inicial: crea .env.docker si falta, construye imagen, levanta contenedor y aplica migraciones
  update - actualizar: reconstruye la imagen y aplica migraciones

Ejemplos:
  python deploy.py init
  python deploy.py update

Notas:
  - Usa `docker compose` si está disponible, si no intenta `docker-compose`.
  - Requiere que el servicio en `docker-compose.yml` se llame `web` (por defecto del repo).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_EXAMPLE = ROOT / ".env.docker.example"
ENV_DOCKER = ROOT / ".env.docker"


def which_docker_compose() -> list[str]:
    """Return the docker compose command as a list of args.

    Prefer `docker compose` (newer CLI), fall back to `docker-compose`.
    """
    try:
        subprocess.run(["docker", "compose", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ["docker", "compose"]
    except Exception:
        try:
            subprocess.run(["docker-compose", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ["docker-compose"]
        except Exception:
            print("Error: docker compose no encontrado. Instala Docker y docker-compose.")
            sys.exit(1)


def run(cmd: list[str], check: bool = True) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=check)


def ensure_env_docker() -> None:
    if ENV_DOCKER.exists():
        print(f"[OK] {ENV_DOCKER} existe.")
        return

    if not ENV_EXAMPLE.exists():
        print(f"No se encontro {ENV_EXAMPLE}. Crea manualmente {ENV_DOCKER} antes de continuar.")
        sys.exit(1)

    shutil.copy(ENV_EXAMPLE, ENV_DOCKER)
    print(f"Copiado {ENV_EXAMPLE} -> {ENV_DOCKER}. Revisa y actualiza las credenciales si es necesario.")


def compose_up(build: bool = True) -> None:
    base = which_docker_compose()
    env_arg: list[str] = []
    if ENV_DOCKER.exists():
        env_arg = ["--env-file", str(ENV_DOCKER)]
    cmd = base + env_arg + ["up", "-d"]
    if build:
        cmd += ["--build"]
    run(cmd)


def compose_exec(cmd_inside: list[str]) -> None:
    base = which_docker_compose()
    # exec runs inside an existing container; interpolation already happened at `up` time.
    cmd = base + ["exec", "web"] + cmd_inside
    run(cmd)


def init(args: argparse.Namespace) -> None:
    """Despliegue inicial."""
    ensure_env_docker()

    print("Construyendo y arrancando servicios (esto puede tardar)...")
    compose_up(build=True)

    if args.no_migrate:
        print("--no-migrate especificado, saltando migraciones.")
        return

    print("Ejecutando migraciones dentro del contenedor (manage.py migrar)...")
    try:
        compose_exec(["python", "manage.py", "migrar"])
        print("Migraciones aplicadas correctamente.")
    except subprocess.CalledProcessError:
        print("Error al aplicar migraciones. Intenta ejecutar 'docker-compose logs web' para ver errores.")


def update(args: argparse.Namespace) -> None:
    """Actualizar despliegue: reconstruir y aplicar migraciones."""
    print("Reconstruyendo e intentando actualizar el contenedor web...")
    # Rebuild only the web service to be faster
    base = which_docker_compose()
    env_arg: list[str] = []
    if ENV_DOCKER.exists():
        env_arg = ["--env-file", str(ENV_DOCKER)]
    try:
        run(base + env_arg + ["build", "web"])
    except subprocess.CalledProcessError:
        print("La reconstruccion falló. Intentando 'up --build' completo.")
        compose_up(build=True)

    # Restart the service
    run(base + env_arg + ["up", "-d", "--no-deps", "web"])

    if args.no_migrate:
        print("--no-migrate especificado, saltando migraciones.")
        return

    print("Ejecutando migraciones dentro del contenedor (manage.py migrar)...")
    try:
        compose_exec(["python", "manage.py", "migrar"])
        print("Migraciones aplicadas correctamente.")
    except subprocess.CalledProcessError:
        print("Error al aplicar migraciones. Revisa los logs del contenedor para diagnosticar.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Script de despliegue para el proyecto")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Despliegue inicial: crea .env.docker (si falta), build, up y migraciones")
    p_init.add_argument("--no-migrate", action="store_true", help="No ejecutar migraciones después de levantar los servicios")

    p_update = sub.add_parser("update", help="Actualizar: rebuild del servicio web y aplicar migraciones")
    p_update.add_argument("--no-migrate", action="store_true", help="No ejecutar migraciones después de actualizar")

    args = parser.parse_args()

    def show_menu() -> None:
        while True:
            print("\n=== Deploy Manager ===")
            print("1) Init (despliegue inicial)")
            print("2) Update (rebuild y migraciones)")
            print("0) Salir")
            opcion = input("Elige una opcion: ").strip()
            if opcion == "1":
                run_mig = input("Ejecutar migraciones despues de levantar? (S/n): ").strip().lower()
                class Args:  # simple namespace
                    pass
                ns = Args()
                ns.no_migrate = not (run_mig in {"", "s", "si", "y", "yes"})
                init(ns)
                continue
            if opcion == "2":
                run_mig = input("Ejecutar migraciones despues de actualizar? (S/n): ").strip().lower()
                class Args:
                    pass
                ns = Args()
                ns.no_migrate = not (run_mig in {"", "s", "si", "y", "yes"})
                update(ns)
                continue
            if opcion == "0":
                print("Saliendo.")
                return
            print("Opcion no valida.")

    # If no subcommand provided and running interactively, show menu
    if args.cmd is None:
        if sys.stdin.isatty():
            show_menu()
            return
        else:
            parser.print_help()
            return

    if args.cmd == "init":
        init(args)
    elif args.cmd == "update":
        update(args)


if __name__ == "__main__":
    main()

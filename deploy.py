#!/usr/bin/env python3
"""Herramienta mínima de despliegue para este proyecto.

Comandos:
  init   - despliegue inicial: crea .env.docker si falta, construye imagen, levanta contenedor y aplica migraciones
  update - actualizar: reconstruye la imagen y aplica migraciones
    install-service - instalar la app nativa como servicio systemd en Ubuntu
    migrate-ubuntu - ejecutar migraciones en Ubuntu usando .venv
    start-service - iniciar el servicio systemd
    stop-service - detener el servicio systemd
    restart-service - reiniciar el servicio systemd
    status-service - ver estado del servicio systemd
    uninstall-service - quitar el servicio systemd

Ejemplos:
  python deploy.py init
  python deploy.py update
    python deploy.py install-service
    python deploy.py migrate-ubuntu
    python deploy.py start-service
    python deploy.py stop-service

Notas:
  - Usa `docker compose` si está disponible, si no intenta `docker-compose`.
  - Requiere que el servicio en `docker-compose.yml` se llame `web` (por defecto del repo).
        - Los comandos disponibles fuera de Docker se limitan al modo Ubuntu/systemd y usan el Python de `.venv`.
        - Los comandos `systemd` son para Linux/Ubuntu.
"""

from __future__ import annotations

import argparse
import os
import signal
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_EXAMPLE = ROOT / ".env.docker.example"
ENV_DOCKER = ROOT / ".env.docker"
ENV_LOCAL = ROOT / ".env"
NATIVE_PID_FILE = ROOT / ".native-app.pid"
NATIVE_LOG_FILE = ROOT / "native-app.log"
DEFAULT_NATIVE_PORT = 8000
REQUIREMENTS_FILE = ROOT / "requirements.txt"
SYSTEMD_SERVICE_NAME = "python_backend.service"
SYSTEMD_SERVICE_PATH = Path("/etc/systemd/system") / SYSTEMD_SERVICE_NAME


def get_native_python_executable() -> str:
    """Return the Python executable from .venv so native commands stay isolated."""
    candidates = [
        ROOT / ".venv" / "Scripts" / "python.exe",
        ROOT / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    print("[!] No se encontró un entorno virtual en .venv. Crea/activa .venv antes de usar opciones nativas.")
    sys.exit(1)


def get_systemd_python_executable() -> str:
    """Return the .venv python for Linux/Ubuntu service installation."""
    candidates = [
        ROOT / ".venv" / "bin" / "python",
        ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    print("[!] No se encontró un entorno virtual en .venv para systemd.")
    sys.exit(1)


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


def read_env_file(path: Path) -> dict[str, str]:
    """Read a simple KEY=VALUE env file without comments or advanced shell syntax."""
    data: dict[str, str] = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        data[key] = value

    return data


def write_env_value(path: Path, key: str, value: str) -> None:
    lines: list[str] = []
    found = False
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith(f"{key}="):
            updated_lines.append(f"{key}={value}")
            found = True
        else:
            updated_lines.append(raw_line)

    if not found:
        if updated_lines and updated_lines[-1].strip():
            updated_lines.append("")
        updated_lines.append(f"{key}={value}")

    path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def regenerate_jwt_secret() -> str:
    return secrets.token_hex(32)


def maybe_regenerate_jwt_secret(target_path: Path, label: str) -> None:
    answer = input(f"¿Deseas generar un nuevo JWT_SECRET_KEY para {label}? (s/N): ").strip().lower()
    if answer not in {"s", "si", "y", "yes"}:
        return

    new_secret = regenerate_jwt_secret()
    write_env_value(target_path, "JWT_SECRET_KEY", new_secret)
    print(f"[OK] JWT_SECRET_KEY actualizado en {target_path}")
    print(f"[OK] Nuevo JWT_SECRET_KEY: {new_secret}")


def get_native_port(explicit_port: int | None = None) -> int:
    if explicit_port is not None:
        return explicit_port

    env_values = read_env_file(ENV_LOCAL)
    if not env_values.get("APP_PORT") and ENV_DOCKER.exists():
        env_values.update(read_env_file(ENV_DOCKER))

    env_port = os.environ.get("APP_PORT") or env_values.get("APP_PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass

    return DEFAULT_NATIVE_PORT


def read_pid_file() -> int | None:
    if not NATIVE_PID_FILE.exists():
        return None

    try:
        return int(NATIVE_PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def write_pid_file(pid: int) -> None:
    NATIVE_PID_FILE.write_text(str(pid), encoding="utf-8")


def remove_pid_file() -> None:
    if NATIVE_PID_FILE.exists():
        NATIVE_PID_FILE.unlink(missing_ok=True)


def is_windows() -> bool:
    return os.name == "nt"


def is_posix_root() -> bool:
    geteuid = getattr(os, "geteuid", None)
    return bool(geteuid and geteuid() == 0)


def maybe_sudo(cmd: list[str]) -> list[str]:
    if is_windows() or is_posix_root():
        return cmd
    sudo = shutil.which("sudo")
    if sudo:
        return [sudo, *cmd]
    return cmd


def find_pids_on_port(port: int) -> list[int]:
    if is_windows():
        result = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, check=False)
        pids: set[int] = set()
        for line in result.stdout.splitlines():
            normalized_line = line.strip()
            if f":{port} " not in normalized_line:
                continue
            parts = normalized_line.split()
            if len(parts) < 5:
                continue
            pid_text = parts[-1]
            state = parts[-2].upper()
            if state == "LISTENING":
                try:
                    pids.add(int(pid_text))
                except ValueError:
                    continue
        return sorted(pids)

    lsof = shutil.which("lsof")
    if not lsof:
        return []

    result = subprocess.run([lsof, "-ti", f"tcp:{port}"], capture_output=True, text=True, check=False)
    pids = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            pids.append(int(line))
        except ValueError:
            continue
    return sorted(set(pids))


def kill_process_tree(pid: int) -> None:
    if is_windows():
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True, text=True)
        return

    try:
        os.killpg(pid, signal.SIGTERM)
    except Exception:
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass


def release_port(port: int) -> list[int]:
    pids = find_pids_on_port(port)
    for pid in pids:
        kill_process_tree(pid)
    if not pids:
        print(f"[OK] El puerto {port} ya estaba libre.")
    else:
        print(f"[OK] Puerto {port} liberado. Procesos detenidos: {', '.join(map(str, pids))}")
    return pids


def start_native(args: argparse.Namespace) -> None:
    port = get_native_port(args.port)

    existing_pid = read_pid_file()
    if existing_pid:
        print(f"[!] Ya existe un PID registrado: {existing_pid}. Si sigue vivo, usa 'stop-native'.")

    if find_pids_on_port(port):
        if args.free_port:
            release_port(port)
            time.sleep(0.5)
        else:
            print(f"[!] El puerto {port} ya está ocupado. Usa 'free-port' o 'start-native --free-port'.")
            return

    env = os.environ.copy()
    env.update(read_env_file(ENV_LOCAL))
    env["APP_PORT"] = str(port)

    command = [
        get_native_python_executable(),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]
    if args.reload:
        command.append("--reload")

    log_file = NATIVE_LOG_FILE.open("a", encoding="utf-8")
    creationflags = 0
    popen_kwargs: dict[str, object] = {
        "cwd": ROOT,
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": log_file,
        "stderr": log_file,
        "text": True,
    }

    if is_windows():
        creationflags = 0
        for flag_name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
            creationflags |= getattr(subprocess, flag_name, 0)
        popen_kwargs["creationflags"] = creationflags
    else:
        popen_kwargs["start_new_session"] = True

    with NATIVE_LOG_FILE.open("a", encoding="utf-8") as log_file:
        popen_kwargs["stdout"] = log_file
        popen_kwargs["stderr"] = log_file
        process = subprocess.Popen(command, **popen_kwargs)

    write_pid_file(process.pid)
    print(f"[OK] App nativa iniciada en el puerto {port} con PID {process.pid}.")
    print(f"[OK] Logs: {NATIVE_LOG_FILE}")


def rebuild_native(args: argparse.Namespace) -> None:
    """Reinstala dependencias nativas; útil cuando cambian requirements o el entorno."""
    if not REQUIREMENTS_FILE.exists():
        print(f"[!] No se encontró {REQUIREMENTS_FILE}.")
        return

    print("Reinstalando dependencias nativas con pip...")
    run([get_native_python_executable(), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    print("[OK] Dependencias nativas actualizadas.")


def migrate_native(args: argparse.Namespace) -> None:
    """Ejecuta migraciones en la PC (sin Docker)."""
    print("Ejecutando migraciones nativas...")
    try:
        run([get_native_python_executable(), "manage.py", "migrar"])
        print("[OK] Migraciones nativas aplicadas correctamente.")
    except subprocess.CalledProcessError:
        print("[!] Error al aplicar migraciones nativas.")


def migrate_ubuntu(args: argparse.Namespace) -> None:
    """Ejecuta migraciones en Ubuntu usando la .venv del proyecto."""
    if is_windows():
        print("[!] Esta opción es para Ubuntu/Linux. En Windows usa migrate-native.")
        return

    print("Ejecutando migraciones en Ubuntu con la .venv...")
    try:
        run([get_systemd_python_executable(), "manage.py", "migrar"])
        print("[OK] Migraciones de Ubuntu aplicadas correctamente.")
    except subprocess.CalledProcessError:
        print("[!] Error al aplicar migraciones de Ubuntu.")


def build_systemd_service_content(port: int) -> str:
    python_executable = get_systemd_python_executable()
    working_directory = str(ROOT)
    service_user = os.environ.get("SUDO_USER") or os.environ.get("USER") or os.environ.get("USERNAME") or "ubuntu"

    return f"""[Unit]
Description=Python Backend API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={service_user}
Group={service_user}
WorkingDirectory={working_directory}
ExecStart={python_executable} -m uvicorn app.main:app --host 0.0.0.0 --port {port}
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""


def write_file_as_root(target_path: Path, content: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if is_posix_root() or is_windows():
        target_path.write_text(content, encoding="utf-8")
        return

    tee_cmd = maybe_sudo(["tee", str(target_path)])
    subprocess.run(tee_cmd, input=content, text=True, check=True, stdout=subprocess.DEVNULL)


def run_systemctl(args_list: list[str], check: bool = True) -> None:
    systemctl = maybe_sudo(["systemctl", *args_list])
    run(systemctl, check=check)


def install_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu. Usa start-native o Docker en Windows.")
        return

    maybe_regenerate_jwt_secret(ENV_LOCAL, "el servicio systemd de Ubuntu")

    port = get_native_port(args.port)
    if not (ROOT / ".venv").exists():
        print("[!] No existe .venv. Crea el entorno virtual antes de instalar el servicio.")
        return

    service_content = build_systemd_service_content(port)
    write_file_as_root(SYSTEMD_SERVICE_PATH, service_content)
    print(f"[OK] Servicio escrito en {SYSTEMD_SERVICE_PATH}")
    run_systemctl(["daemon-reload"])
    run_systemctl(["enable", "--now", SYSTEMD_SERVICE_NAME])
    print("[OK] Servicio instalado, habilitado y arrancado.")


def start_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu.")
        return
    run_systemctl(["start", SYSTEMD_SERVICE_NAME])


def stop_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu.")
        return
    run_systemctl(["stop", SYSTEMD_SERVICE_NAME])


def restart_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu.")
        return
    run_systemctl(["restart", SYSTEMD_SERVICE_NAME])


def status_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu.")
        return
    run_systemctl(["status", "--no-pager", SYSTEMD_SERVICE_NAME], check=False)


def uninstall_service(args: argparse.Namespace) -> None:
    if is_windows():
        print("[!] systemd solo está disponible en Linux/Ubuntu.")
        return
    run_systemctl(["disable", "--now", SYSTEMD_SERVICE_NAME], check=False)
    if SYSTEMD_SERVICE_PATH.exists():
        if is_posix_root():
            SYSTEMD_SERVICE_PATH.unlink()
        else:
            subprocess.run(maybe_sudo(["rm", "-f", str(SYSTEMD_SERVICE_PATH)]), check=False)
    run_systemctl(["daemon-reload"], check=False)
    print("[OK] Servicio systemd eliminado.")


def stop_native(args: argparse.Namespace) -> None:
    port = get_native_port(args.port)
    pid = read_pid_file()

    if pid is not None:
        kill_process_tree(pid)
        remove_pid_file()
        print(f"[OK] Proceso nativo detenido (PID {pid}).")
    else:
        print("[!] No hay PID registrado para la app nativa.")

    release_port(port)


def free_port_command(args: argparse.Namespace) -> None:
    port = get_native_port(args.port)
    release_port(port)


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

    maybe_regenerate_jwt_secret(ENV_DOCKER, "Docker (init)")

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
    maybe_regenerate_jwt_secret(ENV_DOCKER, "Docker (update)")
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

    sub.add_parser("migrate-ubuntu", help="Ejecutar migraciones en Ubuntu usando la .venv")

    p_install_service = sub.add_parser("install-service", help="Instalar la app como servicio systemd en Ubuntu")
    p_install_service.add_argument("--port", type=int, default=None, help="Puerto a exponer por el servicio (default: APP_PORT o 8000)")

    sub.add_parser("start-service", help="Iniciar el servicio systemd")
    sub.add_parser("stop-service", help="Detener el servicio systemd")
    sub.add_parser("restart-service", help="Reiniciar el servicio systemd")
    sub.add_parser("status-service", help="Ver el estado del servicio systemd")
    sub.add_parser("uninstall-service", help="Quitar el servicio systemd")

    args = parser.parse_args()

    def show_menu() -> None:
        while True:
            print("\n=== Deploy Manager ===")
            print("\n--- Opciones Docker ---")
            print("1) Init (despliegue inicial)")
            print("2) Update (rebuild y migraciones)")
            print("\n--- Servicio systemd (Ubuntu) ---")
            print("3) Install service")
            print("4) Migrate Ubuntu")
            print("5) Start service")
            print("6) Stop service")
            print("7) Restart service")
            print("8) Status service")
            print("9) Uninstall service")
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
            if opcion == "3":
                port_text = input("Puerto del servicio (default APP_PORT/8000): ").strip()
                class Args:
                    pass
                ns = Args()
                ns.port = int(port_text) if port_text else None
                install_service(ns)
                continue
            if opcion == "4":
                class Args:
                    pass
                ns = Args()
                migrate_ubuntu(ns)
                continue
            if opcion == "5":
                class Args:
                    pass
                ns = Args()
                start_service(ns)
                continue
            if opcion == "6":
                class Args:
                    pass
                ns = Args()
                stop_service(ns)
                continue
            if opcion == "7":
                class Args:
                    pass
                ns = Args()
                restart_service(ns)
                continue
            if opcion == "8":
                class Args:
                    pass
                ns = Args()
                status_service(ns)
                continue
            if opcion == "9":
                class Args:
                    pass
                ns = Args()
                uninstall_service(ns)
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
    elif args.cmd == "migrate-ubuntu":
        migrate_ubuntu(args)
    elif args.cmd == "install-service":
        install_service(args)
    elif args.cmd == "start-service":
        start_service(args)
    elif args.cmd == "stop-service":
        stop_service(args)
    elif args.cmd == "restart-service":
        restart_service(args)
    elif args.cmd == "status-service":
        status_service(args)
    elif args.cmd == "uninstall-service":
        uninstall_service(args)


if __name__ == "__main__":
    main()

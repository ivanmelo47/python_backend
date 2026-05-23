#!/usr/bin/env python3
"""Herramienta de despliegue nativo para Ubuntu VPS (systemd).
Despliega la aplicación de forma persistente (incluso tras reiniciar el servidor o cerrar terminal).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_LOCAL = ROOT / ".env"
SYSTEMD_SERVICE_NAME = "python_backend.service"
SYSTEMD_SERVICE_PATH = Path("/etc/systemd/system") / SYSTEMD_SERVICE_NAME


def is_posix_root() -> bool:
    geteuid = getattr(os, "geteuid", None)
    return bool(geteuid and geteuid() == 0)


def maybe_sudo(cmd: list[str]) -> list[str]:
    if is_posix_root():
        return cmd
    sudo = shutil.which("sudo")
    if sudo:
        return [sudo, *cmd]
    return cmd


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, check=check)


def read_env_file(path: Path) -> dict[str, str]:
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


def get_systemd_python_executable() -> str:
    candidates = [
        ROOT / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    print("[!] No se encontró un entorno virtual en .venv. Crea/activa .venv e instala dependencias antes de desplegar.")
    sys.exit(1)


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
    if is_posix_root():
        target_path.write_text(content, encoding="utf-8")
        return
    tee_cmd = maybe_sudo(["tee", str(target_path)])
    subprocess.run(tee_cmd, input=content, text=True, check=True, stdout=subprocess.DEVNULL)


def run_systemctl(args_list: list[str], check: bool = True) -> None:
    systemctl = maybe_sudo(["systemctl", *args_list])
    run(systemctl, check=check)


def release_port(port: int) -> None:
    """Libera el puerto usando fuser (típico en Ubuntu/Linux)."""
    fuser = shutil.which("fuser")
    if not fuser:
        print(f"[!] Comando 'fuser' no encontrado. Asegúrate de que el puerto {port} esté libre.")
        return
    
    print(f"Buscando y deteniendo procesos residuales en el puerto {port}...")
    # fuser -k {port}/tcp mata el proceso que esté usando el puerto
    cmd = maybe_sudo([fuser, "-k", f"{port}/tcp"])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[OK] Se ha liberado el puerto {port}.")


def deploy_service() -> None:
    print("\n--- Desplegar Aplicación ---")
    if not (ROOT / ".venv").exists():
        print("[!] Advertencia: No se encontró el directorio .venv.")
        print("Debes crear tu entorno virtual (python3 -m venv .venv) y")
        print("ejecutar: .venv/bin/pip install -r requirements.txt")
        if input("¿Continuar de todos modos? (s/N): ").strip().lower() != "s":
            return

    env_values = read_env_file(ENV_LOCAL)
    default_port = env_values.get("APP_PORT", "8000")
    
    port_input = input(f"Puerto para la aplicación (default: {default_port}): ").strip()
    port = int(port_input) if port_input else int(default_port)

    # 1. Asegurarse de que el puerto esté libre antes de iniciar
    release_port(port)

    # 2. Crear archivo de servicio
    service_content = build_systemd_service_content(port)
    write_file_as_root(SYSTEMD_SERVICE_PATH, service_content)
    print(f"[OK] Archivo de servicio escrito en {SYSTEMD_SERVICE_PATH}")

    # 3. Recargar systemd y arrancar
    run_systemctl(["daemon-reload"])
    run_systemctl(["enable", "--now", SYSTEMD_SERVICE_NAME])
    print("[OK] ¡Servicio instalado y arrancado correctamente!")
    print(f"[OK] La aplicación está configurada para ejecutarse de forma persistente en el puerto {port}.")


def view_status() -> None:
    print("\n--- Estado del Servicio ---")
    if not SYSTEMD_SERVICE_PATH.exists():
        print("[!] El servicio no está instalado.")
        return
    run_systemctl(["status", "--no-pager", SYSTEMD_SERVICE_NAME], check=False)


def view_logs() -> None:
    print("\n--- Logs del Servicio (últimas 50 líneas) ---")
    if not SYSTEMD_SERVICE_PATH.exists():
        print("[!] El servicio no está instalado.")
        return
    journalctl = maybe_sudo(["journalctl", "-u", SYSTEMD_SERVICE_NAME, "-n", "50", "--no-pager"])
    run(journalctl, check=False)


def uninstall_service() -> None:
    print("\n--- Dar de Baja (Desinstalar y liberar) ---")
    if not SYSTEMD_SERVICE_PATH.exists():
        print("[!] El servicio no está instalado actualmente.")
        return

    # Extraer el puerto actual del archivo service si es posible, para limpiarlo garantizadamente.
    port = 8000
    try:
        content = SYSTEMD_SERVICE_PATH.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.strip().startswith("ExecStart="):
                parts = line.split("--port")
                if len(parts) > 1:
                    port = int(parts[1].strip().split()[0])
    except Exception:
        pass

    # 1. Detener y deshabilitar
    run_systemctl(["disable", "--now", SYSTEMD_SERVICE_NAME], check=False)
    
    # 2. Borrar archivo service
    if is_posix_root():
        SYSTEMD_SERVICE_PATH.unlink(missing_ok=True)
    else:
        subprocess.run(maybe_sudo(["rm", "-f", str(SYSTEMD_SERVICE_PATH)]), check=False)
    
    # 3. Recargar systemd
    run_systemctl(["daemon-reload"], check=False)
    print("[OK] Servicio systemd detenido y desinstalado completamente.")

    # 4. Liberar puerto forzosamente (matando cualquier proceso residual)
    release_port(port)


def main() -> None:
    if os.name == "nt":
        print("[!] ADVERTENCIA: Este script está diseñado exclusivamente para Ubuntu/Linux.")
        print("Se detectó que estás en Windows, por lo que los comandos de systemd no funcionarán.")
        print("Por favor, transfiere y ejecuta este script directamente en tu VPS Ubuntu.\n")

    while True:
        print("\n" + "="*35)
        print("=== Deploy Nativo Ubuntu (systemd) ===")
        print("="*35)
        print("1) Desplegar aplicación (Instalar/Actualizar)")
        print("2) Ver estado del servicio")
        print("3) Ver logs del servicio")
        print("4) Dar de baja (Detener, desinstalar y liberar puerto)")
        print("0) Salir")
        
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            deploy_service()
            input("\nPresiona Enter para continuar...")
        elif opcion == "2":
            view_status()
            input("\nPresiona Enter para continuar...")
        elif opcion == "3":
            view_logs()
            input("\nPresiona Enter para continuar...")
        elif opcion == "4":
            uninstall_service()
            input("\nPresiona Enter para continuar...")
        elif opcion == "0":
            print("Saliendo del gestor de despliegue.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()

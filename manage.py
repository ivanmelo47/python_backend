import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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

ensure_venv_and_restart()

from sqlalchemy import create_engine, text

from app.core.settings import settings


def run_alembic(args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        check=True,
        capture_output=capture_output,
        text=True
    )


def clear_screen() -> None:
    command = "cls" if sys.platform.startswith("win") else "clear"
    subprocess.run(command, shell=True, check=False)


def wait_for_continue() -> None:
    input("\nPresiona Enter para continuar...")


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


def show_migration_menu() -> None:
    while True:
        clear_screen()
        print("\n=== Seccion: Migraciones DB ===")
        print("1) Crear migracion")
        print("2) Aplicar migraciones")
        print("3) Retroceder migracion")
        print("4) Ver revision actual")
        print("5) Ver historial")
        print("6) Ver cabezas")
        print("7) Marcar revision actual")
        print("8) Reiniciar base de datos y migrar")
        print("0) Volver al menu principal")

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            mensaje = input("Nombre de la migracion: ").strip()
            if not mensaje:
                print("La migracion no puede quedar vacia.")
                wait_for_continue()
                continue
            try:
                run_alembic(["revision", "--autogenerate", "-m", mensaje])
            except subprocess.CalledProcessError as exc:
                print(f"Error al crear migracion (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "2":
            try:
                run_alembic(["upgrade", "head"])
                print("\n[OK] Migraciones aplicadas y version actualizada.")
            except subprocess.CalledProcessError as exc:
                print(f"\n[!] Error al aplicar migraciones (codigo {exc.returncode}).")
                print("Si el error indica que una tabla o columna ya existe, es probable que")
                print("la base de datos este fuera de sincronia con Alembic.")
                
                confirm = input("¿Deseas forzar la sincronizacion al estado actual (stamp head)? (s/N): ").strip().lower()
                if confirm == "s":
                    try:
                        run_alembic(["stamp", "head"])
                        print("[OK] Version de Alembic sincronizada con el head.")
                    except subprocess.CalledProcessError:
                        print("[!] No se pudo sincronizar la version.")
            wait_for_continue()
            continue

        if opcion == "3":
            paso = input("Paso a retroceder (default -1): ").strip() or "-1"
            try:
                run_alembic(["downgrade", paso])
            except subprocess.CalledProcessError as exc:
                print(f"Error al retroceder migracion (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "4":
            try:
                run_alembic(["current"])
            except subprocess.CalledProcessError as exc:
                print(f"Error al consultar revision actual (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "5":
            try:
                run_alembic(["history"])
            except subprocess.CalledProcessError as exc:
                print(f"Error al consultar historial (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "6":
            try:
                run_alembic(["heads"])
            except subprocess.CalledProcessError as exc:
                print(f"Error al consultar cabezas (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "7":
            revision = input("Revision a marcar (default head): ").strip() or "head"
            try:
                run_alembic(["stamp", revision])
            except subprocess.CalledProcessError as exc:
                print(f"Error al marcar revision (codigo {exc.returncode}).")
            wait_for_continue()
            continue

        if opcion == "8":
            confirmacion = input("Esto eliminara la base actual y la recreara. Escribe SI para continuar: ").strip()
            if confirmacion != "SI":
                print("Operacion cancelada.")
                wait_for_continue()
                continue

            try:
                reset_database_and_migrate()
            except Exception as exc:  # noqa: BLE001
                print(f"Error al reiniciar y migrar la base: {exc}")
            wait_for_continue()
            continue

        if opcion == "0":
            print("Volviendo al menu principal.")
            wait_for_continue()
            return

        print("Opcion no valida. Intenta de nuevo.")
        wait_for_continue()


def show_app_menu() -> None:
    clear_screen()
    print("\n=== Seccion: Ejecutar App ===")
    host = input("Host (default 127.0.0.1): ").strip() or "127.0.0.1"
    raw_port = input("Puerto (default 8000): ").strip() or "8000"

    try:
        port = int(raw_port)
    except ValueError:
        print("Puerto invalido. Debe ser numero entero.")
        wait_for_continue()
        return

    if port < 1 or port > 65535:
        print("Puerto invalido. Debe estar entre 1 y 65535.")
        wait_for_continue()
        return

    reload_answer = input("Habilitar reload automatico? (S/n): ").strip().lower()
    reload_enabled = reload_answer in {"", "s", "si", "y", "yes"}
    run_app(host=host, port=port, reload_enabled=reload_enabled)


def show_main_menu() -> None:
    while True:
        clear_screen()
        print("\n=== Manager Principal ===")
        print("1) Gestion de migraciones DB")
        print("2) Ejecutar app (backend manual)")
        print("3) Generar nuevo JWT Secret Key")
        print("4) Arrancar frontend (Vue)")
        print("5) Arrancar Fullstack (FastAPI + Vue)")
        print("0) Salir")

        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            show_migration_menu()
            continue

        if opcion == "2":
            show_app_menu()
            continue

        if opcion == "3":
            generate_jwt_secret()
            wait_for_continue()
            continue

        if opcion == "4":
            run_frontend()
            continue

        if opcion == "5":
            clear_screen()
            print("\n=== Arrancar Fullstack ===")
            host = input("Host (default 127.0.0.1): ").strip() or "127.0.0.1"
            raw_port = input("Puerto API (default 8000): ").strip() or "8000"
            try:
                port = int(raw_port)
            except ValueError:
                print("Puerto invalido.")
                wait_for_continue()
                continue
            run_fullstack(host=host, port=port, reload_enabled=True)
            continue

        if opcion == "0":
            print("Saliendo del manager.")
            return

        print("Opcion no valida. Intenta de nuevo.")
        wait_for_continue()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manager del proyecto (Migraciones DB y ejecucion de app)")
    subparsers = parser.add_subparsers(dest="command")

    crear_cmd = subparsers.add_parser("crear", aliases=["make"], help="Crear una migracion nueva desde cambios en modelos")
    crear_cmd.add_argument("-m", "--mensaje", required=True, help="Nombre de la migracion")

    subparsers.add_parser("migrar", aliases=["migrate"], help="Aplicar migraciones pendientes")

    retroceder_cmd = subparsers.add_parser("retroceder", aliases=["rollback"], help="Revertir migraciones")
    retroceder_cmd.add_argument("--paso", default="-1", help="Destino del downgrade (por defecto: -1)")

    subparsers.add_parser("actual", aliases=["current"], help="Mostrar la revision actual")
    subparsers.add_parser("historial", aliases=["history"], help="Mostrar el historial de migraciones")
    subparsers.add_parser("cabezas", aliases=["heads"], help="Mostrar las cabezas actuales")
    marcar_cmd = subparsers.add_parser("marcar", aliases=["stamp"], help="Marcar una revision sin ejecutar migraciones")
    marcar_cmd.add_argument("--revision", default="head", help="Revision a marcar (default: head)")
    subparsers.add_parser("reiniciar", aliases=["reset", "reset-db"], help="Reiniciar la base de datos y aplicar migraciones")

    ejecutar_cmd = subparsers.add_parser("ejecutar", aliases=["run", "start"], help="Ejecutar app con host/puerto manual")
    ejecutar_cmd.add_argument("--host", default="127.0.0.1", help="Host de escucha (default: 127.0.0.1)")
    ejecutar_cmd.add_argument("--puerto", type=int, default=8000, help="Puerto de escucha (default: 8000)")
    ejecutar_cmd.add_argument("--sin-reload", action="store_true", help="Deshabilitar reload automatico")

    subparsers.add_parser("generar-jwt", aliases=["jwt", "secret-key"], help="Generar un nuevo JWT secret key y actualizar .env")
    
    subparsers.add_parser("front", aliases=["frontend", "vue"], help="Arrancar solo el frontend de Vue")

    fullstack_cmd = subparsers.add_parser("fullstack", aliases=["full"], help="Arrancar FastAPI y Vue simultaneamente")
    fullstack_cmd.add_argument("--host", default="127.0.0.1", help="Host de escucha (default: 127.0.0.1)")
    fullstack_cmd.add_argument("--puerto", type=int, default=8000, help="Puerto de escucha (default: 8000)")
    fullstack_cmd.add_argument("--sin-reload", action="store_true", help="Deshabilitar reload automatico")
    args = parser.parse_args()

    if args.command is None:
        if sys.stdin.isatty():
            show_main_menu()
        else:
            parser.print_help()
        return

    if args.command in {"crear", "make"}:
        run_alembic(["revision", "--autogenerate", "-m", args.mensaje])
        return

    if args.command in {"migrar", "migrate"}:
        run_alembic(["upgrade", "head"])
        return

    if args.command in {"retroceder", "rollback"}:
        run_alembic(["downgrade", args.paso])
        return

    if args.command in {"actual", "current"}:
        run_alembic(["current"])
        return

    if args.command in {"historial", "history"}:
        run_alembic(["history"])
        return

    if args.command in {"cabezas", "heads"}:
        run_alembic(["heads"])
        return

    if args.command in {"marcar", "stamp"}:
        run_alembic(["stamp", args.revision])
        return

    if args.command in {"reiniciar", "reset", "reset-db"}:
        reset_database_and_migrate()
        return

    if args.command in {"ejecutar", "run", "start"}:
        if args.puerto < 1 or args.puerto > 65535:
            parser.error("El puerto debe estar entre 1 y 65535")
        run_app(host=args.host, port=args.puerto, reload_enabled=not args.sin_reload)
        return

    if args.command in {"generar-jwt", "jwt", "secret-key"}:
        generate_jwt_secret()
        return

    if args.command in {"front", "frontend", "vue"}:
        run_frontend()
        return

    if args.command in {"fullstack", "full"}:
        if args.puerto < 1 or args.puerto > 65535:
            parser.error("El puerto debe estar entre 1 y 65535")
        run_fullstack(host=args.host, port=args.puerto, reload_enabled=not args.sin_reload)
        return


if __name__ == "__main__":
    main()

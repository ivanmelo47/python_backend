from __future__ import annotations

import subprocess
import sys

from seeders.registry import (
    SEEDER_LOG_FILE,
    discover_seeders,
    get_seeder_conflicts,
    read_executed_seeders,
    run_seeder,
)

from manage.actions import generate_jwt_secret, reset_database_and_migrate, run_app, run_frontend, run_fullstack, run_alembic


def clear_screen() -> None:
    command = "cls" if sys.platform.startswith("win") else "clear"
    subprocess.run(command, shell=True, check=False)


def wait_for_continue() -> None:
    input("\nPresiona Enter para continuar...")


def _print_section(title: str, subtitle: str | None = None) -> None:
    width = 72
    print()
    print("=" * width)
    print(title.center(width))
    if subtitle:
        print(subtitle.center(width))
    print("=" * width)


def _print_key_value(label: str, value: str) -> None:
    print(f"{label:<16} {value}")


def _run_seeder_with_prompt(seeder_key: str, *, force: bool = False) -> tuple[bool, str]:
    conflicts = get_seeder_conflicts(seeder_key)
    if conflicts and not force:
        _print_section("ADVERTENCIA DE CONFLICTOS")
        print("Se detectaron registros existentes que coinciden con campos del seeder:")
        for conflict in conflicts:
            print(f"- {conflict}")
        confirmacion = input("¿Deseas continuar y reemplazarlos? (s/N): ").strip().lower()
        if confirmacion not in {"s", "si", "y", "yes"}:
            return False, "Operacion cancelada por el usuario."

    return run_seeder(seeder_key, force=force)


def _select_seeder_from_list(seeders) -> int | None:
    raw_value = input("\nElige el numero del seeder a ejecutar (0 para volver): ").strip()
    if not raw_value.isdigit():
        return None

    index = int(raw_value)
    if index == 0:
        return 0

    if 1 <= index <= len(seeders):
        return index

    return None


def show_seeders_menu() -> None:
    while True:
        clear_screen()
        executed_seeders = read_executed_seeders()
        seeders = discover_seeders()

        _print_section("SECCION: SEEDERS", "Ver listado y elegir cual ejecutar")
        _print_key_value("Log:", str(SEEDER_LOG_FILE))
        _print_key_value("Detectados:", str(len(seeders)))
        _print_key_value("Ejecutados:", str(len(executed_seeders)))
        print()

        if not seeders:
            print("No se encontraron seeders que cumplan la convencion seed_*.py con una funcion run().")
        else:
            for index, seeder in enumerate(seeders, start=1):
                status = "OK" if seeder.key in executed_seeders else "PENDIENTE"
                description = f" - {seeder.description}" if seeder.description else ""
                print(f"{index:>2}. [{status:<9}] {seeder.title} ({seeder.key}){description}")

        print()
        print("[p] Ejecutar pendientes")
        print("[l] Ver registro ejecutado")
        print("[0] Volver")

        opcion = input("Elige una opcion o un numero: ").strip().lower()

        if opcion == "0":
            return

        if opcion == "l":
            _print_section("SEEDERS EJECUTADOS")
            if not executed_seeders:
                print("Ninguno aun.")
            else:
                for seeder_key in sorted(executed_seeders):
                    print(f"- {seeder_key}")
            wait_for_continue()
            continue

        if opcion == "p":
            _print_section("RESULTADO DE SEEDERS PENDIENTES")
            for seeder in seeders:
                if seeder.key in executed_seeders:
                    print(f"SKIP {seeder.key}: Ya ejecutado")
                    continue

                success, message = _run_seeder_with_prompt(seeder.key)
                prefix = "OK" if success else "SKIP"
                print(f"{prefix} {seeder.key}: {message}")
            wait_for_continue()
            continue

        selected_index = _select_seeder_from_list(seeders)
        if selected_index == 0:
            return

        if selected_index is not None:
            seeder = seeders[selected_index - 1]
            if seeder.key in executed_seeders:
                confirmacion = input(
                    "Ese seeder ya fue ejecutado. ¿Deseas forzarlo de nuevo? (s/N): "
                ).strip().lower()
                if confirmacion not in {"s", "si", "y", "yes"}:
                    print("Operacion cancelada.")
                    wait_for_continue()
                    continue

                success, message = _run_seeder_with_prompt(seeder.key, force=True)
            else:
                success, message = _run_seeder_with_prompt(seeder.key)

            print(message)
            if success:
                print("OK Ejecutado y registrado en el log.")
            wait_for_continue()
            continue

        print("Opcion no valida. Intenta de nuevo.")
        wait_for_continue()


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
        print("6) Ver listado de seeders")
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

        if opcion == "6":
            show_seeders_menu()
            continue

        if opcion == "0":
            print("Saliendo del manager.")
            return

        print("Opcion no valida. Intenta de nuevo.")
        wait_for_continue()

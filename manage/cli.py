from __future__ import annotations

import argparse
import sys

from manage.actions import generate_jwt_secret, run_app, run_frontend, run_fullstack, run_alembic
from manage.bootstrap import ensure_venv_and_restart
from manage.ui import show_main_menu, show_seeders_menu
from seeders.registry import discover_seeders, get_seeder_conflicts, run_seeder


def main() -> None:
    ensure_venv_and_restart()

    parser = argparse.ArgumentParser(description="Manager del proyecto (Migraciones DB, seeders y ejecucion de app)")
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
    seeders_cmd = subparsers.add_parser("seeders", aliases=["seeds", "seed"], help="Gestionar seeders del sistema")
    seeders_cmd.add_argument("--run", help="Ejecutar un seeder especifico por nombre de archivo")
    seeders_cmd.add_argument("--force", action="store_true", help="Forzar la ejecucion aunque ya figure en el log")
    seeders_cmd.add_argument("--pending", action="store_true", help="Ejecutar solo los seeders pendientes")

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
        from manage.actions import reset_database_and_migrate
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

    if args.command in {"seeders", "seeds", "seed"}:
        seeders = discover_seeders()
        seeder_keys = {seeder.key for seeder in seeders}

        if args.pending:
            from manage.ui import _run_seeder_with_prompt  # local import to keep ui helpers contained
            for seeder in seeders:
                if sys.stdin.isatty():
                    success, message = _run_seeder_with_prompt(seeder.key)
                else:
                    conflicts = get_seeder_conflicts(seeder.key)
                    if conflicts and not args.force:
                        print(f"SKIP {seeder.key}: se detectaron conflictos. Usa --force para continuar.")
                        for conflict in conflicts:
                            print(f"- {conflict}")
                        continue
                    success, message = run_seeder(seeder.key, force=args.force)
                prefix = "OK" if success else "SKIP"
                print(f"{prefix} {seeder.key}: {message}")
            return

        if args.run:
            if args.run not in seeder_keys:
                print(f"Seeder no encontrado: {args.run}")
                sys.exit(1)

            if sys.stdin.isatty() and not args.force:
                from manage.ui import _run_seeder_with_prompt
                success, message = _run_seeder_with_prompt(args.run)
            else:
                conflicts = get_seeder_conflicts(args.run)
                if conflicts and not args.force:
                    print("Se detectaron conflictos y no se encontro una terminal interactiva.")
                    for conflict in conflicts:
                        print(f"- {conflict}")
                    print("Usa --force si deseas continuar sin confirmar.")
                    sys.exit(1)
                success, message = run_seeder(args.run, force=args.force)

            print(message)
            if not success:
                sys.exit(1)
            return

        if sys.stdin.isatty():
            show_seeders_menu()
        else:
            print("Usa --run <seed_archivo>, --pending o ejecuta desde una terminal interactiva.")
            parser.print_help()
        return


if __name__ == "__main__":
    main()

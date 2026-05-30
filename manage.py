from manage.bootstrap import ensure_venv_and_restart

ensure_venv_and_restart()

from manage.cli import main


if __name__ == "__main__":
    main()

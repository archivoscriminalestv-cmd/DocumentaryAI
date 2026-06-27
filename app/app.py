from config.settings import PROJECT_NAME
from app.project_manager import load_project
from app.ui import (
    show_header,
    show_project_loaded,
    show_main_menu,
    get_menu_option,
)


def run() -> None:
    show_header()

    project = load_project(PROJECT_NAME)
    show_project_loaded(project)

    print()
    print(f"Proyecto activo: {project}")
    print()

    while True:
        show_main_menu()

        option = get_menu_option()

        print()

        if option == "1":
            print("Abriendo proyecto...")

        elif option == "2":
            print("Hasta pronto.")
            break

        else:
            print("Opción no válida.")

        print()
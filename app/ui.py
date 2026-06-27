def show_header() -> None:
    print("=" * 50)
    print("DOCUMENTARY AI")
    print("=" * 50)
    print()


def show_project_loaded(name: str) -> None:
    print(f"Proyecto cargado: {name}")


def show_main_menu() -> None:
    print("1. Abrir proyecto")
    print("2. Salir")
    print()


def get_menu_option() -> str:
    option = input("Selecciona una opción: ")
    return option

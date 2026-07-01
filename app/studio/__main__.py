"""Punto de entrada de DocumentaryAI Studio.

    python -m app.studio

Si PySide6 no está instalado, muestra instrucciones claras en vez de fallar con un traceback.
En el futuro se empaqueta como «DocumentaryAI Studio.exe» (ver app/studio/packaging/).
"""

import sys


def main() -> int:
    try:
        from app.studio.ui.app import run
        return run(sys.argv)
    except ImportError as exc:
        if "PySide6" in str(exc):
            print("DocumentaryAI Studio necesita PySide6 (Qt para escritorio).")
            print("Instálalo con:")
            print("    pip install PySide6")
            print(f"\n(detalle: {exc})")
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())

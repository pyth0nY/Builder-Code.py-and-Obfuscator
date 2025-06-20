# Contenido COMPLETO y FINAL para: BuilderPexe.py

import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from ui.main_window import PyBuilderStudio

def main():
    """Punto de entrada principal para la aplicación."""
    app = QApplication(sys.argv)
    
    try:
        apply_stylesheet(app, theme='dark_cyan.xml')
    except Exception as e:
        print(f"Advertencia: No se pudo aplicar el tema qt-material: {e}")

    window = PyBuilderStudio()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
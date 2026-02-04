import sys
from PySide6.QtWidgets import QApplication
from ui.splash_screen import ModernSplashScreen, LoadingThread
from ui.main_window import PyBuilderStudio 

main_window = None

def show_main_window(splash):
    """Cierra el splash y muestra la ventana principal"""
    global main_window
    splash.close()
    main_window = PyBuilderStudio()
    main_window.show()

def main():
    app = QApplication(sys.argv)
    
    
    splash = ModernSplashScreen()
    splash.show()
    
    
    loader = LoadingThread()
    
     
    
    loader.progress.connect(splash.update_progress)
    loader.status.connect(splash.update_status)
    
    
    loader.finished.connect(lambda: show_main_window(splash))
    
    loader.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
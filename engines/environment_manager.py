# engines/environment_manager.py

import shutil
import subprocess
import sys

def check_tool(name: str) -> dict:
    """Verifica si una herramienta de línea de comandos está disponible en el PATH."""
    path = shutil.which(name)
    if path:
        return {"status": "ok", "path": path, "message": f"{name} encontrado en: {path}"}
    else:
        return {"status": "error", "path": None, "message": f"ERROR: '{name}' no se encuentra en el PATH del sistema. Por favor, instálalo."}

def check_python_package(name: str) -> dict:
    """Verifica si un paquete de Python está instalado en el entorno actual."""
    try:
        # Usamos el ejecutable de Python actual para verificar en el entorno correcto
        subprocess.check_call([sys.executable, "-m", "pip", "show", name], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "ok", "message": f"Paquete '{name}' está instalado."}
    except subprocess.CalledProcessError:
        return {"status": "error", "message": f"ERROR: Paquete '{name}' no instalado. Ejecuta: pip install {name}"}

def check_all() -> list:
    """Ejecuta todas las verificaciones críticas y devuelve una lista de problemas."""
    errors = []
    
    # 1. PyInstaller (esencial)
    pyinstaller_check = check_python_package("pyinstaller")
    if pyinstaller_check["status"] == "error":
        errors.append(pyinstaller_check["message"])

    # 2. PyArmor (opcional pero común)
    pyarmor_check = check_tool("pyarmor")
    if pyarmor_check["status"] == "error":
        # No lo añadimos como error crítico, sino como advertencia, 
        # ya que puede que no se use. Podríamos mejorarlo para que solo avise si se activa.
        pass # Podrías añadir un sistema de warnings si quieres

    # 3. UPX (opcional para compresión)
    upx_check = check_tool("upx")
    # Lo mismo, es opcional.

    return errors
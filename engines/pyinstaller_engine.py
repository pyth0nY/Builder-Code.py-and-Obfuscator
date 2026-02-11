import os
import os
import sys
import shutil
import ast
import uuid
from pathlib import Path

# =============================================================================
# 🔧 SECCIÓN DE IMPORTACIÓN SEGURA (Solución al error amarillo)
# =============================================================================
# Intentamos importar las herramientas de PyInstaller.
# Si VS Code se queja, ignóralo, este bloque try/except hace que el código
# funcione igual al ejecutarse aunque el editor marque error.
try:
    from PyInstaller.utils.hooks import collect_all, collect_submodules
except ImportError:
    # Si realmente no está instalado, usamos funciones falsas para no crashear
    def collect_all(name): return [], [], []     # Retorna vacíos: (binarios, datos, imports)
    def collect_submodules(name): return []      # Retorna lista vacía

# =============================================================================
# 🧠 CEREBRO ANALIZADOR (Lee el script del cliente)
# =============================================================================

class ProjectAnalyzer:
    """
    Analiza el script que el usuario seleccionó en la interfaz
    para saber qué librerías está usando realmente.
    """
    def __init__(self, target_script):
        self.script = target_script
        self.root_dir = os.path.dirname(os.path.abspath(target_script))
        self.imports = set()
        
    def scan_imports(self):
        """Lee el código fuente y busca 'import ...'"""
        if not os.path.exists(self.script):
            return set()
            
        try:
            with open(self.script, "r", encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"⚠️ [MOTOR] No pude leer el script del usuario: {e}")
            
        return self.imports

    def detect_local_modules(self):
        """Detecta carpetas junto al script (assets, utils, img, etc)"""
        local_folders = []
        try:
            for item in os.listdir(self.root_dir):
                full_path = os.path.join(self.root_dir, item)
                if os.path.isdir(full_path):
                    # Filtramos carpetas del sistema que no nos interesan
                    if item not in ['__pycache__', 'build', 'dist', 'venv', '.git', '.idea', '.vscode']:
                        local_folders.append(item)
        except:
            pass
        return local_folders

# =============================================================================
# 🛠️ UTILIDADES DEL MOTOR
# =============================================================================

def create_recursion_hook(output_dir):
    """
    Crea un archivo Python temporal que se inyecta en el EXE.
    Sirve para evitar errores de memoria (RecursionError) en código ofuscado.
    """
    hook_content = """
import sys
import os

# 1. AUMENTAR RECURSIÓN (Vital para scripts ofuscados con AST)
sys.setrecursionlimit(50000)

# 2. ARREGLAR RUTAS RELATIVAS (Para que funcionen las imagenes dentro del exe)
if getattr(sys, 'frozen', False):
    os.environ['BUNDLE_ROOT'] = sys._MEIPASS
"""
    # Usamos un nombre aleatorio para no conflictos
    filename = f"hook_recursion_{uuid.uuid4().hex[:8]}.py"
    path = os.path.join(output_dir, filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(hook_content)
    
    return path

# =============================================================================
# 🚀 FUNCIÓN PRINCIPAL (Llamada por tu GUI)
# =============================================================================

def build_command(options: dict) -> list:
    """
    Genera la lista de comandos para PyInstaller basada en la configuración de la GUI.
    """
    
    # 1. Obtener datos de la GUI
    script_path = options.get("script_path")
    output_dir = options.get("output_dir", os.getcwd())
    exe_name = options.get("exe_name", "MyApp")
    
    if not script_path or not os.path.exists(script_path):
        return None

    # Directorios de trabajo
    dist_path = os.path.join(output_dir, 'dist')
    build_path = os.path.join(output_dir, 'build_temp')

    # 2. INICIAR INTELIGENCIA: Escanear el proyecto del usuario
    analyzer = ProjectAnalyzer(script_path)
    user_imports = analyzer.scan_imports()
    user_folders = analyzer.detect_local_modules()
    
    print(f"🔎 [MOTOR] Librerías detectadas: {user_imports}")
    print(f"📂 [MOTOR] Carpetas locales detectadas: {user_folders}")

    # 3. Construir comando base
    command = [
        'pyinstaller',
        '--noconfirm',
        '--clean',
        '--name', exe_name,
        '--distpath', dist_path,
        '--workpath', build_path,
    ]

    # Flags configurados en la GUI
    if options.get("one_file"): command.append('--onefile')
    else: command.append('--onedir')

    if options.get("no_console"): 
        command.extend(['--noconsole', '--windowed'])
    
    if options.get("clean"):
        # Limpieza manual extra si se pide
        if os.path.exists(build_path): shutil.rmtree(build_path, ignore_errors=True)

    if options.get("icon_path") and os.path.exists(options.get("icon_path")):
        command.extend(['--icon', options.get("icon_path")])

    # 4. APLICAR INTELIGENCIA (Fixes automáticos)
    
    # -> Soporte Full Qt (PySide/PyQt)
    qt_libs = ["PySide6", "PyQt6", "PyQt5", "PySide2"]
    for lib in qt_libs:
        if lib in user_imports:
            print(f"   -> Optimizando para {lib}...")
            command.extend(['--collect-all', lib])
            break # Solo procesamos un framework Qt a la vez
            
    # -> Soporte Tkinter (a veces falla en onefile)
    if "tkinter" in user_imports or "Tkinter" in user_imports:
        command.extend(['--hidden-import', 'tkinter'])
        
    # -> Soporte Librerías Científicas/Datos
    if "pandas" in user_imports: command.extend(['--collect-all', 'pandas'])
    if "numpy" in user_imports: command.extend(['--hidden-import', 'numpy'])
    if "cv2" in user_imports: command.extend(['--collect-all', 'cv2'])
    if "PIL" in user_imports or "Pillow" in user_imports: 
        command.extend(['--hidden-import', 'PIL'])
        command.extend(['--collect-all', 'PIL'])

    # 5. AÑADIR CARPETAS LOCALES AUTOMÁTICAMENTE
    # Si el usuario tiene carpeta 'img' al lado de su script, la metemos.
    sep = os.pathsep # ';' en Windows
    user_root = os.path.dirname(os.path.abspath(script_path))
    
    for folder in user_folders:
        src = os.path.join(user_root, folder)
        # Formato: ruta_origen;nombre_destino
        command.extend(['--add-data', f"{src}{sep}{folder}"])

    # 6. AÑADIR ARCHIVOS MANUALES (Desde la lista de la GUI)
    for data_item in options.get("data_files", []):
        if os.path.exists(data_item):
            if os.path.isdir(data_item):
                folder_name = os.path.basename(data_item)
                command.extend(['--add-data', f"{data_item}{sep}{folder_name}"])
            else:
                command.extend(['--add-data', f"{data_item}{sep}."])

    # 7. INYECTAR HOOK DE PROTECCIÓN
    # Esto asegura que el EXE no se cierre por errores de recursión
    hook_file = create_recursion_hook(output_dir)
    command.extend(['--runtime-hook', hook_file])

    # 8. Script final
    command.append(script_path)
    
    return command
import os
import shutil
import subprocess
import sys 
from pathlib import Path

# Intentamos importar el ofuscador AST
try:
    from .ast_obfuscator import PyObfuscator
except ImportError:
    class PyObfuscator:
        def __init__(self, **kwargs): pass
        def obfuscate_file(self, *args): raise NotImplementedError("AST module missing")

def _ignore_patterns(path, names):
    """Lista negra de carpetas para modo recursivo"""
    ignored = set()
    ignore_dirs = {
        'venv', '.venv', 'env', '.git', '.idea', '.vscode', '__pycache__', 
        'build', 'dist', 'temp_ast_build', 'temp_pyarmor_build', 'output'
    }
    ignore_files = {'.DS_Store', 'Thumbs.db'}

    for name in names:
        if name in ignore_dirs or name in ignore_files:
            ignored.add(name)
        if name.startswith('temp_') or name.endswith('.spec'):
            ignored.add(name)
    return ignored

def process_single_file(src_file, dst_dir, engine_type, options):
    """
    Modo Simple: Solo copia y ofusca UN archivo.
    """
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    src_path = Path(src_file)
    dst_path = os.path.join(dst_dir, src_path.name)
    
    print(f"[*] Single File Mode: Processing {src_path.name}...")
    
    if engine_type == "pyfuscator":
        # PyFuscator: AST Obfuscation
        ast_opts = {k.replace('ast_', ''): v for k, v in options.items() if k.startswith('ast_')}
        obfuscator = PyObfuscator(**ast_opts)
        obfuscator.obfuscate_file(str(src_path), dst_path)
        print(f"   -> AST Obfuscation applied to {dst_path}")
        
    elif engine_type == "pyarmor":
        # PyArmor para un solo archivo
        # PyArmor gen crea carpeta dist, es complejo.
        # Usaremos el comando legacy u opción simple si está disponible, 
        # o simplemente lo copiamos si PyArmor es demasiado complejo para single file "in place".
        # Para simplificar y robustez en V2:
        print("[*] Running PyArmor on single file...")
        cmd = ["pyarmor", "gen", "--output", dst_dir, str(src_path)]
        subprocess.run(cmd, check=True, shell=True if sys.platform=='win32' else False)
        print(f"   -> PyArmor applied.")
    
    return dst_path

def process_project_recursive(src_root, dst_root, engine_type, options):
    """
    Modo Proyecto: Copia todo el árbol y ofusca todo.
    """
    if os.path.exists(dst_root):
        shutil.rmtree(dst_root)
    
    print(f"[*] Cloning project structure from {src_root} to {dst_root}...")
    shutil.copytree(src_root, dst_root, ignore=_ignore_patterns)

    print(f"[*] Applying {engine_type} obfuscation to all .py files...")
    
    ast_obfuscator = None
    if engine_type == "pyfuscator":
        ast_opts = {k.replace('ast_', ''): v for k, v in options.items() if k.startswith('ast_')}
        ast_obfuscator = PyObfuscator(**ast_opts)

    # Recorrer carpeta destino
    for root, dirs, files in os.walk(dst_root):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                try:
                    if engine_type == "pyfuscator":
                        temp_out = full_path + ".tmp"
                        ast_obfuscator.obfuscate_file(full_path, temp_out)
                        os.replace(temp_out, full_path)
                        print(f"   -> Obfuscated (AST): {file}")
                        
                except Exception as e:
                    print(f"   [!] Error obfuscating {file}: {e}")

    # PyArmor Recursivo
    if engine_type == "pyarmor":
        print("[*] Running PyArmor on the entire project structure...")
        cmd = ["pyarmor", "gen", "--recursive", "--output", dst_root + "_armor", dst_root]
        if options.get("pyarmor_add_restrict"): cmd.append("--restrict")
        
        subprocess.run(cmd, check=True, shell=True if sys.platform=='win32' else False)
        
        armor_out = dst_root + "_armor"
        if os.path.exists(armor_out):
            shutil.rmtree(dst_root)
            shutil.move(armor_out, dst_root)

def run_obfuscator(script_path: str, output_dir: str, options: dict) -> str:
    engine_name = options.get("engine")
    is_recursive = options.get("recursive", True) # <--- LEEMOS EL FLAG

    if not options.get("enabled"):
        return script_path

    script_file = Path(script_path)
    
    if is_recursive:
        # --- MODO PROYECTO COMPLETO ---
        project_root = script_file.parent
        temp_folder_name = "temp_project_build"
        temp_project_dir = os.path.join(output_dir, temp_folder_name)
        
        try:
            process_project_recursive(str(project_root), temp_project_dir, engine_name, options)
        except Exception as e:
            raise RuntimeError(f"Obfuscation failed: {e}")
            
        new_script_path = os.path.join(temp_project_dir, script_file.name)
        
    else:
        # --- MODO ARCHIVO ÚNICO ---
        temp_folder_name = "temp_single_build"
        temp_dir = os.path.join(output_dir, temp_folder_name)
        
        try:
            new_script_path = process_single_file(script_path, temp_dir, engine_name, options)
        except Exception as e:
            raise RuntimeError(f"Single file obfuscation failed: {e}")

    if not os.path.exists(new_script_path):
        raise FileNotFoundError(f"Critical: Main script missing after obfuscation at {new_script_path}")
        
    return new_script_path
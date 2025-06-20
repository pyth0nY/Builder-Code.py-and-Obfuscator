import os
import subprocess
import shutil
from pathlib import Path
try:
    from .ast_obfuscator import PyObfuscator
except ImportError:
    class PyObfuscator:
        def __init__(self, **kwargs): pass
        def obfuscate_file(self, *args):
            raise NotImplementedError("El archivo ast_obfuscator.py no se encontró o tiene errores.")

def obfuscate_with_pyarmor(script_path: str, output_path: str, options: dict) -> str:
    """Ejecuta el ofuscador PyArmor con las opciones dadas."""
    temp_obfuscated_dir = os.path.join(output_path, "temp_pyarmor_build")
    if os.path.exists(temp_obfuscated_dir):
        shutil.rmtree(temp_obfuscated_dir)
    
    command = [
        "pyarmor", "obfuscate",
        "--output", temp_obfuscated_dir,
    ]
    

    obf_code = options.get("pyarmor_obf_code", 1)
    obf_mod = options.get("pyarmor_obf_mod", 1)
    add_restrict = options.get("pyarmor_add_restrict", False)
    platform_specific = options.get("pyarmor_platform_specific", False)

    command.extend(["--obf-code", str(obf_code)])
    command.extend(["--obf-mod", str(obf_mod)])
    
    if add_restrict:
        if platform_specific:
            command.extend(["--restrict", "platform"])
        else:
            command.append("--restrict")

    command.append(script_path)
    
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"PyArmor falló:\n{result.stderr}\n{result.stdout}")

    obfuscated_script_path = os.path.join(temp_obfuscated_dir, Path(script_path).name)
    if not os.path.exists(obfuscated_script_path):
        raise FileNotFoundError(f"PyArmor no generó el script esperado.")
        
    return obfuscated_script_path

def obfuscate_with_ast_tool(script_path: str, output_path: str, options: dict) -> str:
    """Ejecuta el ofuscador personalizado basado en AST (PyFuscator)."""
    temp_obfuscated_dir = os.path.join(output_path, "temp_ast_build")
    if not os.path.exists(temp_obfuscated_dir):
        os.makedirs(temp_obfuscated_dir)
        
    output_file_path = os.path.join(temp_obfuscated_dir, f"obfuscated_{Path(script_path).name}")
    

    ast_options = {key.replace('ast_', ''): val for key, val in options.items() if key.startswith('ast_')}

    try:
        obfuscator = PyObfuscator(**ast_options)
        obfuscator.obfuscate_file(script_path, output_file_path)
    except Exception as e:
        raise RuntimeError(f"El ofuscador AST (PyFuscator) falló: {e}")
        
    return output_file_path

def run_obfuscator(script_path: str, output_path: str, options: dict) -> str:
    """
    Función principal: selecciona y ejecuta el motor de ofuscación basado en las opciones.
    """
    engine_name = options.get("engine")
    
    if engine_name == "pyarmor":
        return obfuscate_with_pyarmor(script_path, output_path, options)
    elif engine_name == "pyfuscator":
        return obfuscate_with_ast_tool(script_path, output_path, options)
    else:

        print(f"Advertencia: Motor de ofuscación desconocido: '{engine_name}'. Se omitirá la ofuscación.")
        return script_path

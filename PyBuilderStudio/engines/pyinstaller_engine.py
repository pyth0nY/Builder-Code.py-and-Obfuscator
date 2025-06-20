# Contenido para: engines/pyinstaller_engine.py
import os
from pathlib import Path

def build_command(options: dict) -> list:
    script_path = options.get("script_path")
    if not script_path or not Path(script_path).exists(): return None

    command = ['pyinstaller', '--noconfirm']
    if options.get("one_file"): command.append('--onefile')
    if options.get("no_console"): command.extend(['--noconsole', '--windowed'])
    if options.get("clean"): command.append('--clean')
    if options.get("exe_name"): command.extend(['--name', options.get("exe_name")])
    
    output_dir = options.get("output_dir")
    if output_dir:
        dist_path = os.path.join(output_dir, 'dist')
        build_path = os.path.join(output_dir, 'build')
        command.extend(['--distpath', dist_path])
        command.extend(['--workpath', build_path])
        
    if options.get("icon_path"): command.extend(['--icon', options.get("icon_path")])
    
    for data_item in options.get("data_files", []): command.extend(['--add-data', data_item])
    
    command.append(script_path)
    return command
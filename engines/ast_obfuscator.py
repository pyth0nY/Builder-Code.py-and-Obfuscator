# engines/ast_obfuscator.py
# -*- coding: utf-8 -*-
import ast
import random
import sys
from pathlib import Path

# IMPORTANTE: Importamos desde ast_utils
from .ast_utils import (
    generate_name, xor_string, generate_dummy_code,
    create_opaque_predicate, create_dead_code_branch,
    encode_string_multilayer, DECODE_FUNCTIONS
)

# Soporte para unparse
try:
    def unparse_ast(tree): return ast.unparse(tree)
except AttributeError:
    try:
        import astunparse
        def unparse_ast(tree): return astunparse.unparse(tree)
    except ImportError:
        def unparse_ast(tree): raise RuntimeError("Se requiere Python 3.9+ o 'pip install astunparse'")

class DependencyTracker:
    def __init__(self):
        self.defined_names = set()
        self.used_names = set()
        self.function_names = set()
        self.class_names = set()
        self.imported_names = set()
    
    def add_definition(self, name): self.defined_names.add(name)
    def add_usage(self, name): self.used_names.add(name)
    def add_function(self, name): self.function_names.add(name); self.add_definition(name)
    def add_class(self, name): self.class_names.add(name); self.add_definition(name)
    def add_import(self, name): self.imported_names.add(name); self.add_definition(name)
    
    def is_safe_to_obfuscate(self, name):
        if name in self.used_names and name not in self.defined_names: return False
        return True

class ControlFlowFlattener(ast.NodeTransformer):
    def __init__(self): self.processed_functions = set()
    
    def flatten_body(self, body, function_name=None):
        if (function_name and function_name in self.processed_functions) or len(body) < 4: return body
        
        valid_body = [n for n in body if isinstance(n, ast.stmt) and not isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Try, ast.With, ast.AsyncWith, ast.Import, ast.ImportFrom, ast.For, ast.While))]
        if len(valid_body) < 4: return body
        if function_name: self.processed_functions.add(function_name)

        state_var = generate_name(prefix="state")
        blocks = []
        for i, stmt in enumerate(valid_body):
            next_state = i + 1 if i + 1 < len(valid_body) else -1
            block_body = [stmt]
            if isinstance(stmt, (ast.Return, ast.Break, ast.Continue)): next_state = -1
            
            if next_state != -1:
                block_body.append(ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=next_state)))
            else:
                block_body.append(ast.Break())
                
            condition = ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=i)])
            blocks.append(ast.If(test=condition, body=block_body, orelse=[]) if i == 0 else ast.Elif(test=condition, body=block_body, orelse=[]))

        current = blocks[0]
        for b in blocks[1:]: current.orelse = [b]; current = b
        
        while_loop = ast.While(test=ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.GtE()], comparators=[ast.Constant(value=0)]), body=[blocks[0]], orelse=[])
        return [ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=0)), while_loop]

class AdvancedObfuscator(ast.NodeTransformer):
    def __init__(self, **kwargs):
        self.options = kwargs
        self.name_map = {}
        self.recursion_depth = 0
        self.max_recursion_depth = 20
        self.cff_applied = set()
        self.errors = []
        self.dependency_tracker = DependencyTracker()
        self.protected_names = {
            '__init__', '__main__', '__name__', 'self', 'print', 'input', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'range', 'open', 'super', 'type', 'id', 'Exception', 'True', 'False', 'None', 'args', 'kwargs', 'exit', 'quit', 'format'
        }

    def get_option(self, key, default=False): return self.options.get(key, default)

    def visit(self, node):
        if node is None: return None
        self.recursion_depth += 1
        if self.recursion_depth > self.max_recursion_depth: self.recursion_depth -= 1; return node
        try:
            result = super().visit(node)
            if result and hasattr(result, '_fields'): ast.fix_missing_locations(result)
            self.recursion_depth -= 1
            return result
        except Exception as e:
            self.errors.append(f"Error nodo {type(node).__name__}: {e}")
            self.recursion_depth -= 1
            return node

    def obfuscate_name(self, name, length=12):
        if name in self.protected_names or name.startswith('__') or not self.dependency_tracker.is_safe_to_obfuscate(name): return name
        if name not in self.name_map:
            self.name_map[name] = generate_name(length=length + self.get_option('obfuscation_level', 2))
        return self.name_map[name]

    def visit_FunctionDef(self, node):
        self.dependency_tracker.add_function(node.name)
        if self.get_option('obfuscate_names') and not node.name.startswith('__'): node.name = self.obfuscate_name(node.name)
        if self.get_option('obfuscate_names'):
            for arg in node.args.args:
                if arg.arg not in self.protected_names: self.dependency_tracker.add_definition(arg.arg); arg.arg = self.obfuscate_name(arg.arg, length=8)
        
        self.generic_visit(node)
        
        if self.get_option('control_flow_flattening') and node.name not in self.cff_applied and len(node.body) >= 5:
            try:
                flattener = ControlFlowFlattener()
                flattened = flattener.flatten_body(node.body, node.name)
                if flattened != node.body: node.body = flattened; self.cff_applied.add(node.name)
            except: pass
            
        if self.get_option('dead_code_insertion') and random.random() < 0.1:
            try: node.body.insert(random.randint(0, len(node.body)), create_dead_code_branch())
            except: pass
        return node

    def visit_ClassDef(self, node):
        self.dependency_tracker.add_class(node.name)
        if self.get_option('obfuscate_names'): node.name = self.obfuscate_name(node.name)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store): self.dependency_tracker.add_definition(node.id)
        elif isinstance(node.ctx, ast.Load): self.dependency_tracker.add_usage(node.id)
        if self.get_option('obfuscate_names') and not node.id.startswith('__'): node.id = self.obfuscate_name(node.id)
        return node

    def visit_Constant(self, node):
        # Strings
        if self.get_option('obfuscate_strings') and isinstance(node.value, str) and len(node.value) > 2:
            try:
                if self.get_option('string_encryption'): return encode_string_multilayer(node.value)
                else:
                    enc, key = xor_string(node.value)
                    return ast.Call(func=ast.Name(id='__decode_xor', ctx=ast.Load()), args=[ast.Constant(enc), ast.Constant(key)], keywords=[])
            except: return node
        # Números
        if self.get_option('obfuscate_numbers') and isinstance(node.value, int) and 10 <= abs(node.value) <= 1000:
            try:
                offset = random.randint(50, 200)
                return ast.BinOp(left=ast.Constant(node.value + offset), op=ast.Sub(), right=ast.Constant(offset))
            except: return node
        return node

    def visit_Import(self, node):
        for a in node.names: self.dependency_tracker.add_import(a.asname or a.name)
        return node

    def visit_ImportFrom(self, node):
        for a in node.names: self.dependency_tracker.add_import(a.asname or a.name)
        return node

class PyObfuscator:
    def __init__(self, **kwargs): self.options = kwargs
    
    def _create_decode_functions(self):
        code = ["import base64", "import random"]
        if self.options.get('obfuscate_strings'):
            code.append(DECODE_FUNCTIONS['__decode_multilayer'] if self.options.get('string_encryption') else DECODE_FUNCTIONS['__decode_xor'])
        return "\n".join(code) + "\n"

    def obfuscate_file(self, input_path, output_path):
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f: source = f.read()
        try: tree = ast.parse(source)
        except SyntaxError as e: raise ValueError(f"Sintaxis inválida: {e}")
        
        obfuscator = AdvancedObfuscator(**self.options)
        try: tree = obfuscator.visit(tree); ast.fix_missing_locations(tree)
        except Exception as e: raise RuntimeError(f"Error ofuscación: {e}")
        
        try: final_code = self._create_decode_functions() + unparse_ast(tree)
        except Exception as e: raise RuntimeError(f"Error generación código: {e}")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f: f.write(final_code)
        
        return obfuscator.errors
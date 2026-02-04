import ast
import astunparse 
import random
from pathlib import Path
from .ast_utils import (
    generate_name, xor_string, generate_dummy_code, 
    create_opaque_predicate, create_dead_code_branch,
    encode_string_multilayer, DECODE_FUNCTIONS
)

class ControlFlowFlattener(ast.NodeTransformer):
    def flatten_body(self, body):
        if len(body) < 3: return body
        body = [node for node in body if isinstance(node, ast.stmt)]; 
        if not body: return body
        state_var_name = generate_name(prefix="_state_"); state_var_load = ast.Name(id=state_var_name, ctx=ast.Load()); state_var_store = ast.Name(id=state_var_name, ctx=ast.Store())
        blocks = {}; original_indices = list(range(len(body))); random.shuffle(original_indices)
        dispatch_map = {original_idx: new_idx for new_idx, original_idx in enumerate(original_indices)}
        for i, stmt in enumerate(body):
            block_body = [stmt]; dead_code = create_dead_code_branch()
            if isinstance(stmt, ast.Return): block_body.append(ast.Break())
            else: block_body.append(ast.Assign(targets=[state_var_store], value=ast.Constant(value=dispatch_map.get(i + 1, -1))))
            blocks[dispatch_map[i]] = ast.If(test=ast.Compare(left=state_var_load, ops=[ast.Eq()], comparators=[ast.Constant(value=dispatch_map[i])]), body=block_body, orelse=[])
        loop_body = [blocks[i] for i in range(len(body))]
        while_loop = ast.While(test=ast.Compare(left=state_var_load, ops=[ast.NotEq()], comparators=[ast.Constant(value=-1)]), body=loop_body, orelse=[])
        return [ast.Assign(targets=[state_var_store], value=ast.Constant(value=dispatch_map.get(0, -1))), while_loop]

class AdvancedObfuscator(ast.NodeTransformer):
    def __init__(self, **kwargs):
        self.options = kwargs; self.name_map = {}; self.recursion_depth = 0; self.max_recursion_depth = 15; self.cff_applied = set()
        self.protected_names = {'__init__', '__main__', '__name__', '__file__', 'print', 'input', 'len', 'str', 'int', 'float', 'list', 'dict', 'tuple', 'set', 'range', 'open', 'super', 'type', *DECODE_FUNCTIONS.keys()}
    def get_option(self, key, default=False): return self.options.get(key, default)
    def visit(self, node):
        self.recursion_depth += 1
        if self.recursion_depth > self.max_recursion_depth: self.recursion_depth -= 1; return node
        try: result = super().visit(node); ast.fix_missing_locations(result)
        except Exception: result = node
        self.recursion_depth -= 1; return result
    def obfuscate_name(self, name, length=12):
        if name in self.protected_names or name.startswith('__'): return name
        if name not in self.name_map: self.name_map[name] = generate_name(length=length + self.get_option('obfuscation_level', 2))
        return self.name_map[name]
    def visit_FunctionDef(self, node):
        if self.get_option('obfuscate_names'): node.name = self.obfuscate_name(node.name)
        if self.get_option('obfuscate_names'):
            for arg in node.args.args: arg.arg = self.obfuscate_name(arg.arg, length=8)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]; new_body = []
        for stmt in node.body:
            processed_stmt = self.visit(stmt)
            if isinstance(processed_stmt, list): new_body.extend(processed_stmt)
            else: new_body.append(processed_stmt)
            if self.get_option('add_dummy_code') and random.random() < 0.15: new_body.append(generate_dummy_code(self.get_option('obfuscation_level')))
        node.body = new_body
        if self.get_option('control_flow_flattening') and node.name not in self.cff_applied:
            node.body = ControlFlowFlattener().flatten_body(node.body); self.cff_applied.add(node.name)
        if self.get_option('dead_code_insertion') and random.random() < 0.25: node.body.insert(random.randint(0, len(node.body)), create_dead_code_branch())
        return node
    def visit_ClassDef(self, node):
        if self.get_option('obfuscate_names'): node.name = self.obfuscate_name(node.name)
        self.generic_visit(node); return node
    def visit_Name(self, node):
        if self.get_option('obfuscate_names') and isinstance(node.ctx, (ast.Store, ast.Load)): node.id = self.obfuscate_name(node.id)
        return node
    def visit_Constant(self, node):
        if self.get_option('obfuscate_strings') and isinstance(node.value, str) and len(node.value) > 2:
            if self.get_option('string_encryption'): return encode_string_multilayer(node.value)
            else: encoded, key = xor_string(node.value); return ast.Call(func=ast.Name(id='__decode_xor', ctx=ast.Load()), args=[ast.Constant(value=encoded), ast.Constant(value=key)], keywords=[])
        if self.get_option('obfuscate_numbers') and isinstance(node.value, int) and 1 < abs(node.value) < 100000:
            op = random.choice([ast.Add(), ast.Sub(), ast.Mult(), ast.Xor]);
            if isinstance(op, ast.Xor): key = random.randint(100, 1000); return ast.BinOp(left=ast.Constant(value=node.value ^ key), op=ast.Xor(), right=ast.Constant(value=key))
            else: offset = random.randint(100, 1000); return ast.BinOp(left=ast.Constant(value=node.value + offset), op=ast.Sub(), right=ast.Constant(value=offset))
        return node
    def visit_If(self, node):
        if self.get_option('opaque_predicates') and random.random() < 0.4:
            node.test = ast.BoolOp(op=ast.And(), values=[create_opaque_predicate(always_true=True), self.visit(node.test)])
            if not node.orelse and random.random() < 0.5: node.orelse = [create_dead_code_branch()]
        self.generic_visit(node); return node
    def visit_Import(self, node):
        if not self.get_option('obfuscate_names'): return node
        new_nodes = []; 
        for alias in node.names:
            target_name = alias.asname or alias.name; import_call = ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()), args=[encode_string_multilayer(alias.name)], keywords=[])
            new_nodes.append(ast.Assign(targets=[ast.Name(id=self.obfuscate_name(target_name), ctx=ast.Store())], value=import_call))
        return new_nodes if new_nodes else ast.Pass()
    def visit_ImportFrom(self, node):
        if not self.get_option('obfuscate_names'): return node
        temp_module_var = generate_name(prefix="_mod_");
        from_list = [ast.Constant(value=alias.name) for alias in node.names]
        import_call = ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()), args=[encode_string_multilayer(node.module), ast.Constant(value=None), ast.Constant(value=None), ast.List(elts=from_list, ctx=ast.Load())], keywords=[])
        new_nodes = [ast.Assign(targets=[ast.Name(id=temp_module_var, ctx=ast.Store())], value=import_call)]
        for alias in node.names:
            target_name = alias.asname or alias.name
            getattr_call = ast.Call(func=ast.Name(id='getattr', ctx=ast.Load()), args=[ast.Name(id=temp_module_var, ctx=ast.Load()), encode_string_multilayer(alias.name)], keywords=[])
            new_nodes.append(ast.Assign(targets=[ast.Name(id=self.obfuscate_name(target_name), ctx=ast.Store())], value=getattr_call))
        return new_nodes if new_nodes else ast.Pass()

class PyObfuscator:
    def __init__(self, **kwargs): self.options = kwargs
    def _create_decode_functions(self):
        code = []; imports = "import base64\n"
        if self.options.get('obfuscate_strings', False):
            if self.options.get('string_encryption', False): code.append(DECODE_FUNCTIONS['__decode_multilayer'])
            else: code.append(DECODE_FUNCTIONS['__decode_xor'])
        if not code: return ""
        return imports + "\n".join(code)
    def obfuscate_file(self, input_path, output_path):
        input_path, output_path = Path(input_path), Path(output_path)
        try:
            with open(input_path, "r", encoding="utf-8") as f: source = f.read()
        except Exception:
            with open(input_path, "r", encoding="latin-1") as f: source = f.read()
        try: tree = ast.parse(source)
        except SyntaxError as e: raise ValueError(f"Sintaxis inválida en {input_path.name}: {e}")
        try: obfuscated_tree = AdvancedObfuscator(**self.options).visit(tree); ast.fix_missing_locations(obfuscated_tree)
        except Exception as e: raise RuntimeError(f"Error inesperado en ofuscación: {e}")
        try: obfuscated_code = astunparse.unparse(obfuscated_tree)
        except Exception as e: raise RuntimeError(f"Error generando código ofuscado: {e}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f: f.write(self._create_decode_functions() + "\n\n" + obfuscated_code)

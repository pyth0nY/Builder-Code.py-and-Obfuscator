# engines/ast_utils.py
# -*- coding: utf-8 -*-
import ast
import base64
import random
import string
import sys

def generate_name(length=12, prefix=""):
    confusing_chars = "Il1O0"
    unicode_chars = "αβγδεζηθικλμνξοπρστυφχψω"
    base_chars = string.ascii_letters + string.digits
    population = base_chars + confusing_chars
    
    if random.random() < 0.3:
        population += unicode_chars
    
    name = ''.join(random.choices(population, k=length))
    
    if not name[0].isalpha() and name[0] != '_':
        name = random.choice(string.ascii_letters + '_') + name[1:]
    
    reserved_endings = ['__', '_builtin', '_module', '_class']
    for ending in reserved_endings:
        if name.endswith(ending):
            name = name[:-len(ending)] + generate_name(length=3)
    
    return prefix + name

def xor_string(s: str):
    if not s or len(s) > 200:
        return s, ""
    try:
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 16)))
        encoded = []
        for i, char in enumerate(s):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(char) ^ ord(key_c))
            if ord(encoded_c) < 32 or ord(encoded_c) > 126:
                return s, ""
            encoded.append(encoded_c)
        return ''.join(encoded), key
    except Exception:
        return s, ""

# --- Funciones de codificación multicapa ---
def _encode_b64(s): 
    try: return base64.b64encode(s.encode('utf-8')).decode('ascii') if s and len(s) <= 100 else s
    except: return s

def _encode_rot(s): 
    try: return ''.join(chr((ord(c) + 13) % 256) for c in s) if s and len(s) <= 100 else s
    except: return s

def _encode_reverse(s): 
    try: return s[::-1] if s else s
    except: return s

def _encode_hex(s): 
    try: return s.encode('utf-8').hex() if s and len(s) <= 50 else s
    except: return s

ENCODING_LAYERS = [
    (0, _encode_b64),
    (1, _encode_rot),
    (2, _encode_reverse),
    (3, _encode_hex)
]

def encode_string_multilayer(s: str):
    if not s or len(s) > 100:
        return ast.Constant(value=s)
    encoded = s
    applied_layers_indices = []
    try:
        layers_to_apply = list(range(len(ENCODING_LAYERS)))
        random.shuffle(layers_to_apply)
        num_layers = random.randint(1, 2)
        for i in range(num_layers):
            layer_idx = layers_to_apply[i]
            func = ENCODING_LAYERS[layer_idx][1]
            new_encoded = func(encoded)
            if new_encoded and new_encoded != encoded and len(new_encoded) < 500:
                encoded = new_encoded
                applied_layers_indices.append(layer_idx)
            else:
                break
        if not applied_layers_indices:
            return ast.Constant(value=s)
        return ast.Call(
            func=ast.Name(id='__decode_multilayer', ctx=ast.Load()),
            args=[
                ast.Constant(value=encoded),
                ast.List(elts=[ast.Constant(value=i) for i in applied_layers_indices], ctx=ast.Load())
            ],
            keywords=[]
        )
    except Exception:
        return ast.Constant(value=s)

DECODE_FUNCTIONS = {
    '__decode_xor': """
def __decode_xor(data, key):
    if not data or not key: return data
    try: return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
    except: return data
""",
    '__decode_multilayer': """
def __safe_b64_decode(s):
    try: return __import__('base64').b64decode(s.encode('ascii')).decode('utf-8') if s else s
    except: return s
def __safe_rot_decode(s):
    try: return ''.join(chr((ord(c) - 13 + 256) % 256) for c in s) if s else s
    except: return s
def __safe_reverse(s):
    try: return s[::-1] if s else s
    except: return s
def __safe_hex_decode(s):
    try: return bytes.fromhex(s).decode('utf-8') if s else s
    except: return s

__DECODING_LAYERS = {0: __safe_b64_decode, 1: __safe_rot_decode, 2: __safe_reverse, 3: __safe_hex_decode}

def __decode_multilayer(data, layers):
    if not data or not layers: return data
    try:
        d = data
        for l in reversed(layers):
            if l in __DECODING_LAYERS: d = __DECODING_LAYERS[l](d)
        return d
    except: return data
"""
}

def create_opaque_predicate(always_true=True):
    x = random.randint(5, 50)
    if always_true:
        return ast.Compare(left=ast.BinOp(left=ast.Constant(x), op=ast.Add(), right=ast.Constant(0)), ops=[ast.Eq()], comparators=[ast.Constant(x)])
    else:
        return ast.Compare(left=ast.Constant(x * 2), ops=[ast.Eq()], comparators=[ast.Constant(x * 2 + 1)])

def create_dead_code_branch():
    var1 = generate_name(6, prefix="dead")
    body = [ast.Assign(targets=[ast.Name(id=var1, ctx=ast.Store())], value=ast.Constant(random.randint(100, 999)))]
    return ast.If(test=create_opaque_predicate(always_true=False), body=body, orelse=[])

def generate_dummy_code(level=2):
    var_name = generate_name(6, prefix="dummy")
    val = ast.Constant(random.randint(1, 100))
    return ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=val)
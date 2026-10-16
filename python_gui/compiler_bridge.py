import ctypes
import json
import os
import sys

# Locate rust_engine.dll
dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rust_engine", "target", "release", "rust_engine.dll"))
if not os.path.exists(dll_path):
    dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rust_engine", "target", "debug", "rust_engine.dll"))

if not os.path.exists(dll_path):
    raise FileNotFoundError(f"Could not find rust_engine.dll at {dll_path}")

lib = ctypes.CDLL(dll_path)

lib.compile_expression.argtypes = [ctypes.c_char_p]
lib.compile_expression.restype = ctypes.c_void_p

lib.free_string.argtypes = [ctypes.c_void_p]
lib.free_string.restype = None

def compile_expr(expr: str) -> dict:
    expr_bytes = expr.encode('utf-8')
    raw_ptr = lib.compile_expression(expr_bytes)
    if not raw_ptr:
        return {"success": False, "error_message": "Null pointer returned from Rust engine"}

    try:
        json_bytes = ctypes.string_at(raw_ptr)
        json_str = json_bytes.decode('utf-8')
        return json.loads(json_str)
    finally:
        lib.free_string(raw_ptr)

if __name__ == "__main__":
    result = compile_expr("(10 + 20) * 3 ^ 2")
    print("Success:", result.get("success"))
    print("Final Result:", result.get("final_result"))
    print("Comp Time:", result.get("compilation_time_us"), "us")
    print("Token count:", len(result.get("tokens", [])))
    print("3AC quads:", len(result.get("unoptimized_3ac", [])))
    print("Bytecode count:", len(result.get("bytecode", [])))
    print("VM steps:", len(result.get("vm_steps", [])))

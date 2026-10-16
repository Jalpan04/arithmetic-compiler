"""
Top-level runner for the Interactive Arithmetic Expression Compiler
Automatically checks and builds the Rust engine if needed, then starts the PyQt6 GUI.
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUST_DIR = os.path.join(BASE_DIR, "rust_engine")
DLL_PATH = os.path.join(RUST_DIR, "target", "release", "rust_engine.dll")


def ensure_engine_built():
    if not os.path.exists(DLL_PATH):
        print("Rust engine DLL not found. Compiling with cargo build --release...")
        res = subprocess.run(["cargo", "build", "--release"], cwd=RUST_DIR)
        if res.returncode != 0:
            print("Failed to build Rust engine. Ensure cargo is installed and in PATH.")
            sys.exit(1)
        print("Rust engine compiled successfully.")


def main():
    ensure_engine_built()

    sys.path.insert(0, os.path.join(BASE_DIR, "python_gui"))
    from main_window import main as run_gui
    run_gui()


if __name__ == "__main__":
    main()

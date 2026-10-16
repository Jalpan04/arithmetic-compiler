# Interactive Arithmetic Expression Compiler

A mini-project for 7th-Semester Compiler Design implementing an **Interactive Arithmetic Expression Compiler**. The system compiles arithmetic expressions into stack-machine bytecode and interactively executes them on a virtual machine step-by-step.

---

## Architecture & Compiler Stages

The project strictly focuses on compiling arithmetic expressions:

1. **Lexical Analysis (Scanner)**: Tokenizes input arithmetic expressions into typed tokens (`NUMBER`, `PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`, `CARET`, `LPAREN`, `RPAREN`) with character spans.
2. **Syntax Analysis (Pratt Parser)**: Constructs an Abstract Syntax Tree (AST) enforcing standard arithmetic operator precedence and right-associativity for exponentiation (`^`).
3. **Target Code Generation (Bytecode)**: Translates the AST directly into stack-machine bytecode instructions (`PUSH`, `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `POW`, `NEG`, `HALT`).
4. **Virtual Machine Execution**: Executes the bytecode on an operand stack, recording cycle-by-cycle snapshots allowing interactive step-forward, step-backward, and run controls.

---

## Directory Structure

```text
project/
├── run.py                       # Root launcher (builds DLL if needed and starts GUI)
├── run.bat                      # Windows one-click batch launcher
├── README.md                    # Project documentation
│
├── rust_engine/                 # Rust compiler engine
│   ├── Cargo.toml               # Configured for cdylib and CLI binary
│   └── src/
│       ├── lib.rs               # Compiler pipeline coordinator and C-ABI FFI
│       ├── main.rs              # Standalone CLI binary for terminal usage
│       ├── token.rs             # Token types and structures
│       ├── lexer.rs             # Lexical analyzer
│       ├── ast.rs               # AST nodes and tree layout
│       ├── parser.rs            # Top-Down Operator Precedence (Pratt Parser)
│       ├── bytecode.rs          # Stack-machine bytecode generator
│       └── vm.rs                # Stack virtual machine execution engine
│
├── python_gui/                  # PyQt6 Desktop GUI
│   ├── __init__.py
│   ├── main_window.py           # Main window with tabs and controls
│   ├── compiler_bridge.py       # Ctypes FFI bridge to rust_engine.dll
│   ├── ast_visualizer.py        # Interactive AST graph visualizer
│   ├── vm_stepper.py            # Live Stack visualizer and step debugger
│   └── styles.py                # Modern stylesheet
│
└── tests/                       # Test suite
    ├── __init__.py
    └── test_compiler.py         # Unit tests for arithmetic compilation and execution
```

---

## Running the Application

### 1. Launch Desktop GUI

```powershell
python run.py
```
*(Or double-click `run.bat`)*

**Features in GUI**:
- **Bytecode & Execution**: Disassembled bytecode table, visual operand stack, and interactive stepping controls (`Step Forward`, `Step Back`, `Play`, `Reset`).
- **Syntax Tree (AST)**: Interactive tree hierarchy with zoom and pan.
- **Lexer Tokens**: Table of scanned tokens with type and span information.

### 2. Run Standalone CLI

```powershell
cargo run --manifest-path rust_engine/Cargo.toml --release -- "(3 + 5) * 2 ^ 3"
```

### 3. Run Automated Tests

```powershell
python tests/test_compiler.py
```

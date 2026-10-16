"""
Interactive Arithmetic Expression Compiler - Main Application Window
"""

import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from compiler_bridge import compile_expr
from ast_visualizer import AstVisualizerWidget
from vm_stepper import VmStepperWidget
from styles import MAIN_STYLESHEET


class CompilerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Arithmetic Expression Compiler")
        self.resize(1150, 780)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._setup_ui()
        self._load_presets()
        # Compile default initial expression
        self.compile_current_expression()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Top Bar: Title, Presets, Input, Compile Button
        top_box = QFrame()
        top_box.setObjectName("TopBox")
        top_box.setStyleSheet("""
            #TopBox {
                background-color: #121722;
                border: 1px solid #1e2638;
                border-radius: 8px;
                padding: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        top_layout = QVBoxLayout(top_box)
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(8)

        # Title Row
        title_row = QHBoxLayout()
        title_row.setSpacing(14)

        app_title = QLabel("Interactive Arithmetic Expression Compiler")
        app_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        title_row.addWidget(app_title)

        title_row.addStretch()

        self.result_badge = QLabel("Result: -")
        self.result_badge.setStyleSheet("color: #38bdf8; font-weight: 700; font-size: 14px; font-family: monospace; background: transparent;")
        title_row.addWidget(self.result_badge)

        top_layout.addLayout(title_row)

        # Input Row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        preset_lbl = QLabel("Presets:")
        preset_lbl.setStyleSheet("color: #94a3b8; font-weight: 600;")
        input_row.addWidget(preset_lbl)

        self.combo_presets = QComboBox()
        self.combo_presets.setFixedWidth(280)
        self.combo_presets.currentIndexChanged.connect(self._preset_selected)
        input_row.addWidget(self.combo_presets)

        self.input_expr = QLineEdit()
        self.input_expr.setPlaceholderText("Enter arithmetic expression e.g. (3 + 5) * 2 ^ 3 ...")
        self.input_expr.returnPressed.connect(self.compile_current_expression)
        input_row.addWidget(self.input_expr, 1)

        self.btn_compile = QPushButton("Compile & Run")
        self.btn_compile.setObjectName("CompileBtn")
        self.btn_compile.clicked.connect(self.compile_current_expression)
        input_row.addWidget(self.btn_compile)

        top_layout.addLayout(input_row)
        main_layout.addWidget(top_box)

        # Error notification bar
        self.error_bar = QFrame()
        self.error_bar.setStyleSheet("""
            QFrame {
                background-color: #450a0a;
                border: 1px solid #dc2626;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        error_layout = QHBoxLayout(self.error_bar)
        error_layout.setContentsMargins(6, 4, 6, 4)
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #fca5a5; font-weight: 600; font-family: monospace;")
        error_layout.addWidget(self.error_lbl)
        self.error_bar.hide()
        main_layout.addWidget(self.error_bar)

        # Central Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        # TAB 1: Bytecode & Interactive VM Stepper
        self.vm_widget = VmStepperWidget()
        self.tabs.addTab(self.vm_widget, "Bytecode & Execution")

        # TAB 2: AST Visualizer
        self.ast_widget = AstVisualizerWidget()
        self.tabs.addTab(self.ast_widget, "Syntax Tree (AST)")

        # TAB 3: Lexical Analysis
        self.tab_tokens = QWidget()
        self._setup_tokens_tab()
        self.tabs.addTab(self.tab_tokens, "Lexer Tokens")

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready. Enter an arithmetic expression and press Compile.")

    def _load_presets(self):
        presets = [
            ("(3 + 5) * 2 ^ 3", "Precedence & Exponent"),
            ("(100 - 25) / 5 * 2 + 3 ^ 2", "Multi-stage Operations"),
            ("-15 + 2 * (8 % 3)", "Unary minus & Modulo"),
            ("(2 + 3) * (7 - 2) ^ 2", "Parenthesized Subexpressions"),
            ("3.14159 * 2.0 ^ 3", "Floating Point Literals"),
            ("10 / (5 - 5)", "Error: Division by Zero"),
            ("3 + * 5", "Error: Syntax Error"),
            ("(4 + 2", "Error: Mismatched Parentheses"),
        ]
        for expr, desc in presets:
            self.combo_presets.addItem(f"{expr}  [{desc}]", expr)

        self.input_expr.setText("(3 + 5) * 2 ^ 3")

    def _preset_selected(self, index: int):
        data = self.combo_presets.itemData(index)
        if data:
            self.input_expr.setText(data)
            self.compile_current_expression()

    def _setup_tokens_tab(self):
        layout = QVBoxLayout(self.tab_tokens)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        lbl = QLabel("Lexical Analysis: Scanned Token Stream")
        lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #38bdf8;")
        layout.addWidget(lbl)

        self.table_tokens = QTableWidget()
        self.table_tokens.setColumnCount(5)
        self.table_tokens.setHorizontalHeaderLabels(["Index", "Token Type", "Lexeme", "Span [Start..End]", "Length"])
        self.table_tokens.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_tokens.horizontalHeader().setStretchLastSection(True)
        self.table_tokens.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_tokens)

    def compile_current_expression(self):
        expr = self.input_expr.text().strip()
        if not expr:
            return

        res = compile_expr(expr)

        # Check for errors
        if not res.get("success", False):
            stage = res.get("error_stage", "Compilation")
            msg = res.get("error_message", "Unknown error")
            pos = res.get("error_position")
            pos_info = f" at position {pos}" if pos is not None else ""

            self.error_lbl.setText(f"[{stage} Error{pos_info}]: {msg}")
            self.error_bar.show()

            self.result_badge.setText("Result: ERROR")
            self.result_badge.setStyleSheet("color: #f87171; font-weight: 700; font-size: 14px; font-family: monospace; background: transparent;")
            self.status.showMessage(f"Compilation failed during {stage}")
            return

        # Success: hide error bar
        self.error_bar.hide()

        final_val = res.get("final_result", 0.0)
        self.result_badge.setText(f"Result: {final_val}")
        self.result_badge.setStyleSheet("color: #34d399; font-weight: 700; font-size: 14px; font-family: monospace; background: transparent;")

        tokens = res.get("tokens", [])
        ast = res.get("ast", {})
        node_count = res.get("node_count", 0)
        tree_depth = res.get("tree_depth", 0)
        bytecode = res.get("bytecode", [])
        vm_steps = res.get("vm_steps", [])

        # Update Bytecode & VM Execution Tab
        self.vm_widget.load_execution_data(bytecode, vm_steps)

        # Update AST Visualizer Tab
        self.ast_widget.render_ast(ast, node_count=node_count, tree_depth=tree_depth)

        # Update Tokens Tab
        self._populate_tokens_table(tokens)

        self.status.showMessage("Expression compiled and executed successfully.")

    def _populate_tokens_table(self, tokens: list):
        self.table_tokens.setRowCount(len(tokens))
        for row, tok in enumerate(tokens):
            idx_item = QTableWidgetItem(str(row))
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tokens.setItem(row, 0, idx_item)

            type_str = tok.get("type_name", "")
            type_item = QTableWidgetItem(type_str)
            if type_str == "NUMBER":
                type_item.setForeground(QColor("#34d399"))
            elif type_str in ["PLUS", "MINUS", "STAR", "SLASH", "PERCENT", "CARET"]:
                type_item.setForeground(QColor("#38bdf8"))
            elif type_str in ["LPAREN", "RPAREN"]:
                type_item.setForeground(QColor("#fbbf24"))
            else:
                type_item.setForeground(QColor("#94a3b8"))
            self.table_tokens.setItem(row, 1, type_item)

            lexeme_item = QTableWidgetItem(f"'{tok.get('lexeme', '')}'")
            self.table_tokens.setItem(row, 2, lexeme_item)

            start = tok.get("start", 0)
            end = tok.get("end", 0)
            span_item = QTableWidgetItem(f"[{start} .. {end}]")
            span_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tokens.setItem(row, 3, span_item)

            length_item = QTableWidgetItem(str(end - start))
            length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tokens.setItem(row, 4, length_item)


def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CompilerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

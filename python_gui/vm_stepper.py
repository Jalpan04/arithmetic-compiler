"""
Interactive Stack-Machine Virtual Machine Debugger and Stepper
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QSlider,
    QGroupBox, QFrame, QScrollArea
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QTimer


class StackBoxWidget(QFrame):
    """Visual widget representing a single item on the operand stack"""
    def __init__(self, index: int, value: float, is_top: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("StackBox")
        self.setFixedHeight(42)

        tag_color = "#38bdf8" if is_top else "#64748b"
        border_color = "#38bdf8" if is_top else "#1e2638"
        self.setStyleSheet(f"""
            #StackBox {{
                background-color: #121722;
                border: 1px solid {border_color};
                border-radius: 6px;
                margin: 2px 8px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)

        tag = "TOP -> " if is_top else "       "
        idx_lbl = QLabel(f"{tag}[{index}]")
        idx_lbl.setFont(QFont("Cascadia Code", 11, QFont.Weight.Bold))
        idx_lbl.setStyleSheet("color: #94a3b8;")

        val_lbl = QLabel(f"{value}")
        val_lbl.setFont(QFont("Cascadia Code", 13, QFont.Weight.Bold))
        val_lbl.setStyleSheet("color: #f8fafc;")

        layout.addWidget(idx_lbl)
        layout.addStretch()
        layout.addWidget(val_lbl)


class VmStepperWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps = []
        self.bytecode = []
        self.current_step_idx = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step_forward)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()
        title_lbl = QLabel("Stack Machine Virtual Machine (Interactive Stepper)")
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #38bdf8;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.step_badge = QLabel("Step 0 / 0")
        self.step_badge.setStyleSheet("color: #38bdf8; font-weight: 700; font-family: monospace; font-size: 13px; background: transparent;")
        header_layout.addWidget(self.step_badge)

        main_layout.addLayout(header_layout)

        # Split area: Bytecode on left, Stack visualizer on right
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # Left: Bytecode Table
        bc_box = QGroupBox("Bytecode Disassembly")
        bc_layout = QVBoxLayout(bc_box)
        bc_layout.setContentsMargins(6, 12, 6, 6)

        self.table_bc = QTableWidget()
        self.table_bc.setColumnCount(4)
        self.table_bc.setHorizontalHeaderLabels(["PC", "Opcode", "Operand", "Mnemonic"])
        self.table_bc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_bc.horizontalHeader().setStretchLastSection(True)
        self.table_bc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_bc.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bc_layout.addWidget(self.table_bc)
        content_layout.addWidget(bc_box, 1)

        # Right: Operand Stack Visualizer
        stack_box = QGroupBox("Operand Stack (Memory)")
        stack_layout = QVBoxLayout(stack_box)
        stack_layout.setContentsMargins(6, 12, 6, 6)

        self.stack_scroll = QScrollArea()
        self.stack_scroll.setWidgetResizable(True)
        self.stack_scroll.setStyleSheet("QScrollArea { border: none; background-color: #11151e; }")

        self.stack_container = QWidget()
        self.stack_container.setStyleSheet("background-color: #11151e;")
        self.stack_items_layout = QVBoxLayout(self.stack_container)
        self.stack_items_layout.setContentsMargins(4, 10, 4, 10)
        self.stack_items_layout.setSpacing(4)
        self.stack_items_layout.addStretch()

        self.stack_scroll.setWidget(self.stack_container)
        stack_layout.addWidget(self.stack_scroll)

        self.stack_depth_lbl = QLabel("Stack: Empty")
        self.stack_depth_lbl.setStyleSheet("color: #64748b; font-size: 11px; padding: 4px;")
        stack_layout.addWidget(self.stack_depth_lbl)

        content_layout.addWidget(stack_box, 1)
        main_layout.addLayout(content_layout, 1)

        # Step Explanation Banner
        self.desc_frame = QFrame()
        self.desc_frame.setObjectName("DescFrame")
        self.desc_frame.setStyleSheet("""
            #DescFrame {
                background-color: #121722;
                border: 1px solid #1e2638;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        desc_layout = QHBoxLayout(self.desc_frame)
        desc_layout.setContentsMargins(8, 6, 8, 6)
        self.desc_lbl = QLabel("Click Step Forward or Play to execute instructions step-by-step.")
        self.desc_lbl.setStyleSheet("font-size: 13px; color: #f1f5f9; font-family: 'Segoe UI', sans-serif;")
        desc_layout.addWidget(self.desc_lbl)
        main_layout.addWidget(self.desc_frame)

        # Bottom Playback Controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        self.btn_reset = QPushButton("Reset (|<)")
        self.btn_reset.setObjectName("SecondaryBtn")
        self.btn_reset.clicked.connect(self.reset_stepper)
        ctrl_layout.addWidget(self.btn_reset)

        self.btn_back = QPushButton("Step Back (<)")
        self.btn_back.setObjectName("SecondaryBtn")
        self.btn_back.clicked.connect(self.step_back)
        ctrl_layout.addWidget(self.btn_back)

        self.btn_play = QPushButton("Play")
        self.btn_play.setStyleSheet("background-color: #0284c7; font-weight: 700;")
        self.btn_play.clicked.connect(self.toggle_play)
        ctrl_layout.addWidget(self.btn_play)

        self.btn_forward = QPushButton("Step Forward (>)")
        self.btn_forward.setStyleSheet("background-color: #2563eb; font-weight: 700;")
        self.btn_forward.clicked.connect(self.step_forward)
        ctrl_layout.addWidget(self.btn_forward)

        self.btn_end = QPushButton("Jump to End (>|)")
        self.btn_end.setObjectName("SecondaryBtn")
        self.btn_end.clicked.connect(self.jump_to_end)
        ctrl_layout.addWidget(self.btn_end)

        ctrl_layout.addSpacing(20)

        speed_lbl = QLabel("Speed:")
        speed_lbl.setStyleSheet("color: #94a3b8; font-weight: 600;")
        ctrl_layout.addWidget(speed_lbl)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(100, 1500)
        self.speed_slider.setValue(600)
        self.speed_slider.setFixedWidth(120)
        ctrl_layout.addWidget(self.speed_slider)

        main_layout.addLayout(ctrl_layout)

    def load_execution_data(self, bytecode: list, steps: list):
        self.timer.stop()
        self.btn_play.setText("Play")
        self.bytecode = bytecode or []
        self.steps = steps or []
        self.current_step_idx = 0

        # Populate bytecode table
        self.table_bc.setRowCount(len(self.bytecode))
        for row, bc in enumerate(self.bytecode):
            pc_str = f"0x{bc.get('index', 0):04X}"
            op_code = bc.get("opcode", "")
            if isinstance(op_code, dict):
                op_code = list(op_code.keys())[0] if op_code else ""
            operand_str = str(bc.get("operand", "")) if bc.get("operand") is not None else "-"
            mnemonic_str = bc.get("mnemonic", "")

            item_pc = QTableWidgetItem(pc_str)
            item_pc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_bc.setItem(row, 0, item_pc)

            item_op = QTableWidgetItem(str(op_code))
            self.table_bc.setItem(row, 1, item_op)

            item_val = QTableWidgetItem(operand_str)
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_bc.setItem(row, 2, item_val)

            item_mn = QTableWidgetItem(mnemonic_str)
            self.table_bc.setItem(row, 3, item_mn)

        self.update_display()

    def update_display(self):
        total_steps = len(self.steps)
        if total_steps == 0:
            self.step_badge.setText("Step 0 / 0")
            self.desc_lbl.setText("No bytecode instructions to execute.")
            self._clear_stack_display()
            return

        self.step_badge.setText(f"Step {self.current_step_idx + 1} / {total_steps}")
        current_step = self.steps[self.current_step_idx]

        # Highlight current instruction in bytecode table
        pc = current_step.get("pc", 0)
        self.table_bc.selectRow(pc)

        # Update description banner
        desc = current_step.get("description", "")
        self.desc_lbl.setText(f"Cycle {current_step.get('step', 0)} (PC: {pc}): {desc}")

        # Render operand stack after instruction execution
        stack_vals = current_step.get("stack_after", [])
        self._render_stack(stack_vals)

    def _render_stack(self, stack: list):
        self._clear_stack_display()

        if not stack:
            self.stack_depth_lbl.setText("Stack Depth: 0 (Empty)")
            empty_lbl = QLabel("Stack is currently empty")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #475569; font-style: italic; padding: 20px;")
            self.stack_items_layout.insertWidget(0, empty_lbl)
            return

        self.stack_depth_lbl.setText(f"Stack Depth: {len(stack)} items")

        # Top of stack at the top of the layout
        for i in reversed(range(len(stack))):
            val = stack[i]
            is_top = (i == len(stack) - 1)
            box = StackBoxWidget(i, val, is_top=is_top)
            self.stack_items_layout.insertWidget(len(stack) - 1 - i, box)

    def _clear_stack_display(self):
        while self.stack_items_layout.count() > 1:
            item = self.stack_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def step_forward(self):
        if self.current_step_idx + 1 < len(self.steps):
            self.current_step_idx += 1
            self.update_display()
        else:
            self.timer.stop()
            self.btn_play.setText("Play")

    def step_back(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.update_display()

    def reset_stepper(self):
        self.timer.stop()
        self.btn_play.setText("Play")
        self.current_step_idx = 0
        self.update_display()

    def jump_to_end(self):
        self.timer.stop()
        self.btn_play.setText("Play")
        if self.steps:
            self.current_step_idx = len(self.steps) - 1
            self.update_display()

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("Play")
        else:
            if self.current_step_idx >= len(self.steps) - 1:
                self.current_step_idx = 0
            interval = self.speed_slider.value()
            self.timer.start(interval)
            self.btn_play.setText("Pause")

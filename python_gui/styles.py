"""
Professional Modern Dark Theme Stylesheet for Interactive Compiler
"""

MAIN_STYLESHEET = """
QMainWindow, QWidget#CentralWidget {
    background-color: #0f131a;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #232c3d;
    background-color: #141a24;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #121722;
    color: #64748b;
    padding: 10px 18px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 600;
    border: 1px solid transparent;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #141a24;
    color: #38bdf8;
    border: 1px solid #232c3d;
    border-bottom: 1px solid #141a24;
}

QTabBar::tab:hover:!selected {
    background-color: #161d2b;
    color: #cbd5e1;
}

/* Input Fields */
QLineEdit {
    background-color: #18202d;
    border: 1px solid #2d384d;
    border-radius: 6px;
    padding: 10px 14px;
    color: #f8fafc;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 14px;
    selection-background-color: #0284c7;
}

QLineEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #1b2433;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton#CompileBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#CompileBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #1d4ed8);
}

QPushButton#SecondaryBtn {
    background-color: #232c3d;
    color: #cbd5e1;
    border: 1px solid #2e3a50;
}

QPushButton#SecondaryBtn:hover {
    background-color: #2c374d;
    color: #f8fafc;
}

/* ComboBox */
QComboBox {
    background-color: #18202d;
    border: 1px solid #2d384d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #cbd5e1;
}

QComboBox:hover {
    border: 1px solid #38bdf8;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #18202d;
    border: 1px solid #2d384d;
    color: #cbd5e1;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

/* Tables */
QTableWidget {
    background-color: #141a24;
    alternate-background-color: #18202d;
    border: 1px solid #232c3d;
    border-radius: 6px;
    gridline-color: #222b3b;
    color: #e2e8f0;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #1b2433;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-right: 1px solid #232c3d;
    border-bottom: 1px solid #232c3d;
    font-weight: 600;
    font-family: 'Segoe UI', sans-serif;
}

QTableWidget::item:selected {
    background-color: #0369a1;
    color: #ffffff;
}

/* ListWidget */
QListWidget {
    background-color: #141a24;
    border: 1px solid #232c3d;
    border-radius: 6px;
    color: #e2e8f0;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1c2433;
}

QListWidget::item:selected {
    background-color: #1e3a5f;
    border-left: 3px solid #38bdf8;
    color: #38bdf8;
}

/* Plain Text & Text Browser */
QTextEdit, QPlainTextEdit, QTextBrowser {
    background-color: #141a24;
    border: 1px solid #232c3d;
    border-radius: 6px;
    color: #e2e8f0;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    padding: 10px;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #141a24;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2a3548;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #3b4962;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #141a24;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #2a3548;
    min-width: 20px;
    border-radius: 5px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #232c3d;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0284c7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #38bdf8;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

/* Status Bar */
QStatusBar {
    background-color: #11151e;
    color: #94a3b8;
    border-top: 1px solid #202838;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #232c3d;
    border-radius: 6px;
    margin-top: 18px;
    font-weight: 600;
    color: #38bdf8;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: #141a24;
}
"""

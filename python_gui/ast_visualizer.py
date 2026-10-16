"""
Interactive AST Graph Visualizer with GPU-Accelerated QOpenGLWidget Viewport
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsPathItem, QGraphicsTextItem, QToolTip
)
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath,
    QLinearGradient, QWheelEvent, QMouseEvent
)
from PyQt6.QtCore import Qt, QRectF, QPointF

# Try to use GPU-accelerated OpenGL viewport as per user rule
try:
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False


class AstGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor("#0d1117")))

        # Use GPU acceleration via QOpenGLWidget if available
        if HAS_OPENGL:
            self.setViewport(QOpenGLWidget())

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)


class AstVisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.view = AstGraphicsView(self.scene, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Controls bar
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        title_lbl = QLabel("Abstract Syntax Tree (AST) Visualization")
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #38bdf8;")
        ctrl_layout.addWidget(title_lbl)

        ctrl_layout.addStretch()

        self.btn_zoom_in = QPushButton("Zoom In (+)")
        self.btn_zoom_in.setObjectName("SecondaryBtn")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        ctrl_layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("Zoom Out (-)")
        self.btn_zoom_out.setObjectName("SecondaryBtn")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        ctrl_layout.addWidget(self.btn_zoom_out)

        self.btn_fit = QPushButton("Fit to View")
        self.btn_fit.setObjectName("SecondaryBtn")
        self.btn_fit.clicked.connect(self.fit_to_view)
        ctrl_layout.addWidget(self.btn_fit)

        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.setObjectName("SecondaryBtn")
        self.btn_reset.clicked.connect(self.reset_view)
        ctrl_layout.addWidget(self.btn_reset)

        layout.addLayout(ctrl_layout)
        layout.addWidget(self.view)

        # Bottom info card
        self.info_lbl = QLabel("Compile an arithmetic expression to render the interactive AST.")
        self.info_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 4px;")
        layout.addWidget(self.info_lbl)

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(0.8, 0.8)

    def fit_to_view(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def reset_view(self):
        self.view.resetTransform()
        self.fit_to_view()

    def render_ast(self, ast_dict: dict, node_count: int = 0, tree_depth: int = 0):
        self.scene.clear()
        if not ast_dict:
            self.info_lbl.setText("No AST available.")
            return

        self.info_lbl.setText(f"AST Generated: {node_count} nodes | Tree Depth: {tree_depth} levels | Use mouse scroll to Zoom, drag canvas to Pan.")

        # Draw edges first, then nodes
        self._draw_edges(ast_dict)
        self._draw_nodes(ast_dict)

        # Set scene rect with some padding
        items_rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(items_rect.adjusted(-60, -40, 60, 40))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _draw_edges(self, node: dict):
        x1 = node.get("x", 0.0)
        y1 = node.get("y", 0.0)

        for child in node.get("children", []):
            x2 = child.get("x", 0.0)
            y2 = child.get("y", 0.0)

            path = QPainterPath()
            path.moveTo(x1, y1 + 22)

            # Curved cubic bezier edge connecting parent bottom to child top
            control_y1 = y1 + 55
            control_y2 = y2 - 25
            path.cubicTo(x1, control_y1, x2, control_y2, x2, y2 - 22)

            edge_item = QGraphicsPathItem(path)
            edge_pen = QPen(QColor("#334155"), 2.2)
            edge_item.setPen(edge_pen)
            edge_item.setZValue(1)
            self.scene.addItem(edge_item)

            self._draw_edges(child)

    def _draw_nodes(self, node: dict):
        x = node.get("x", 0.0)
        y = node.get("y", 0.0)
        node_type = node.get("node_type", "Unknown")
        label = node.get("label", "")
        node_id = node.get("id", 0)
        span = node.get("span", [0, 0])

        # Width and height of node capsule
        width = max(90.0, len(label) * 11.0 + 30.0)
        height = 42.0

        rect = QRectF(x - width / 2.0, y - height / 2.0, width, height)

        # Node container item
        node_item = QGraphicsRectItem(rect)
        node_item.setZValue(2)

        # Clean node box with subtle border and colored text
        bg_brush = QBrush(QColor("#131822"))
        if node_type == "Number":
            border_pen = QPen(QColor("#1e293b"), 1.2)
            text_color = "#34d399"
        elif node_type == "UnaryOp":
            border_pen = QPen(QColor("#1e293b"), 1.2)
            text_color = "#fbbf24"
        else:
            border_pen = QPen(QColor("#1e293b"), 1.2)
            text_color = "#38bdf8"

        node_item.setBrush(bg_brush)
        node_item.setPen(border_pen)

        # Tooltip for inspection
        val_str = f"\nValue: {node.get('value')}" if node.get("value") is not None else ""
        tooltip = (
            f"Node ID: {node_id}\n"
            f"Type: {node_type}\n"
            f"Label: {label}{val_str}\n"
            f"Span: [{span[0]}..{span[1]}]\n"
            f"Depth: {node.get('depth', 0)}"
        )
        node_item.setToolTip(tooltip)
        self.scene.addItem(node_item)

        # Label text
        text_item = QGraphicsTextItem(label, node_item)
        font = QFont("Cascadia Code", 11, QFont.Weight.Bold)
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor(text_color))

        # Center text inside node capsule
        text_rect = text_item.boundingRect()
        text_item.setPos(
            x - text_rect.width() / 2.0,
            y - text_rect.height() / 2.0
        )

        for child in node.get("children", []):
            self._draw_nodes(child)

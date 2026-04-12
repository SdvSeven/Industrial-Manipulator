import os

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPen, QPixmap,
)
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class Dashboard(QWidget):
    """
    Central content area — main dashboard screen.
    Inner container: 720×480 px, centered both axes.

    Vertical stack inside container:
        Logo       max 320×180 px, aspect-ratio preserved  ← 32 px gap
        Title      20 px / weight 600                      ← 24 px gap
        Button     280×56 px, border-radius 10             ← 16 px gap
        Status     14 px
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")

        # ── Outer layout: centres the fixed-size container ────
        outer_v = QVBoxLayout(self)
        outer_v.setContentsMargins(0, 0, 0, 0)
        outer_v.setSpacing(0)
        outer_v.addStretch(1)

        outer_h = QHBoxLayout()
        outer_h.setContentsMargins(0, 0, 0, 0)
        outer_h.setSpacing(0)
        outer_h.addStretch(1)

        container = QWidget()
        container.setObjectName("dashboardContainer")
        container.setFixedSize(720, 480)
        self._build_container(container)

        outer_h.addWidget(container)
        outer_h.addStretch(1)

        outer_v.addLayout(outer_h)
        outer_v.addStretch(1)

    # ──────────────────────────────────────────────────────────
    def _build_container(self, container: QWidget) -> None:
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Push content to vertical centre inside the 720×480 box
        layout.addStretch(1)

        # ── Logo ──────────────────────────────────────────────
        logo_label = QLabel()
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = self._load_logo()
        logo_label.setPixmap(pixmap)
        logo_label.setFixedSize(pixmap.size())

        layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(32)   # logo → title gap

        # ── Title ─────────────────────────────────────────────
        title = QLabel("Индустриальный Манипулятор")
        title.setObjectName("dashboardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(24)   # title margin-bottom

        # ── Connect button ────────────────────────────────────
        layout.addSpacing(16)   # button margin-top
        btn = QPushButton("ПОДКЛЮЧИТЬСЯ")
        btn.setObjectName("buttonPrimary")
        btn.setFixedSize(280, 56)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)

        # ── Status indicator ──────────────────────────────────
        layout.addSpacing(16)   # status margin-top
        status = QLabel("● НЕ ПОДКЛЮЧЕНО")
        status.setObjectName("statusLabel")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)

    # ──────────────────────────────────────────────────────────
    def _load_logo(self) -> QPixmap:
        """Return scaled logo pixmap, falling back to a drawn placeholder."""
        assets_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "assets"
        )
        for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.svg"):
            path = os.path.join(assets_dir, name)
            if os.path.exists(path):
                pm = QPixmap(path)
                if not pm.isNull():
                    return pm.scaled(
                        320, 180,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
        return self._draw_placeholder_logo()

    def _draw_placeholder_logo(self) -> QPixmap:
        """Draw a minimal industrial-arm silhouette as a 320×160 pixmap."""
        W, H = 320, 160
        px = QPixmap(W, H)
        px.fill(Qt.GlobalColor.transparent)

        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Card background
        p.setBrush(QBrush(QColor("#1e293b")))
        p.setPen(QPen(QColor("#334155"), 1))
        p.drawRoundedRect(0, 0, W, H, 8, 8)

        # ── Robot-arm silhouette ───────────────────────────────
        arm_pen = QPen(
            QColor("#2563eb"), 5,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        p.setPen(arm_pen)

        # Joint coordinates: base → elbow → wrist → tip
        pts = [(160, 128), (118, 78), (182, 40), (208, 26)]
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            p.drawLine(x1, y1, x2, y2)

        # Base platform
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#2563eb")))
        p.drawRoundedRect(132, 128, 56, 12, 3, 3)

        # Joints (inner dark circle + outer accent ring)
        for x, y in pts[1:-1]:
            p.setBrush(QBrush(QColor("#0f172a")))
            p.setPen(QPen(QColor("#2563eb"), 2))
            p.drawEllipse(x - 9, y - 9, 18, 18)
            p.setBrush(QBrush(QColor("#2563eb")))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x - 4, y - 4, 8, 8)

        # End-effector (gripper fork)
        grip_pen = QPen(
            QColor("#2563eb"), 3,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
        )
        p.setPen(grip_pen)
        wx, wy = pts[-1]
        p.drawLine(wx, wy, wx + 20, wy - 12)
        p.drawLine(wx, wy, wx + 20, wy + 12)

        # Caption
        font = QFont("Segoe UI", 8)
        font.setWeight(QFont.Weight.Medium)
        p.setFont(font)
        p.setPen(QColor("#475569"))
        p.drawText(QRect(0, 4, W, 18), Qt.AlignmentFlag.AlignCenter,
                   "INDUSTRIAL MANIPULATOR SYSTEM")

        p.end()
        return px

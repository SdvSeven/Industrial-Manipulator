"""
Design tokens — glassmorphism, iOS-grade.

Palette
-------
Accent:      #6366F1 → #8B5CF6   (indigo → violet)
Glass fill:  rgba(255,255,255, 0.55)
Border:      rgba(255,255,255, 0.55)
Text:        #0F172A (primary), #64748B (muted), #94A3B8 (hint)
Danger:      #EF4444
"""

APP_STYLE = """

/* ─────────── Base ─────────── */
QWidget {
    background: transparent;
    color: #0F172A;
    font-family: "SF Pro Display", "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 14px;
    font-weight: 400;
}
QMainWindow, QDialog { background: transparent; }


/* ─────────── Glass surfaces ─────────── */
QFrame#glass {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   rgba(255, 255, 255, 0.62),
        stop:0.5 rgba(255, 255, 255, 0.48),
        stop:1   rgba(255, 255, 255, 0.30)
    );
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 22px;
}
QFrame#glassCard {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   rgba(255, 255, 255, 0.68),
        stop:0.5 rgba(255, 255, 255, 0.50),
        stop:1   rgba(255, 255, 255, 0.32)
    );
    border: 1px solid rgba(255, 255, 255, 0.60);
    border-radius: 28px;
}
QFrame#glassSidebar {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.66),
        stop:1 rgba(255, 255, 255, 0.38)
    );
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 24px;
}
QFrame#glassDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   rgba(255, 255, 255, 0.80),
        stop:0.5 rgba(255, 255, 255, 0.64),
        stop:1   rgba(255, 255, 255, 0.50)
    );
    border: 1px solid rgba(255, 255, 255, 0.72);
    border-radius: 28px;
}


/* ─────────── Burger (round icon) ─────────── */
QPushButton#burger {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.75),
        stop:1 rgba(255,255,255,0.40)
    );
    border: 1px solid rgba(255,255,255,0.70);
    border-radius: 22px;
    color: #1E293B;
    font-size: 18px;
    font-weight: 500;
}
QPushButton#burger:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.92),
        stop:1 rgba(255,255,255,0.60)
    );
    border-color: rgba(255,255,255,0.90);
}
QPushButton#burger:pressed { background: rgba(255,255,255,0.55); }


/* ─────────── Ghost button ─────────── */
QPushButton#ghost {
    background: rgba(255,255,255,0.45);
    color: #1E293B;
    border: 1px solid rgba(255,255,255,0.60);
    border-radius: 14px;
    min-height: 42px;
    padding: 0 22px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#ghost:hover {
    background: rgba(255,255,255,0.72);
    border-color: rgba(255,255,255,0.85);
    color: #0F172A;
}
QPushButton#ghost:pressed { background: rgba(255,255,255,0.35); }


/* ─────────── Primary button ─────────── */
QPushButton#primary {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #8B5CF6
    );
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    min-height: 42px;
    padding: 0 24px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.2px;
}
QPushButton#primary:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #7C7FF4, stop:1 #A78BFA
    );
}
QPushButton#primary:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #4F46E5, stop:1 #7C3AED
    );
}


/* ─────────── Connect button (hero) ─────────── */
QPushButton#connect {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #8B5CF6
    );
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    min-height: 56px;
    padding: 0 36px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
QPushButton#connect:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #7C7FF4, stop:1 #A78BFA
    );
}
QPushButton#connect:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #4F46E5, stop:1 #7C3AED
    );
}


/* ─────────── Sidebar menu items ─────────── */
QPushButton#menuItem {
    background: transparent;
    color: #334155;
    border: none;
    border-radius: 14px;
    text-align: left;
    padding: 0 18px;
    min-height: 48px;
    font-size: 15px;
    font-weight: 500;
}
QPushButton#menuItem:hover {
    background: rgba(255,255,255,0.55);
    color: #6366F1;
}
QPushButton#menuItem:pressed { background: rgba(255,255,255,0.75); }


/* ─────────── User chip ─────────── */
QLabel#userChip {
    background: rgba(255,255,255,0.50);
    border: 1px solid rgba(255,255,255,0.65);
    border-radius: 14px;
    padding: 0 16px;
    min-height: 42px;
    font-size: 14px;
    font-weight: 600;
    color: #0F172A;
}


/* ─────────── Logo badge ─────────── */
QLabel#logoBadge {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,0.85),
        stop:1 rgba(255,255,255,0.45)
    );
    border: 1px solid rgba(255,255,255,0.80);
    border-radius: 60px;
    color: #6366F1;
    font-size: 52px;
    font-weight: 300;
}


/* ─────────── Typography ─────────── */
QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.3px;
}
QLabel#subtitle {
    font-size: 14px;
    font-weight: 400;
    color: #64748B;
}
QLabel#stubTitle {
    font-size: 32px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.5px;
}
QLabel#stubHint {
    font-size: 15px;
    font-weight: 400;
    color: #64748B;
}
QLabel#fieldLabel {
    font-size: 11px;
    font-weight: 700;
    color: #94A3B8;
    letter-spacing: 1.2px;
}
QLabel#errorMsg {
    font-size: 13px;
    font-weight: 500;
    color: #B91C1C;
    background: rgba(239, 68, 68, 0.10);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 12px;
    padding: 10px 14px;
}
QLabel#toast {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.30);
    border-radius: 12px;
    padding: 8px 16px;
    color: #B91C1C;
    font-size: 13px;
    font-weight: 600;
}
QLabel#dialogBody {
    font-size: 14px;
    font-weight: 400;
    color: #475569;
    line-height: 1.6;
}


/* ─────────── Inputs ─────────── */
QLineEdit {
    background: rgba(255,255,255,0.72);
    border: 1.5px solid rgba(255,255,255,0.70);
    border-radius: 12px;
    min-height: 44px;
    padding: 0 16px;
    font-size: 14px;
    color: #0F172A;
    selection-background-color: rgba(99, 102, 241, 0.25);
}
QLineEdit:focus {
    border-color: rgba(99, 102, 241, 0.65);
    background: rgba(255,255,255,0.92);
}
QLineEdit:hover:!focus { border-color: rgba(255,255,255,0.90); }


/* ─────────── Checkbox ─────────── */
QCheckBox { spacing: 10px; color: #334155; font-size: 13px; }
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1.5px solid rgba(148, 163, 184, 0.75);
    background: rgba(255,255,255,0.85);
}
QCheckBox::indicator:hover { border-color: rgba(99, 102, 241, 0.65); }
QCheckBox::indicator:checked {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366F1, stop:1 #8B5CF6
    );
    border-color: #6366F1;
}


/* ─────────── Scrollbar ─────────── */
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
QScrollBar::handle:vertical {
    background: rgba(148, 163, 184, 0.45);
    border-radius: 3px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover { background: rgba(99, 102, 241, 0.55); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
"""

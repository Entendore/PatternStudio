#!/usr/bin/env python3
"""
PatternLearn - Sewing Pattern Learning App
A comprehensive application for learning sewing patterns interactively.
Built with PySide6
"""

import sys
import os
import json
import math
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QStackedWidget,
    QScrollArea, QListWidget, QListWidgetItem, QComboBox,
    QDoubleSpinBox, QFormLayout, QProgressBar, QLineEdit,
    QSizePolicy, QSpacerItem, QTabWidget, QGroupBox, QCheckBox,
    QMessageBox, QTextEdit, QFileDialog, QInputDialog, QSplitter
)
from PySide6.QtCore import (
    Qt, Signal, QPointF, QRectF, QSize, QSettings, QStandardPaths
)
from PySide6.QtGui import (
    QPainter, QPen, QColor, QFont, QPainterPath,
    QLinearGradient, QPainterPathStroker, QBrush, QPalette,
    QFontMetrics, QAction
)
from PySide6.QtPrintSupport import QPrinter

# ======================== COLOR PALETTE ========================
LIGHT_PALETTE = {
    'primary': '#AD1457', 'primary_light': '#F48FB1', 'primary_dark': '#880E4F',
    'secondary': '#E65100', 'secondary_light': '#FFB74D',
    'accent': '#6A1B9A', 'accent_light': '#CE93D8',
    'bg': '#FFF8E1', 'bg_dark': '#F5E6C8', 'bg_darker': '#EED9B6',
    'card': '#FFFFFF', 'card_hover': '#FFF3E0',
    'text': '#333333', 'text_light': '#757575', 'text_inverse': '#FFFFFF',
    'success': '#2E7D32', 'success_light': '#C8E6C9',
    'info': '#1565C0', 'info_light': '#BBDEFB',
    'border': '#E0E0E0', 'border_dark': '#BDBDBD',
    'warning': '#F57F17', 'warning_light': '#FFF9C4',
    'danger': '#C62828',
    'sidebar': '#3E2723', 'sidebar_text': '#EFEBE9', 'sidebar_hover': '#5D4037',
    'sidebar_active': '#AD1457',
}

DARK_PALETTE = {
    'primary': '#F48FB1', 'primary_light': '#F8BBD0', 'primary_dark': '#EC407A',
    'secondary': '#FFB74D', 'secondary_light': '#FFCC80',
    'accent': '#CE93D8', 'accent_light': '#E1BEE7',
    'bg': '#1A1A2E', 'bg_dark': '#16213E', 'bg_darker': '#0F3460',
    'card': '#222244', 'card_hover': '#2A2A4A',
    'text': '#E0E0E0', 'text_light': '#A0A0A0', 'text_inverse': '#1A1A2E',
    'success': '#66BB6A', 'success_light': '#2E4A2E',
    'info': '#42A5F5', 'info_light': '#1A3A5A',
    'border': '#3A3A5A', 'border_dark': '#4A4A6A',
    'warning': '#FFD54F', 'warning_light': '#3A3A1A',
    'danger': '#EF5350',
    'sidebar': '#0F0F1A', 'sidebar_text': '#E0E0E0', 'sidebar_hover': '#1A1A2E',
    'sidebar_active': '#F48FB1',
}

PIECE_COLORS = ['#E91E63', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#FF5722', '#8BC34A']
DIFFICULTY_COLORS = {'Beginner': '#4CAF50', 'Intermediate': '#FF9800', 'Advanced': '#F44336'}
CATEGORY_ICONS = {'Bottoms': '👖', 'Accessories': '👜', 'Tops': '👕', 'Dresses': '👗'}

# ======================== DATA MODELS ========================
class PatternPiece:
    def __init__(self, name, color, path, description, grain_line=None, notches=None):
        self.name = name
        self.color = color
        self.path = path
        self.description = description
        self.grain_line = grain_line
        self.notches = notches or []

class SewingPattern:
    def __init__(self, name, category, difficulty, description, pieces, steps, materials, tips=None, estimated_time=""):
        self.name = name
        self.category = category
        self.difficulty = difficulty
        self.description = description
        self.pieces = pieces
        self.steps = steps
        self.materials = materials
        self.tips = tips or []
        self.estimated_time = estimated_time

# ======================== PATTERN DEFINITIONS ========================
def create_aline_skirt():
    pieces = []
    front_path = QPainterPath()
    front_path.moveTo(80, 30); front_path.lineTo(220, 30); front_path.quadTo(240, 30, 245, 50)
    front_path.lineTo(270, 280); front_path.quadTo(275, 300, 260, 305); front_path.lineTo(30, 305)
    front_path.quadTo(15, 300, 25, 280); front_path.lineTo(55, 50); front_path.quadTo(60, 30, 80, 30)
    front_path.closeSubpath()
    pieces.append(PatternPiece("Front Panel", PIECE_COLORS[0], front_path, "Main front piece. Cut 1 on fold.", (QPointF(150, 35), QPointF(150, 295)), [QPointF(150, 30)]))
    
    back_path = QPainterPath()
    back_path.moveTo(330, 30); back_path.lineTo(470, 30); back_path.quadTo(490, 30, 495, 50)
    back_path.lineTo(520, 280); back_path.quadTo(525, 300, 510, 305); back_path.lineTo(290, 305)
    back_path.quadTo(275, 300, 285, 280); back_path.lineTo(305, 50); back_path.quadTo(310, 30, 330, 30)
    back_path.closeSubpath()
    pieces.append(PatternPiece("Back Panel", PIECE_COLORS[1], back_path, "Back piece. Cut 2.", (QPointF(400, 35), QPointF(400, 295))))
    
    waist_path = QPainterPath(); waist_path.addRoundedRect(QRectF(80, 340, 390, 40), 5, 5)
    pieces.append(PatternPiece("Waistband", PIECE_COLORS[2], waist_path, "Waistband. Cut 1 on fold.", (QPointF(100, 360), QPointF(450, 360))))
    
    steps = [
        {"title": "Prepare Fabric", "description": "Pre-wash and iron fabric. Lay flat folded selvage to selvage.", "tip": "Pre-washing prevents later shrinkage!"},
        {"title": "Cut Pieces", "description": "Pin and cut front on fold, two back panels, and waistband.", "tip": "Use pattern weights for cleaner cuts."},
        {"title": "Mark Darts", "description": "Transfer dart markings using tailor's chalk.", "tip": "Clip notches rather than cutting outward triangles."},
        {"title": "Sew Darts", "description": "Fold and sew darts. Press toward center.", "tip": "Sew from wide end to point."},
        {"title": "Sew Back Seam", "description": "Sew center back, leaving top 7\" open for zipper.", "tip": "Baste the zipper opening first."},
        {"title": "Insert Zipper", "description": "Install invisible zipper in center back.", "tip": "Use an invisible zipper foot."},
        {"title": "Sew Side Seams", "description": "Sew side seams right sides together.", "tip": "Try on before finishing seams."},
        {"title": "Attach Waistband", "description": "Sew waistband, fold over, stitch in ditch.", "tip": "Interface waistband for stability."},
        {"title": "Hem", "description": "Turn up hem 1/4\" then 1\" and stitch.", "tip": "Blind hem stitch gives invisible finish."},
        {"title": "Final Press", "description": "Press completed skirt thoroughly.", "tip": "Press each seam as you go for best results."},
    ]
    materials = [{"name": "Cotton/Linen Fabric", "amount": "1.5 yards", "note": "45\" wide"}, {"name": "Invisible Zipper", "amount": "7 inches", "note": "Matching"}, {"name": "Interfacing", "amount": "0.25 yards", "note": "Fusible"}, {"name": "Thread", "amount": "1 spool", "note": "Matching"}]
    return SewingPattern("A-Line Skirt", "Bottoms", "Beginner", "Classic A-line skirt with darts and zipper.", pieces, steps, materials, estimated_time="4-6 hours")

def create_tote_bag():
    pieces = []
    body_path = QPainterPath(); body_path.addRoundedRect(QRectF(40, 30, 200, 250), 8, 8)
    pieces.append(PatternPiece("Main Body", PIECE_COLORS[3], body_path, "Body panel. Cut 2.", (QPointF(60, 155), QPointF(220, 155))))
    bottom_path = QPainterPath(); bottom_path.addRoundedRect(QRectF(280, 30, 150, 60), 5, 5)
    pieces.append(PatternPiece("Bottom", PIECE_COLORS[4], bottom_path, "Bottom panel. Cut 2.", (QPointF(300, 60), QPointF(410, 60))))
    strap_path = QPainterPath(); strap_path.addRoundedRect(QRectF(40, 310, 50, 150), 10, 10)
    pieces.append(PatternPiece("Strap", PIECE_COLORS[5], strap_path, "Straps. Cut 4.", (QPointF(65, 320), QPointF(65, 450))))
    pocket_path = QPainterPath(); pocket_path.addRoundedRect(QRectF(280, 130, 150, 120), 5, 5)
    pieces.append(PatternPiece("Pocket", PIECE_COLORS[7], pocket_path, "Interior pocket. Cut 1.", (QPointF(300, 190), QPointF(410, 190))))
    
    steps = [
        {"title": "Cut Pieces", "description": "Cut all pieces from outer and lining fabric.", "tip": "Rotary cutter gives cleanest edges."},
        {"title": "Make Straps", "description": "Fold straps, sew, turn, topstitch.", "tip": "Safety pin helps turn straps."},
        {"title": "Sew Pocket", "description": "Hem top, stitch to lining panel.", "tip": "Reinforce top corners."},
        {"title": "Assemble Outer", "description": "Sew outer body, attach bottom.", "tip": "Clip corners before turning."},
        {"title": "Assemble Lining", "description": "Sew lining, leave 4\" gap in side.", "tip": "Gap is for turning later."},
        {"title": "Attach Straps", "description": "Baste straps to outer bag top.", "tip": "Ensure straps aren't twisted."},
        {"title": "Join Layers", "description": "Sew lining to outer at top edge.", "tip": "Go slow around straps."},
        {"title": "Finish", "description": "Turn, stitch gap closed, topstitch.", "tip": "Press well for pro finish!"},
    ]
    materials = [{"name": "Canvas Fabric", "amount": "0.75 yards", "note": "Outer"}, {"name": "Cotton Fabric", "amount": "0.75 yards", "note": "Lining"}, {"name": "Thread", "amount": "1 spool", "note": "Heavy-duty"}]
    return SewingPattern("Tote Bag", "Accessories", "Beginner", "Sturdy everyday tote with pockets.", pieces, steps, materials, estimated_time="2-3 hours")

def get_all_patterns():
    return [create_aline_skirt(), create_tote_bag()]

GLOSSARY = [
    ("Armhole", "Opening where sleeve attaches."), ("Backstitch", "Securing seam start/end by sewing backwards."),
    ("Baste", "Temporary stitching to hold pieces."), ("Bias", "Diagonal 45° grain with most stretch."),
    ("Dart", "Folded/stitched wedge for shaping."), ("Grain Line", "Arrow aligning piece to lengthwise grain."),
    ("Interfacing", "Fabric added between shell and facing for body."), ("Notch", "Mark for matching pieces."),
    ("Seam Allowance", "Area between stitch line and raw edge. Standard 5/8\"."), ("Selvage", "Finished fabric edges."),
    ("Stay Stitch", "Stitching within SA to prevent stretching curves."), ("Topstitch", "Stitching visible on outside."),
    ("Understitch", "Stitching facing to SA to prevent rolling."), ("Yoke", "Fitted panel at shoulders/waist for support."),
]

# ======================== STITCH LIBRARY DATA ========================
STITCHES = [
    {"name": "Running Stitch", "uses": "Basic gathering, basting, mending seams.", "type": "hand",
     "draw": "running"},
    {"name": "Backstitch", "uses": "Strong hand-sewn seams, replacing machine stitching.", "type": "hand",
     "draw": "back"},
    {"name": "Basting Stitch", "uses": "Temporary holding stitch, long and easily removable.", "type": "hand",
     "draw": "basting"},
    {"name": "Whipstitch", "uses": "Hemming, closing openings, attaching appliqués.", "type": "hand",
     "draw": "whip"},
    {"name": "Straight Stitch", "uses": "Standard machine stitching for seams and topstitching.", "type": "machine",
     "draw": "straight"},
    {"name": "Zigzag Stitch", "uses": "Finishing raw edges, sewing stretch fabrics.", "type": "machine",
     "draw": "zigzag"},
    {"name": "Overlock / Serging", "uses": "Professional edge finishing, stretch seam construction.", "type": "machine",
     "draw": "overlock"},
    {"name": "Blind Hem", "uses": "Invisible hems on pants and skirts.", "type": "machine",
     "draw": "blind_hem"},
]

# ======================== CUSTOM WIDGETS ========================
class PatternCanvas(QWidget):
    piece_clicked = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = []
        self.hovered_piece = -1
        self.selected_piece = -1
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._dragging = False
        self._last_mouse = None
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.show_labels = True
        self.show_grain_lines = True
        self.show_notches = True
        self.seam_allowance = 0.0
        self._dark_mode = False

    def set_dark_mode(self, d): self._dark_mode = d; self.update()
    def set_pieces(self, p): self.pieces = p; self.hovered_piece = -1; self.selected_piece = -1; self._fit_view()

    def _fit_view(self):
        if not self.pieces: return
        bounds = QRectF()
        for p in self.pieces: bounds = bounds.united(p.path.boundingRect())
        if bounds.isEmpty(): return
        m = 40; w = self.width() - 2*m; h = self.height() - 2*m
        if w <= 0 or h <= 0: return
        self.scale = min(w / bounds.width(), h / bounds.height())
        self.offset_x = m + (w - bounds.width() * self.scale) / 2 - bounds.x() * self.scale
        self.offset_y = m + (h - bounds.height() * self.scale) / 2 - bounds.y() * self.scale

    def resizeEvent(self, e): super().resizeEvent(e); self._fit_view()

    def _scaled_path(self, path):
        m = QPainterPath(path); m.translate(self.offset_x, self.offset_y); return m

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            for i, p in enumerate(self.pieces):
                if self._scaled_path(p.path).contains(e.position()):
                    self.selected_piece = i if self.selected_piece != i else -1; self.piece_clicked.emit(i); self.update(); return
            self.selected_piece = -1; self.update()
        elif e.button() == Qt.RightButton: self._dragging = True; self._last_mouse = e.position()

    def mouseMoveEvent(self, e):
        if self._dragging and self._last_mouse:
            self.offset_x += e.position().x() - self._last_mouse.x(); self.offset_y += e.position().y() - self._last_mouse.y()
            self._last_mouse = e.position(); self.update()
        else:
            old = self.hovered_piece; self.hovered_piece = -1
            for i, p in enumerate(self.pieces):
                if self._scaled_path(p.path).contains(e.position()): self.hovered_piece = i; break
            if old != self.hovered_piece: self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton: self._dragging = False; self._last_mouse = None

    def wheelEvent(self, e):
        f = 1.1 if e.angleDelta().y() > 0 else 0.9; os = self.scale
        self.scale = max(0.2, min(5.0, self.scale * f)); r = self.scale / os
        mx, my = e.position().x(), e.position().y()
        self.offset_x = mx - (mx - self.offset_x) * r; self.offset_y = my - (my - self.offset_y) * r; self.update()

    def paintEvent(self, e):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        c = '#1A1A2E' if self._dark_mode else '#FFF8E1'; gc = QColor('#2A2A4A') if self._dark_mode else QColor('#E8DCC8'); tc = QColor('#E0E0E0') if self._dark_mode else QColor('#333333')
        painter.fillRect(self.rect(), QColor(c))
        painter.setPen(QPen(gc, 0.5, Qt.DotLine)); s = 30 * self.scale
        if s > 5:
            x = self.offset_x % s
            while x < self.width(): painter.drawLine(int(x), 0, int(x), self.height()); x += s
            y = self.offset_y % s
            while y < self.height(): painter.drawLine(0, int(y), self.width(), int(y)); y += s
        
        for i, piece in enumerate(self.pieces):
            is_sel = (i == self.selected_piece); is_hov = (i == self.hovered_piece)
            dim = (self.selected_piece >= 0 and not is_sel and not is_hov)
            mapped = self._scaled_path(piece.path)
            fc = QColor(piece.color)
            fc.setAlpha(40 if dim else (160 if is_hov else (180 if is_sel else 120)))
            sc = QColor(piece.color); sc.setAlpha(60 if dim else 255)
            painter.setPen(QPen(sc, 2.5 if (is_sel or is_hov) else 1.5)); painter.setBrush(fc); painter.drawPath(mapped)
            if self.show_grain_lines and piece.grain_line and not dim:
                g = piece.grain_line
                p1 = QPointF(g[0].x()*self.scale+self.offset_x, g[0].y()*self.scale+self.offset_y)
                p2 = QPointF(g[1].x()*self.scale+self.offset_x, g[1].y()*self.scale+self.offset_y)
                painter.setPen(QPen(tc, 1, Qt.DashLine)); painter.drawLine(p1, p2)
            if self.show_labels and not dim:
                painter.setFont(QFont('Segoe UI', 9, QFont.Bold)); painter.setPen(tc)
                painter.drawText(mapped.boundingRect(), Qt.AlignCenter, piece.name)
        if not self.pieces:
            painter.setPen(tc); painter.setFont(QFont('Segoe UI', 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "Select a pattern to view")
        painter.end()


class StitchCanvas(QWidget):
    """Draws vector illustrations of stitches."""
    def __init__(self, stitch_type, parent=None):
        super().__init__(parent)
        self.stitch_type = stitch_type
        self.setFixedSize(200, 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        
        pen = QPen(QColor("#333333"), 2.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        y_center = 40
        x_start = 20
        x_end = 180
        
        if self.stitch_type == "running":
            pen.setStyle(Qt.DashLine); pen.setDashPattern([4, 4]); painter.setPen(pen)
            painter.drawLine(x_start, y_center, x_end, y_center)
        elif self.stitch_type == "back":
            pen.setStyle(Qt.DashLine); pen.setDashPattern([6, 3]); painter.setPen(pen)
            painter.drawLine(x_start, y_center, x_end, y_center)
            # Draw overlaps
            pen2 = QPen(QColor("#E91E63"), 2.5, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen2)
            x = x_start
            while x < x_end - 10:
                painter.drawLine(x, y_center, x + 6, y_center)
                x += 9
        elif self.stitch_type == "basting":
            pen.setStyle(Qt.DashLine); pen.setDashPattern([10, 6]); painter.setPen(pen)
            painter.drawLine(x_start, y_center, x_end, y_center)
        elif self.stitch_type == "whip":
            x = x_start
            while x < x_end:
                painter.drawEllipse(QPointF(x, y_center - 5), 4, 8)
                x += 10
        elif self.stitch_type == "straight":
            painter.drawLine(x_start, y_center, x_end, y_center)
        elif self.stitch_type == "zigzag":
            path = QPainterPath(); path.moveTo(x_start, y_center)
            x = x_start + 10
            toggle = True
            while x < x_end:
                path.lineTo(x, y_center - 15 if toggle else y_center + 15)
                x += 10; toggle = not toggle
            path.lineTo(x_end, y_center)
            painter.drawPath(path)
        elif self.stitch_type == "overlock":
            # Zigzag + edge loop
            path = QPainterPath(); path.moveTo(x_start, y_center)
            x = x_start + 10; toggle = True
            while x < x_end:
                path.lineTo(x, y_center - 15 if toggle else y_center + 15)
                x += 10; toggle = not toggle
            path.lineTo(x_end, y_center)
            painter.drawPath(path)
            # Edge thread
            pen2 = QPen(QColor("#2196F3"), 2, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen2)
            painter.drawLine(x_start, y_center + 15, x_end, y_center + 15)
            # Loops
            pen3 = QPen(QColor("#2196F3"), 1.5, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen3)
            x_loop = x_start + 10
            while x_loop < x_end:
                painter.drawArc(int(x_loop - 5), int(y_center + 10), 10, 20, 0, -180 * 16)
                x_loop += 20
        elif self.stitch_type == "blind_hem":
            # Main fabric line
            pen2 = QPen(QColor("#BDBDBD"), 1, Qt.SolidLine)
            painter.setPen(pen2)
            painter.drawLine(x_start, y_center + 10, x_end, y_center + 10)
            # Stitches
            pen3 = QPen(QColor("#333333"), 2.5, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen3)
            x = x_start
            while x < x_end:
                painter.drawLine(x, y_center + 10, x + 2, y_center - 10)
                x += 15
        painter.end()


class NavButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent); self.icon_text = icon_text; self.text_label = text; self._active = False; self._hovered = False
        self.setCheckable(True); self.setCursor(Qt.PointingHandCursor); self.setFixedHeight(44); self.setMinimumWidth(200)
    @property
    def active(self): return self._active
    @active.setter
    def active(self, v): self._active = v; self.setChecked(v); self.update()
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); c = self.window()._get_colors()
        p.fillRect(self.rect(), QColor(c['sidebar_active'] if self._active else (c['sidebar_hover'] if self._hovered else c['sidebar'])))
        f = QFont('Segoe UI', 11);
        if self._active: f.setBold(True)
        x = 16
        if self.icon_text:
            p.setFont(QFont('Segoe UI', 14)); p.setPen(QColor(c['sidebar_text'])); p.drawText(QRectF(x, 0, 30, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self.icon_text); x += 30
        p.setFont(f); p.setPen(QColor(c['sidebar_text'])); p.drawText(QRectF(x, 0, self.width()-x-10, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self.text_label); p.end()
    def enterEvent(self, e): self._hovered = True; self.update()
    def leaveEvent(self, e): self._hovered = False; self.update()


class PatternCard(QFrame):
    clicked = Signal(object)
    def __init__(self, pattern, index, parent=None):
        super().__init__(parent); self.pattern = pattern; self.index = index; self._hovered = False
        self.setCursor(Qt.PointingHandCursor); self.setFixedHeight(140)
    def enterEvent(self, e): self._hovered = True; self.update()
    def leaveEvent(self, e): self._hovered = False; self.update()
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit(self.pattern)
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); c = self.window()._get_colors()
        if self._hovered:
            p.setPen(Qt.NoPen); p.setBrush(QColor(0,0,0,30)); p.drawRoundedRect(self.rect().adjusted(3,3,3,3), 10, 10)
        bg = c['card_hover'] if self._hovered else c['card']
        p.setPen(QPen(QColor(c['border']), 1)); p.setBrush(QColor(bg)); p.drawRoundedRect(self.rect().adjusted(0,0,-1,-1), 10, 10)
        accent = DIFFICULTY_COLORS.get(self.pattern.difficulty, '#999')
        p.setPen(Qt.NoPen); p.setBrush(QColor(accent)); p.drawRoundedRect(QRectF(0,0,6,self.height()), 3, 3)
        y = 16; p.setFont(QFont('Segoe UI', 13)); p.setPen(QColor(c['text'])); p.drawText(QRectF(20,y,30,24), Qt.AlignLeft, CATEGORY_ICONS.get(self.pattern.category, '📐'))
        p.setFont(QFont('Segoe UI', 10)); p.setPen(QColor(c['text_light'])); p.drawText(QRectF(45,y,200,24), Qt.AlignLeft, self.pattern.category)
        df = QFont('Segoe UI', 8, QFont.Bold); p.setFont(df); tw = QFontMetrics(df).horizontalAdvance(self.pattern.difficulty)+14; dx = self.width()-tw-20
        p.setPen(Qt.NoPen); p.setBrush(QColor(accent)); p.drawRoundedRect(QRectF(dx, y+2, tw, 20), 10, 10); p.setPen(QColor('#FFFFFF')); p.drawText(QRectF(dx, y+2, tw, 20), Qt.AlignCenter, self.pattern.difficulty)
        y += 30; p.setFont(QFont('Segoe UI', 15, QFont.Bold)); p.setPen(QColor(c['text'])); p.drawText(QRectF(20, y, self.width()-40, 28), Qt.AlignLeft, self.pattern.name)
        y += 30; p.setFont(QFont('Segoe UI', 9)); p.setPen(QColor(c['text_light']))
        desc = self.pattern.description
        if len(desc)>80: desc = desc[:77]+"..."
        p.drawText(QRectF(20, y, self.width()-40, 40), Qt.AlignLeft | Qt.TextWordWrap, desc)
        p.end()


# ======================== MAIN WINDOW ========================
class PatternLearnApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧵 PatternLearn — Sewing Pattern Studio")
        self.setMinimumSize(1200, 750); self.resize(1400, 850)
        
        self.patterns = get_all_patterns()
        self.current_pattern = None; self.current_step = 0
        self.completed_steps = {}; self.favorites = set(); self.notes = {}; self.dark_mode = False
        self.fabric_stash = []  # New: [{name, yards, width, fiber, color}]
        
        self.data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), 'PatternLearn')
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_data()
        self._build_ui()
        self._apply_theme()

    def _load_data(self):
        path = os.path.join(self.data_dir, 'userdata.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f: data = json.load(f)
                self.favorites = set(data.get('favorites', [])); self.notes = data.get('notes', {})
                cs = data.get('completed_steps', {}); self.completed_steps = {k: set(v) for k, v in cs.items()}
                self.dark_mode = data.get('dark_mode', False); self.measurements = data.get('measurements', {})
                self.fabric_stash = data.get('fabric_stash', [])
            except Exception: self.measurements = {}
        else: self.measurements = {}

    def _save_data(self):
        data = {'favorites': list(self.favorites), 'notes': self.notes, 'completed_steps': {k: list(v) for k, v in self.completed_steps.items()}, 'dark_mode': self.dark_mode, 'measurements': self.measurements, 'fabric_stash': self.fabric_stash}
        path = os.path.join(self.data_dir, 'userdata.json')
        try:
            with open(path, 'w') as f: json.dump(data, f, indent=2)
        except Exception: pass

    def closeEvent(self, e): self._save_data(); super().closeEvent(e)
    def _get_colors(self): return DARK_PALETTE if self.dark_mode else LIGHT_PALETTE

    # ---- UI BUILDING ----
    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        self._build_sidebar(); main_layout.addWidget(self.sidebar)
        self.page_stack = QStackedWidget()
        self._build_dashboard(); self._build_library(); self._build_detail()
        self._build_calculator(); self._build_glossary(); self._build_measurements_page()
        self._build_progress_page(); self._build_fabric_stash_page(); self._build_stitch_library_page()
        main_layout.addWidget(self.page_stack, 1)
        self.nav_buttons[0].active = True; self.page_stack.setCurrentIndex(0)

    def _build_sidebar(self):
        c = self._get_colors(); self.sidebar = QFrame(); self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(f"QFrame {{ background-color: {c['sidebar']}; border: none; }}")
        layout = QVBoxLayout(self.sidebar); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        logo_frame = QFrame(); logo_frame.setStyleSheet(f"background-color: {c['sidebar']}; border: none;")
        ll = QVBoxLayout(logo_frame); ll.setContentsMargins(16,16,16,8)
        lbl = QLabel("🧵 PatternLearn"); lbl.setStyleSheet(f"color: {c['sidebar_text']}; font-size: 18px; font-weight: bold; border: none;")
        ll.addWidget(lbl); sub = QLabel("Sewing Studio"); sub.setStyleSheet(f"color: {c['sidebar_text']}; font-size: 10px; opacity: 0.7; border: none;"); ll.addWidget(sub)
        layout.addWidget(logo_frame); sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background-color: rgba(255,255,255,0.1); border: none;"); layout.addWidget(sep); layout.addSpacing(8)
        
        nav_items = [("Dashboard", "🏠"), ("Pattern Library", "📚"), ("Pattern Detail", "📐"), ("Fabric Calculator", "🧮"), ("Glossary", "📖"), ("Measurements", "📏"), ("My Progress", "📊"), ("Fabric Stash", "🧶"), ("Stitch Library", "🪡")]
        self.nav_buttons = []
        for t, i in nav_items:
            btn = NavButton(t, i); btn.clicked.connect(lambda checked, idx=len(self.nav_buttons): self._switch_page(idx))
            layout.addWidget(btn); self.nav_buttons.append(btn)
        
        layout.addStretch(); sep2 = QFrame(); sep2.setFixedHeight(1); sep2.setStyleSheet("background-color: rgba(255,255,255,0.1); border: none;"); layout.addWidget(sep2)
        tf = QFrame(); tf.setStyleSheet(f"background-color: {c['sidebar']}; border: none;"); tl = QHBoxLayout(tf); tl.setContentsMargins(16,8,16,16)
        self.theme_btn = QPushButton("🌙 Dark Mode"); self.theme_btn.setCheckable(True); self.theme_btn.setChecked(self.dark_mode); self.theme_btn.setCursor(Qt.PointingHandCursor); self.theme_btn.clicked.connect(self._toggle_theme)
        self.theme_btn.setStyleSheet(f"QPushButton {{ background-color: rgba(255,255,255,0.1); color: {c['sidebar_text']}; border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; padding: 8px 12px; font-size: 11px; }} QPushButton:hover {{ background-color: rgba(255,255,255,0.2); }}")
        tl.addWidget(self.theme_btn); layout.addWidget(tf)

    def _switch_page(self, idx):
        if idx < 0 or idx >= self.page_stack.count(): return
        for i, btn in enumerate(self.nav_buttons): btn.active = (i == idx)
        self.page_stack.setCurrentIndex(idx)

    # --- PAGES ---
    def _build_dashboard(self):
        c = self._get_colors(); page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(30,20,30,20); l.setSpacing(16)
        l.addWidget(QLabel("Welcome to PatternLearn 👋")); l.addWidget(QLabel("Your personal sewing pattern studio."))
        self.page_stack.addWidget(page)

    def _build_library(self):
        c = self._get_colors(); page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(30,20,30,20)
        h = QLabel("Pattern Library 📚"); h.setFont(QFont('Segoe UI', 22, QFont.Bold)); l.addWidget(h)
        self.lib_scroll = QScrollArea(); self.lib_scroll.setWidgetResizable(True)
        self.lib_grid_widget = QWidget(); self.lib_grid_layout = QGridLayout(self.lib_grid_widget); self.lib_grid_layout.setSpacing(16)
        self.lib_scroll.setWidget(self.lib_grid_widget); l.addWidget(self.lib_scroll, 1)
        for i, p in enumerate(self.patterns):
            card = PatternCard(p, i); card.clicked.connect(self._open_pattern_detail); self.lib_grid_layout.addWidget(card, i//2, i%2)
        self.page_stack.addWidget(page)

    def _build_detail(self):
        c = self._get_colors(); self.detail_page = QWidget(); layout = QVBoxLayout(self.detail_page); layout.setContentsMargins(30,20,30,20); layout.setSpacing(12)
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back"); self.back_btn.setCursor(Qt.PointingHandCursor); self.back_btn.clicked.connect(lambda: self._switch_page(1)); top_bar.addWidget(self.back_btn)
        self.detail_title = QLabel(""); self.detail_title.setFont(QFont('Segoe UI', 20, QFont.Bold)); top_bar.addWidget(self.detail_title, 1)
        self.fav_btn = QPushButton("⭐"); self.fav_btn.setCursor(Qt.PointingHandCursor); self.fav_btn.setFixedSize(40,40); self.fav_btn.clicked.connect(self._toggle_favorite); top_bar.addWidget(self.fav_btn)
        
        # PDF EXPORT BUTTON
        self.pdf_btn = QPushButton("🖨️ Export PDF"); self.pdf_btn.setCursor(Qt.PointingHandCursor); self.pdf_btn.clicked.connect(self._export_pdf)
        self.pdf_btn.setStyleSheet(f"QPushButton {{ background-color: {c['info']}; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }} QPushButton:hover {{ background-color: #0D47A1; }}")
        top_bar.addWidget(self.pdf_btn)
        
        layout.addLayout(top_bar)
        
        splitter = QSplitter(Qt.Horizontal)
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)
        
        # Canvas controls
        cc = QHBoxLayout()
        self.sa_spin = QDoubleSpinBox(); self.sa_spin.setRange(0,2); self.sa_spin.setSingleStep(0.125); self.sa_spin.setValue(0); self.sa_spin.setSuffix(" in SA")
        self.sa_spin.valueChanged.connect(lambda v: setattr(self.pattern_canvas, 'seam_allowance', v) or self.pattern_canvas.update()); cc.addWidget(QLabel("SA:")); cc.addWidget(self.sa_spin)
        fit_btn = QPushButton("Fit View"); fit_btn.clicked.connect(lambda: self.pattern_canvas._fit_view() or self.pattern_canvas.update()); cc.addWidget(fit_btn); cc.addStretch()
        ll.addLayout(cc)
        
        self.pattern_canvas = PatternCanvas(); ll.addWidget(self.pattern_canvas, 1)
        self.piece_list = QListWidget(); self.piece_list.setMaximumHeight(120)
        self.piece_list.currentRowChanged.connect(lambda r: setattr(self.pattern_canvas, 'selected_piece', r) or self.pattern_canvas.update())
        ll.addWidget(self.piece_list)
        splitter.addWidget(left)
        
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        self.detail_tabs = QTabWidget()
        
        # Steps Tab
        sw = QWidget(); sl = QVBoxLayout(sw); sl.setContentsMargins(12,12,12,12)
        self.step_progress = QProgressBar(); self.step_progress.setFixedHeight(12); sl.addWidget(self.step_progress)
        nl = QHBoxLayout()
        self.prev_step_btn = QPushButton("◀ Previous"); self.prev_step_btn.clicked.connect(self._prev_step); nl.addWidget(self.prev_step_btn)
        self.step_indicator = QLabel("Step 1/1"); self.step_indicator.setAlignment(Qt.AlignCenter); nl.addWidget(self.step_indicator, 1)
        self.next_step_btn = QPushButton("Next ▶"); self.next_step_btn.clicked.connect(self._next_step); nl.addWidget(self.next_step_btn)
        sl.addLayout(nl)
        self.step_title = QLabel(""); self.step_title.setFont(QFont('Segoe UI', 14, QFont.Bold)); sl.addWidget(self.step_title)
        self.step_desc = QLabel(""); self.step_desc.setWordWrap(True); sl.addWidget(self.step_desc, 1)
        self.step_tip = QLabel(""); self.step_tip.setWordWrap(True); sl.addWidget(self.step_tip)
        self.complete_step_btn = QPushButton("✓ Mark Step Complete"); self.complete_step_btn.clicked.connect(self._toggle_step_complete); sl.addWidget(self.complete_step_btn)
        self.detail_tabs.addTab(sw, "📋 Steps")
        
        # Materials Tab
        self.materials_widget = QWidget(); self.materials_layout = QVBoxLayout(self.materials_widget); self.materials_layout.setContentsMargins(12,12,12,12)
        self.detail_tabs.addTab(self.materials_widget, "🧵 Materials")
        
        # Notes Tab
        nw = QWidget(); nwl = QVBoxLayout(nw); nwl.setContentsMargins(12,12,12,12)
        self.notes_edit = QTextEdit(); self.notes_edit.textChanged.connect(self._save_notes); nwl.addWidget(self.notes_edit)
        self.detail_tabs.addTab(nw, "📝 Notes")
        
        rl.addWidget(self.detail_tabs); splitter.addWidget(right); splitter.setSizes([550, 450]); layout.addWidget(splitter, 1)
        self.page_stack.addWidget(self.detail_page)

    def _build_calculator(self):
        c = self._get_colors(); page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(30,20,30,20)
        h = QLabel("Calculators 🧮"); h.setFont(QFont('Segoe UI', 22, QFont.Bold)); layout.addWidget(h)
        
        content = QHBoxLayout()
        
        # Fabric Yardage Calc
        yf = QFrame(); yf.setStyleSheet(f"QFrame {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 10px; }}")
        yl = QVBoxLayout(yf); yl.setContentsMargins(20,16,20,16); yl.addWidget(self._make_section_label("📏 Fabric Yardage", c))
        form = QFormLayout()
        self.fab_width_spin = QDoubleSpinBox(); self.fab_width_spin.setRange(20,72); self.fab_width_spin.setValue(45); self.fab_width_spin.setSuffix(" in"); form.addRow("Fabric Width:", self.fab_width_spin)
        self.pat_len_spin = QDoubleSpinBox(); self.pat_len_spin.setRange(1,200); self.pat_len_spin.setValue(36); self.pat_len_spin.setSuffix(" in"); form.addRow("Pattern Length:", self.pat_len_spin)
        self.num_pcs_spin = QDoubleSpinBox(); self.num_pcs_spin.setRange(1,50); self.num_pcs_spin.setValue(2); self.num_pcs_spin.setDecimals(0); form.addRow("Pieces:", self.num_pcs_spin)
        calc_btn = QPushButton("🧮 Calculate"); calc_btn.clicked.connect(self._calc_fabric); form.addRow(calc_btn)
        self.fabric_result = QLabel("Enter values and click Calculate"); self.fabric_result.setWordWrap(True); self.fabric_result.setStyleSheet(f"background-color: {c['success_light']}; color: {c['success']}; border-radius: 6px; padding: 12px; font-weight: bold;")
        form.addRow(self.fabric_result); yl.addLayout(form); yl.addStretch(); content.addWidget(yf, 1)
        
        # PATTERN GRADING CALCULATOR (NEW)
        gf = QFrame(); gf.setStyleSheet(f"QFrame {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 10px; }}")
        gl = QVBoxLayout(gf); gl.setContentsMargins(20,16,20,16); gl.addWidget(self._make_section_label("📐 Pattern Grading / Scaling", c))
        gform = QFormLayout()
        self.std_bust = QDoubleSpinBox(); self.std_bust.setRange(10,80); self.std_bust.setValue(36); self.std_bust.setSuffix(" in"); gform.addRow("Pattern Bust:", self.std_bust)
        self.usr_bust = QDoubleSpinBox(); self.usr_bust.setRange(10,80); self.usr_bust.setValue(38); self.usr_bust.setSuffix(" in"); gform.addRow("Your Bust:", self.usr_bust)
        self.std_waist = QDoubleSpinBox(); self.std_waist.setRange(10,60); self.std_waist.setValue(28); self.std_waist.setSuffix(" in"); gform.addRow("Pattern Waist:", self.std_waist)
        self.usr_waist = QDoubleSpinBox(); self.usr_waist.setRange(10,60); self.usr_waist.setValue(30); self.usr_waist.setSuffix(" in"); gform.addRow("Your Waist:", self.usr_waist)
        self.std_hip = QDoubleSpinBox(); self.std_hip.setRange(10,80); self.std_hip.setValue(38); self.std_hip.setSuffix(" in"); gform.addRow("Pattern Hip:", self.std_hip)
        self.usr_hip = QDoubleSpinBox(); self.usr_hip.setRange(10,80); self.usr_hip.setValue(40); self.usr_hip.setSuffix(" in"); gform.addRow("Your Hip:", self.usr_hip)
        
        grade_btn = QPushButton("📐 Calculate Grade"); grade_btn.clicked.connect(self._calc_grading); gform.addRow(grade_btn)
        self.grade_result = QLabel("Input measurements to calculate scaling percentage."); self.grade_result.setWordWrap(True); self.grade_result.setStyleSheet(f"background-color: {c['info_light']}; color: {c['info']}; border-radius: 6px; padding: 12px; font-weight: bold;")
        gform.addRow(self.grade_result)
        gl.addLayout(gform); gl.addStretch(); content.addWidget(gf, 1)
        
        layout.addLayout(content, 1); self.page_stack.addWidget(page)

    def _build_glossary(self):
        c = self._get_colors(); page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(30,20,30,20)
        l.addWidget(QLabel("Glossary 📖")); self.glossary_scroll = QScrollArea(); self.glossary_scroll.setWidgetResizable(True)
        self.glossary_inner = QWidget(); self.glossary_inner_layout = QVBoxLayout(self.glossary_inner); self.glossary_scroll.setWidget(self.glossary_inner)
        self._populate_glossary(); l.addWidget(self.glossary_scroll, 1); self.page_stack.addWidget(page)

    def _populate_glossary(self):
        c = self._get_colors()
        while self.glossary_inner_layout.count():
            item = self.glossary_inner_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for term, defn in GLOSSARY:
            card = QFrame(); card.setStyleSheet(f"QFrame {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 6px; }}")
            cl = QVBoxLayout(card); cl.setContentsMargins(14,8,14,8)
            tl = QLabel(term); tl.setFont(QFont('Segoe UI', 11, QFont.Bold)); tl.setStyleSheet(f"color: {c['primary']}; border: none;"); cl.addWidget(tl)
            dl = QLabel(defn); dl.setWordWrap(True); dl.setStyleSheet(f"color: {c['text']}; border: none;"); cl.addWidget(dl)
            self.glossary_inner_layout.addWidget(card)
        self.glossary_inner_layout.addStretch()

    def _build_measurements_page(self):
        c = self._get_colors(); page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(30,20,30,20)
        l.addWidget(QLabel("Body Measurements 📏")); self.meas_spins = {}
        form = QFormLayout()
        for label, key in [("Bust","bust"),("Waist","waist"),("Hips","hips")]:
            s = QDoubleSpinBox(); s.setRange(0,100); s.setSuffix(" in")
            if key in self.measurements: s.setValue(float(self.measurements[key]))
            s.valueChanged.connect(lambda v, k=key: self._update_meas(k,v)); self.meas_spins[key] = s; form.addRow(label+":", s)
        l.addLayout(form); self.page_stack.addWidget(page)

    def _update_meas(self, k, v): self.measurements[k] = v; self._save_data()

    def _build_progress_page(self):
        c = self._get_colors(); page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(30,20,30,20)
        l.addWidget(QLabel("My Progress 📊"))
        total_steps_all = sum(len(p.steps) for p in self.patterns); total_done = sum(len(v) for v in self.completed_steps.values())
        pct = int(total_done/total_steps_all*100) if total_steps_all else 0
        prog = QProgressBar(); prog.setValue(pct); l.addWidget(prog)
        for p in self.patterns:
            done = len(self.completed_steps.get(p.name, set())); tot = len(p.steps)
            ppct = int(done/tot*100) if tot else 0
            lbl = QLabel(f"{p.name}: {done}/{tot} ({ppct}%)"); l.addWidget(lbl)
        l.addStretch(); self.page_stack.addWidget(page)

    def _build_fabric_stash_page(self):
        c = self._get_colors(); page = QWidget(); layout = QHBoxLayout(page); layout.setContentsMargins(30,20,30,20)
        
        # Left: List
        left = QVBoxLayout()
        left.addWidget(self._make_section_label("🧶 My Fabric Stash", c))
        self.stash_list = QListWidget(); self.stash_list.currentRowChanged.connect(self._load_stash_item)
        self.stash_list.setStyleSheet(f"QListWidget {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 6px; padding: 4px; color: {c['text']}; }}")
        left.addWidget(self.stash_list, 1)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Fabric"); add_btn.setStyleSheet(f"background-color: {c['success']}; color: white; border: none; border-radius: 6px; padding: 8px; font-weight: bold;")
        add_btn.clicked.connect(self._add_stash_item); btn_layout.addWidget(add_btn)
        del_btn = QPushButton("🗑️ Delete"); del_btn.setStyleSheet(f"background-color: {c['danger']}; color: white; border: none; border-radius: 6px; padding: 8px; font-weight: bold;")
        del_btn.clicked.connect(self._del_stash_item); btn_layout.addWidget(del_btn)
        left.addLayout(btn_layout)
        
        layout.addLayout(left, 1)
        
        # Right: Form
        right = QVBoxLayout()
        right.addWidget(self._make_section_label("📋 Fabric Details", c))
        form = QFormLayout()
        self.stash_name = QLineEdit(); self.stash_name.setPlaceholderText("e.g., Blue Denim"); form.addRow("Name:", self.stash_name)
        self.stash_yards = QDoubleSpinBox(); self.stash_yards.setRange(0,100); self.stash_yards.setDecimals(2); self.stash_yards.setSuffix(" yards"); form.addRow("Yardage:", self.stash_yards)
        self.stash_width = QDoubleSpinBox(); self.stash_width.setRange(20,72); self.stash_width.setValue(45); self.stash_width.setSuffix(" in"); form.addRow("Width:", self.stash_width)
        self.stash_fiber = QComboBox(); self.stash_fiber.addItems(["Cotton", "Linen", "Silk", "Wool", "Polyester", "Denim", "Canvas", "Jersey", "Flannel", "Other"]); self.stash_fiber.setEditable(True); form.addRow("Fiber:", self.stash_fiber)
        self.stash_color = QLineEdit(); self.stash_color.setPlaceholderText("e.g., Navy Blue"); form.addRow("Color:", self.stash_color)
        
        save_btn = QPushButton("💾 Save Fabric"); save_btn.setStyleSheet(f"background-color: {c['primary']}; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self._save_stash_item); form.addRow(save_btn)
        right.addLayout(form); right.addStretch()
        layout.addLayout(right, 1)
        
        self._refresh_stash_list()
        self.page_stack.addWidget(page)

    def _build_stitch_library_page(self):
        c = self._get_colors(); page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(30,20,30,20)
        layout.addWidget(self._make_section_label("🪡 Stitch Library", c))
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner = QWidget(); inner_layout = QVBoxLayout(inner); inner_layout.setSpacing(12)
        
        hand_label = QLabel("✋ Hand Stitches"); hand_label.setFont(QFont('Segoe UI', 14, QFont.Bold)); inner_layout.addWidget(hand_label)
        for s in STITCHES:
            if s['type'] == 'hand':
                card = QFrame(); card.setStyleSheet(f"QFrame {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 8px; }}")
                cl = QHBoxLayout(card); cl.setContentsMargins(12,8,12,8)
                canvas = StitchCanvas(s['draw']); cl.addWidget(canvas)
                info = QVBoxLayout(); info.setSpacing(2)
                name_lbl = QLabel(s['name']); name_lbl.setFont(QFont('Segoe UI', 12, QFont.Bold)); name_lbl.setStyleSheet(f"color: {c['primary']}; border: none;"); info.addWidget(name_lbl)
                uses_lbl = QLabel(s['uses']); uses_lbl.setWordWrap(True); uses_lbl.setStyleSheet(f"color: {c['text']}; border: none;"); info.addWidget(uses_lbl)
                cl.addLayout(info, 1); inner_layout.addWidget(card)
                
        machine_label = QLabel("🧵 Machine Stitches"); machine_label.setFont(QFont('Segoe UI', 14, QFont.Bold)); inner_layout.addWidget(machine_label)
        for s in STITCHES:
            if s['type'] == 'machine':
                card = QFrame(); card.setStyleSheet(f"QFrame {{ background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 8px; }}")
                cl = QHBoxLayout(card); cl.setContentsMargins(12,8,12,8)
                canvas = StitchCanvas(s['draw']); cl.addWidget(canvas)
                info = QVBoxLayout(); info.setSpacing(2)
                name_lbl = QLabel(s['name']); name_lbl.setFont(QFont('Segoe UI', 12, QFont.Bold)); name_lbl.setStyleSheet(f"color: {c['primary']}; border: none;"); info.addWidget(name_lbl)
                uses_lbl = QLabel(s['uses']); uses_lbl.setWordWrap(True); uses_lbl.setStyleSheet(f"color: {c['text']}; border: none;"); info.addWidget(uses_lbl)
                cl.addLayout(info, 1); inner_layout.addWidget(card)
        
        inner_layout.addStretch(); scroll.setWidget(inner); layout.addWidget(scroll, 1)
        self.page_stack.addWidget(page)

    # ---- LOGIC ----
    def _make_section_label(self, t, c):
        l = QLabel(t); l.setFont(QFont('Segoe UI', 13, QFont.Bold)); l.setStyleSheet(f"color: {c['text']}; border: none; margin-bottom: 8px;"); return l

    def _open_pattern_detail(self, pattern):
        self.current_pattern = pattern; self.current_step = 0; self._load_pattern_detail(); self._switch_page(2)

    def _load_pattern_detail(self):
        p = self.current_pattern; c = self._get_colors()
        if not p: return
        self.detail_title.setText(f"{CATEGORY_ICONS.get(p.category, '📐')} {p.name}")
        self.pattern_canvas.set_dark_mode(self.dark_mode); self.pattern_canvas.set_pieces(p.pieces)
        self.piece_list.clear()
        for pc in p.pieces:
            item = QListWidgetItem(f"🧩 {pc.name}"); item.setForeground(QColor(pc.color)); self.piece_list.addItem(item)
        self._update_step_display()
        
        # Materials with stash check
        while self.materials_layout.count():
            item = self.materials_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.materials_layout.addWidget(self._make_section_label("🧵 Materials & Supplies", c))
        
        for mat in p.materials:
            mat_frame = QFrame(); mat_frame.setStyleSheet(f"QFrame {{ background-color: {c['bg']}; border: 1px solid {c['border']}; border-radius: 6px; }}")
            mfl = QVBoxLayout(mat_frame); mfl.setContentsMargins(12,8,12,8)
            top_row = QHBoxLayout()
            top_row.addWidget(QLabel(f"• {mat['name']}"))
            top_row.addWidget(QLabel(mat['amount']), 1)
            
            # Check stash
            needed_match = re.search(r'([\d.]+)\s*yard', mat['amount'], re.IGNORECASE)
            needed_yards = float(needed_match.group(1)) if needed_match else 0
            found_in_stash = False
            for s in self.fabric_stash:
                # Simple keyword match on fiber/name
                if s['fiber'].lower() in mat['name'].lower() or s['name'].lower() in mat['name'].lower():
                    if s['yards'] >= needed_yards and needed_yards > 0:
                        stash_lbl = QLabel("✅ In Stash!"); stash_lbl.setStyleSheet(f"color: {c['success']}; font-weight: bold; border: none;"); top_row.addWidget(stash_lbl); found_in_stash = True; break
            if not found_in_stash and needed_yards > 0:
                need_lbl = QLabel("🛒 Need to buy"); need_lbl.setStyleSheet(f"color: {c['text_light']}; font-size: 10px; border: none;"); top_row.addWidget(need_lbl)
                
            mfl.addLayout(top_row)
            if mat.get('note'): mfl.addWidget(QLabel(f"({mat['note']})"))
            self.materials_layout.addWidget(mat_frame)
            
        self.notes_edit.blockSignals(True); self.notes_edit.setText(self.notes.get(p.name, "")); self.notes_edit.blockSignals(False)
        self.materials_layout.addStretch()

    def _update_step_display(self):
        p = self.current_pattern; c = self._get_colors()
        if not p: return
        total = len(p.steps); step = p.steps[self.current_step]
        done = len(self.completed_steps.get(p.name, set())); pct = int(done/total*100) if total else 0
        self.step_progress.setValue(pct); self.step_indicator.setText(f"Step {self.current_step+1} / {total}")
        self.step_title.setText(step['title']); self.step_desc.setText(step['description'])
        self.step_tip.setText(f"💡 Tip: {step['tip']}" if step.get('tip') else "")
        completed = self.current_step in self.completed_steps.get(p.name, set())
        self.complete_step_btn.setText("✓ Step Completed ✓" if completed else "✓ Mark Step Complete")
        self.complete_step_btn.setStyleSheet(f"background-color: {c['bg_dark'] if completed else c['success']}; color: {c['success'] if completed else 'white'}; border: 2px solid {c['success']}; border-radius: 6px; padding: 10px; font-weight: bold;")
        self.prev_step_btn.setEnabled(self.current_step > 0); self.next_step_btn.setEnabled(self.current_step < total-1)

    def _prev_step(self): 
        if self.current_step > 0: self.current_step -= 1; self._update_step_display()
    def _next_step(self): 
        if self.current_pattern and self.current_step < len(self.current_pattern.steps)-1: self.current_step += 1; self._update_step_display()
    def _toggle_step_complete(self):
        p = self.current_pattern
        if not p: return
        if p.name not in self.completed_steps: self.completed_steps[p.name] = set()
        if self.current_step in self.completed_steps[p.name]: self.completed_steps[p.name].discard(self.current_step)
        else: self.completed_steps[p.name].add(self.current_step)
        self._update_step_display(); self._save_data()
    def _toggle_favorite(self):
        if not self.current_pattern: return
        n = self.current_pattern.name
        if n in self.favorites: self.favorites.discard(n)
        else: self.favorites.add(n)
        self._load_pattern_detail(); self._save_data()
    def _save_notes(self):
        if self.current_pattern: self.notes[self.current_pattern.name] = self.notes_edit.toPlainText(); self._save_data()

    # ---- FABRIC CALCULATOR ----
    def _calc_fabric(self):
        w = self.fab_width_spin.value(); l = self.pat_len_spin.value(); pcs = int(self.num_pcs_spin.value())
        rows = math.ceil((pcs * l) / w); total_in = rows * l
        self.fabric_result.setText(f"Estimated: {total_in/36:.2f} yards ({total_in:.0f} inches)")

    # ---- PATTERN GRADING CALCULATOR ----
    def _calc_grading(self):
        c = self._get_colors()
        sb, ub = self.std_bust.value(), self.usr_bust.value()
        sw, uw = self.std_waist.value(), self.usr_waist.value()
        sh, uh = self.std_hip.value(), self.usr_hip.value()
        
        diff_bust = ub - sb; diff_waist = uw - sw; diff_hip = uh - sh
        scale_bust = (ub / sb) * 100 if sb else 100
        scale_waist = (uw / sw) * 100 if sw else 100
        scale_hip = (uh / sh) * 100 if sh else 100
        
        # Average uniform scale for home printing (simplification)
        avg_scale = (scale_bust + scale_waist + scale_hip) / 3
        
        result_text = (
            f"<b>Uniform Scaling (for print):</b> {avg_scale:.1f}%<br><br>"
            f"<b>Differences (for manual grading):</b><br>"
            f"• Bust: {diff_bust:+.1f} inches ({scale_bust:.1f}%)<br>"
            f"• Waist: {diff_waist:+.1f} inches ({scale_waist:.1f}%)<br>"
            f"• Hips: {diff_hip:+.1f} inches ({scale_hip:.1f}%)<br><br>"
            f"<i>💡 Tip: If printing at home, scale the PDF by {avg_scale:.1f}%. "
            f"For better fit, grade each area manually by adding {diff_bust/4:.2f}\" to each side seam at the bust.</i>"
        )
        self.grade_result.setText(result_text)

    # ---- FABRIC STASH ----
    def _refresh_stash_list(self):
        self.stash_list.clear()
        for s in self.fabric_stash:
            self.stash_list.addItem(f"{s['name']} ({s['yards']} yd, {s['fiber']})")
    
    def _load_stash_item(self, row):
        if 0 <= row < len(self.fabric_stash):
            s = self.fabric_stash[row]
            self.stash_name.setText(s['name']); self.stash_yards.setValue(s['yards'])
            self.stash_width.setValue(s['width']); self.stash_color.setText(s['color'])
            idx = self.stash_fiber.findText(s['fiber'])
            if idx >= 0: self.stash_fiber.setCurrentIndex(idx)
            else: self.stash_fiber.setEditText(s['fiber'])
            
    def _save_stash_item(self):
        row = self.stash_list.currentRow()
        data = {"name": self.stash_name.text(), "yards": self.stash_yards.value(), "width": self.stash_width.value(), "fiber": self.stash_fiber.currentText(), "color": self.stash_color.text()}
        if 0 <= row < len(self.fabric_stash): self.fabric_stash[row] = data
        else: self.fabric_stash.append(data)
        self._refresh_stash_list(); self._save_data()
        
    def _add_stash_item(self):
        self.stash_list.setCurrentRow(-1)
        self.stash_name.clear(); self.stash_yards.setValue(0); self.stash_width.setValue(45); self.stash_color.clear(); self.stash_fiber.setCurrentIndex(0)
        
    def _del_stash_item(self):
        row = self.stash_list.currentRow()
        if 0 <= row < len(self.fabric_stash):
            self.fabric_stash.pop(row); self._refresh_stash_list(); self._save_data()

    # ---- PDF EXPORT ----
    def _export_pdf(self):
        if not self.current_pattern:
            QMessageBox.warning(self, "Export Error", "No pattern selected."); return
            
        path, _ = QFileDialog.getSaveFileName(self, "Save Pattern PDF", f"{self.current_pattern.name}_Pattern.pdf", "PDF Files (*.pdf)")
        if not path: return
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat); printer.setOutputFileName(path)
        printer.setPageSize(QPageSize(QPageSize.Letter)); printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        painter = QPainter(printer)
        font = QFont("Arial", 8); painter.setFont(font)
        
        # Calculate bounds of all pieces
        bounds = QRectF()
        for piece in self.current_pattern.pieces:
            bounds = bounds.united(piece.path.boundingRect())
            
        # Scaling: 1 unit = 1 mm for standard drafting
        scale = 3.78  # 1 mm = 3.78 dots at 96 dpi
        
        page_rect = printer.pageRect(QPrinter.DevicePixel); page_w = page_rect.width(); page_h = page_rect.height()
        
        # Calculate grid
        cols = math.ceil((bounds.width() * scale) / page_w)
        rows = math.ceil((bounds.height() * scale) / page_h)
        
        row_labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        for r in range(rows):
            for c_idx in range(cols):
                # Offset translation for tiling
                painter.save()
                painter.translate(-c_idx * page_w, -r * page_h)
                
                # Draw pieces
                for piece in self.current_pattern.pieces:
                    path = QPainterPath(piece.path)
                    path.translate(-bounds.x(), -bounds.y()) # Normalize to 0,0
                    path.translate(50, 50) # Padding
                    
                    painter.setPen(QPen(QColor(piece.color), 2)); painter.setBrush(QColor(piece.color).lighter(150))
                    painter.drawPath(path)
                    
                    # Label
                    br = path.boundingRect(); painter.setPen(QColor("#333333"))
                    painter.drawText(br, Qt.AlignCenter, piece.name)
                
                painter.restore()
                
                # Draw Alignment Marks and Page Label
                painter.setPen(QPen(QColor("#000000"), 1))
                mark_size = 20
                
                # Top Left
                painter.drawLine(0, 0, mark_size, 0); painter.drawLine(0, 0, 0, mark_size)
                # Top Right
                painter.drawLine(page_w, 0, page_w - mark_size, 0); painter.drawLine(page_w, 0, page_w, mark_size)
                # Bottom Left
                painter.drawLine(0, page_h, mark_size, page_h); painter.drawLine(0, page_h, 0, page_h - mark_size)
                # Bottom Right
                painter.drawLine(page_w, page_h, page_w - mark_size, page_h); painter.drawLine(page_w, page_h, page_w, page_h - mark_size)
                
                # Alignment Diamonds (if not edge)
                if c_idx > 0:  # Left edge mark
                    mid_y = page_h / 2; painter.drawLine(0, mid_y - mark_size, 0, mid_y + mark_size)
                    painter.drawPolygon([QPointF(-5, mid_y), QPointF(0, mid_y - 5), QPointF(5, mid_y), QPointF(0, mid_y + 5)])
                if r > 0:  # Top edge mark
                    mid_x = page_w / 2; painter.drawLine(mid_x - mark_size, 0, mid_x + mark_size, 0)
                    painter.drawPolygon([QPointF(mid_x, -5), QPointF(mid_x + 5, 0), QPointF(mid_x, 5), QPointF(mid_x - 5, 0)])
                
                # Page Label
                page_label = f"{row_labels[r]}{c_idx+1}"
                painter.setFont(QFont("Arial", 14, QFont.Bold)); painter.drawText(20, 30, page_label)
                painter.setFont(QFont("Arial", 8)); painter.drawText(20, 50, self.current_pattern.name)
                
                if not (r == rows - 1 and c_idx == cols - 1):
                    printer.newPage()
                    
        painter.end()
        QMessageBox.information(self, "PDF Exported", f"Pattern successfully exported to:\n{path}\n\nRemember to print at 100% scale (no scaling)!")

    # ---- THEME ----
    def _toggle_theme(self):
        self.dark_mode = self.theme_btn.isChecked(); self._save_data(); self._apply_theme()
        
    def _apply_theme(self):
        c = self._get_colors()
        self.theme_btn.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        self.sidebar.setStyleSheet(f"QFrame {{ background-color: {c['sidebar']}; border: none; }}")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(c['bg'])); palette.setColor(QPalette.WindowText, QColor(c['text']))
        palette.setColor(QPalette.Base, QColor(c['card'])); palette.setColor(QPalette.AlternateBase, QColor(c['bg_dark']))
        palette.setColor(QPalette.Text, QColor(c['text'])); palette.setColor(QPalette.Button, QColor(c['bg_dark']))
        palette.setColor(QPalette.ButtonText, QColor(c['text'])); palette.setColor(QPalette.Highlight, QColor(c['primary']))
        QApplication.instance().setPalette(palette)
        self.setStyleSheet(f"QMainWindow {{ background-color: {c['bg']}; }} QLabel {{ color: {c['text']}; }}")
        if self.current_pattern: self._load_pattern_detail()


# ======================== MAIN ========================
def main():
    app = QApplication(sys.argv); app.setStyle('Fusion'); app.setFont(QFont('Segoe UI', 10))
    window = PatternLearnApp(); window.show(); sys.exit(app.exec())

if __name__ == '__main__':
    main()
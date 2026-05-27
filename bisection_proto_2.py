import sys
import math
import re

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


SUPERSCRIPT_MAP = {
    "\u00b2": "**2",
    "\u00b3": "**3",
    "\u2074": "**4",
    "\u2070": "**0",
    "\u00b9": "**1",
    "\u2075": "**5",
    "\u2076": "**6",
    "\u2077": "**7",
    "\u2078": "**8",
    "\u2079": "**9",
}


def convert_superscript(expr: str) -> str:
    for char, replacement in SUPERSCRIPT_MAP.items():
        expr = expr.replace(char, replacement)
    return expr


def preprocess_expression(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = re.sub(r"(\d+)(x)", r"\1*\2", expr)
    expr = re.sub(r"(\d+)(\()", r"\1*\2", expr)
    expr = convert_superscript(expr)
    return expr


def create_function(expr: str):
    expr = preprocess_expression(expr)
    allowed = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "log10": math.log10,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "ceil": math.ceil,
        "floor": math.floor,
        "factorial": math.factorial,
        "abs": abs,
        "pi": math.pi,
        "e": math.e,
    }
    safe_builtins = {"True": True, "False": False, "abs": abs, "round": round}
    return lambda x: eval(expr, {"__builtins__": {}}, {**safe_builtins, **allowed, "x": x})


def bisection(f, a, b, max_iter=50, tol=1e-6):
    fa, fb = f(a), f(b)

    if abs(fa) < tol:
        return a, [(0, a, b, a, fa, fb, fa)]
    if abs(fb) < tol:
        return b, [(0, a, b, b, fa, fb, fb)]

    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    steps = []

    for i in range(max_iter):
        m = (a + b) / 2
        fm = f(m)

        steps.append((i, a, b, m, fa, fb, fm))

        if abs(fm) < tol or (b - a) / 2 < tol:
            return m, steps

        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm

    return m, steps


class FocusLineEdit(QLineEdit):
    def __init__(self, placeholder: str = "", value: str = ""):
        super().__init__()
        self.setText(value)
        self.setPlaceholderText(placeholder)
        self._on_focus = None

    def set_on_focus(self, callback):
        self._on_focus = callback

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self._on_focus:
            self._on_focus(self)


class BisectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bisection Method Calculator")
        self.setGeometry(100, 100, 1100, 650)

        self.active = None
        self.buttons_list = []
        self.grid = None

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        vsplit = QSplitter(Qt.Orientation.Vertical)
        left_layout.addWidget(vsplit)

        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        self.func = self.make_input("f(x)", "x^3 - x - 2")
        self.a = self.make_input("a", "1")
        self.b = self.make_input("b", "2")
        self.iters = self.make_input("Iterations", "50")

        self.solve_btn = QPushButton("Solve")
        self.solve_btn.clicked.connect(self.solve)

        self.result = QLabel("Root \u2248")

        self.widgets = [self.func, self.a, self.b, self.iters, self.solve_btn, self.result]

        for w in self.widgets:
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        input_layout.addWidget(self.func)
        input_layout.addWidget(self.a)
        input_layout.addWidget(self.b)
        input_layout.addWidget(self.iters)
        input_layout.addWidget(self.solve_btn)
        input_layout.addWidget(self.result)
        input_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["n", "a", "b", "m", "f(a)", "f(b)", "f(m)"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.verticalHeader().setVisible(False)
        vsplit.addWidget(input_widget)
        vsplit.addWidget(self.table)

        vsplit.setStretchFactor(0, 2)
        vsplit.setStretchFactor(1, 5)

        right_widget = QWidget()
        calc_layout = QVBoxLayout(right_widget)
        calc_layout.setContentsMargins(10, 10, 10, 10)

        self.grid = QGridLayout()
        self.grid.setSpacing(8)

        buttons = [
            ["x", "y", "C", "\u232b"],
            ["x\u00b3", "x\u00b2", "\u221a", "\u00f7"],
            ["7", "8", "9", "\u00d7"],
            ["4", "5", "6", "\u2212"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="],
        ]

        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = QPushButton(text)

                btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding,
                )

                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        color: white;
                        border-radius: 6px;
                        font-size: 15px;
                    }
                    QPushButton:hover {
                        background-color: #3a3a3a;
                    }
                """)

                if text == "=":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4cc2ff;
                            color: black;
                            font-size: 18px;
                            font-weight: bold;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #6dd1ff;
                        }
                    """)

                btn.clicked.connect(lambda _, t=text: self.handle_calc(t))
                self.grid.addWidget(btn, i, j)
                self.buttons_list.append(btn)

        calc_layout.addLayout(self.grid)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(6)

    def make_input(self, ph, val=""):
        w = FocusLineEdit(ph, val)
        w.set_on_focus(lambda x: self.set_active(x))
        return w

    def set_active(self, w):
        self.active = w

    def handle_calc(self, t):
        if not self.active:
            self.active = self.func

        w = self.active

        if t == "C":
            w.clear()
        elif t == "y":
            w.clear()
        elif t == "\u232b":
            w.backspace()
        elif t == "x\u00b3":
            w.insert("\u00b3")
        elif t == "x\u00b2":
            w.insert("\u00b2")
        elif t == "\u221a":
            w.insert("sqrt(")
        elif t == "\u00d7":
            w.insert("*")
        elif t == "\u00f7":
            w.insert("/")
        elif t == "\u2212":
            w.insert("-")
        elif t == "x":
            w.insert("x")
        elif t == "+/-":
            text = w.text()
            cursor = w.cursorPosition()
            if text and cursor > 0:
                if text[cursor - 1] == "-":
                    w.setText(text[: cursor - 1] + text[cursor:])
                    w.setCursorPosition(cursor - 1)
                else:
                    w.insert("-")
            else:
                w.insert("-")
        elif t == "=":
            self.solve()
        else:
            w.insert(t)

    def solve(self):
        try:
            f = create_function(self.func.text())
            a = float(self.a.text())
            b = float(self.b.text())
            it = int(self.iters.text())

            if a == b:
                raise ValueError("a and b must be different values")

            root, steps = bisection(f, a, b, it)

            self.table.setRowCount(len(steps))

            for i, (n, a1, b1, m, fa, fb, fm) in enumerate(steps):
                self.table.setItem(i, 0, QTableWidgetItem(str(n)))
                self.table.setItem(i, 1, QTableWidgetItem(f"{a1:.4f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{b1:.4f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{m:.4f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{fa:.4f}"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{fb:.4f}"))
                self.table.setItem(i, 6, QTableWidgetItem(f"{fm:.4f}"))

            self.result.setText(f"Root \u2248 {root}")

        except ValueError as e:
            QMessageBox.critical(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)

        height = self.height()

        btn_size = max(50, int(height / 7))
        btn_font_size = max(10, int(height / 50))

        input_font_size = max(9, int(height / 55))
        input_padding = max(5, int(height / 100))

        table_font_size = max(8, int(height / 65))
        table_row_height = max(18, int(height / 30))

        label_font_size = max(9, int(height / 60))

        input_style = f"""
            QLineEdit, QLabel {{
                font-size: {input_font_size}px;
                padding: {input_padding}px;
            }}
        """

        for w in self.widgets:
            w.setStyleSheet(input_style)
            if isinstance(w, QPushButton):
                w.setMinimumHeight(int(btn_size * 0.8))

        self.solve_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {input_font_size}px;
                padding: {input_padding}px;
                background-color: #1e7fb0;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a9bc5;
            }}
        """)

        for btn in self.buttons_list:
            btn.setMinimumHeight(btn_size)
            btn.setMinimumWidth(btn_size)

            if btn.text() == "=":
                eq_font_size = max(18, int(height / 45))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #4cc2ff;
                        color: black;
                        font-size: {eq_font_size}px;
                        font-weight: bold;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: #6dd1ff;
                    }}
                    QPushButton:pressed {{
                        background-color: #3ab8ff;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2b2b2b;
                        color: white;
                        border-radius: 6px;
                        font-size: {btn_font_size}px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3a3a3a;
                    }}
                    QPushButton:pressed {{
                        background-color: #1a1a1a;
                    }}
                """)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {table_font_size}px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
        """)
        self.table.verticalHeader().setDefaultSectionSize(table_row_height)

        self.result.setStyleSheet(f"""
            QLabel {{
                font-size: {label_font_size}px;
                font-weight: bold;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BisectionApp()
    window.show()
    sys.exit(app.exec())

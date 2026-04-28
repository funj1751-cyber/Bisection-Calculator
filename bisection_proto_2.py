import sys
import math
import re

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


def convert_superscript(expr):
    return expr.replace("²", "**2").replace("³", "**3").replace("⁴", "**4")


def preprocess_expression(expr):
    expr = expr.replace("^", "**")
    expr = re.sub(r'(\d)(x)', r'\1*\2', expr)
    expr = re.sub(r'(\d)(\()', r'\1*\2', expr)
    expr = convert_superscript(expr)
    return expr


def create_function(expr):
    expr = preprocess_expression(expr)
    allowed = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "pi": math.pi,
        "e": math.e
    }
    return lambda x: eval(expr, {"__builtins__": {}}, {**allowed, "x": x})


def bisection(f, a, b, max_iter=50):
    fa, fb = f(a), f(b)

    if fa * fb >= 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    steps = []
    prev = None

    for i in range(max_iter):
        m = (a + b) / 2
        fm = f(m)

        steps.append((i, a, b, m, fa, fb, fm))

        if prev is not None and round(prev, 3) == round(m, 3):
            return round(m, 3), steps

        prev = m

        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm

    return round(m, 3), steps


class BisectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bisection Method - Professional UI")
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

        self.result = QLabel("Root ≈")

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
            ["x", "y", "C", "⌫"],
            ["x³", "x²", "√", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="]
        ]

        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = QPushButton(text)

                btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding
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
        w = QLineEdit()
        w.setText(val)
        w.setPlaceholderText(ph)
        w.focusInEvent = lambda e, x=w: self.set_active(x)
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
        elif t == "⌫":
            w.backspace()
        elif t == "x³":
            w.insert("³")
        elif t == "x²":
            w.insert("²")
        elif t == "√":
            w.insert("sqrt(")
        elif t == "×":
            w.insert("*")
        elif t == "÷":
            w.insert("/")
        elif t == "−":
            w.insert("-")
        elif t == "x":
            w.insert("x")
        elif t == "+/-":
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

            root, steps = bisection(f, a, b, it)

            self.table.setRowCount(len(steps))

            for i, (n,a1,b1,m,fa,fb,fm) in enumerate(steps):
                self.table.setItem(i,0,QTableWidgetItem(str(n)))
                self.table.setItem(i,1,QTableWidgetItem(f"{a1:.4f}"))
                self.table.setItem(i,2,QTableWidgetItem(f"{b1:.4f}"))
                self.table.setItem(i,3,QTableWidgetItem(f"{m:.4f}"))
                self.table.setItem(i,4,QTableWidgetItem(f"{fa:.4f}"))
                self.table.setItem(i,5,QTableWidgetItem(f"{fb:.4f}"))
                self.table.setItem(i,6,QTableWidgetItem(f"{fm:.4f}"))

            self.result.setText(f"Root ≈ {root}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        height = self.height()
        width = self.width()

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
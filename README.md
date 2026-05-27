# Bisection Method Calculator

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt-6-green)](https://www.riverbankcomputing.com/software/pyqt/)

A desktop GUI application for finding roots of equations using the bisection method. Built with Python and PyQt6.

## Features

- Interactive function input with on-screen calculator keypad
- Supports superscript notation (e.g., x², x³, x⁴)
- Step-by-step iteration table with full precision
- Real-time responsive UI
- Dark theme design

## Screenshots

![App Screenshot](screenshot.png)

## Setup

```bash
pip install PyQt6
python bisection_proto_2.py
```

## Usage

1. Enter a function in the `f(x)` field (e.g., `x^3 - x - 2`)
2. Set interval `[a, b]` endpoints
3. Click **Solve**
4. View iteration table and root result

### Supported Functions

- `sin`, `cos`, `tan`, `sqrt`, `exp`, `log`, `log10`
- `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`
- `ceil`, `floor`, `factorial`, `abs`
- Constants: `pi`, `e`

## License

MIT

"""Тесты примеров кода из книги.

Запуск:
    cd code
    python -m unittest discover -s tests -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

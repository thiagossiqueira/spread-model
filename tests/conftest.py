# tests/conftest.py
import sys
import os
import pytest

# Garante que o diretório src/ esteja no path para importações como src.utils.x
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

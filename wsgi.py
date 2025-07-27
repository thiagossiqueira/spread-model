import sys
import os

# Caminho absoluto para o diretório do projeto
project_home = '/home/tsiqueira4/spread-model'

# Garante que o diretório esteja no sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Define a variável de ambiente do Flask, se necessário
os.environ["FLASK_ENV"] = "production"

# Importa a aplicação Flask do app.py
from app import app as application

import sys
import os

# Redireciona print() para console + arquivo de log
class Logger:
    def __init__(self, filename="wsgi_log.txt"):
        self.terminal = sys.stdout
        log_path = os.path.join(os.path.dirname(__file__), filename)
        self.log = open(log_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Ativa o logger (apenas uma vez no deploy)
sys.stdout = sys.stderr = Logger()

# Caminho absoluto para o diretório do projeto
project_home = '/home/tsiqueira4/spread-model'

# Garante que o diretório esteja no sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Define a variável de ambiente do Flask, se necessário
os.environ["FLASK_ENV"] = "production"

# Importa a aplicação Flask do app.py
from app import app as application
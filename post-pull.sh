#!/bin/bash

echo "🔁 Iniciando post-pull automático..."

# 1. Git pull
echo "📥 Executando git pull..."
git pull origin master

# 2. Detecta se estamos no PythonAnywhere
if [[ "$HOME" == "/home/tsiqueira4" ]]; then
    echo "🧠 Ambiente detectado: PythonAnywhere (produção)"
    ON_PYTHONANYWHERE=true
else
    echo "🧠 Ambiente detectado: Local (desenvolvimento)"
    ON_PYTHONANYWHERE=false
fi

# 3. Ativa venv local (se existir)
if [ "$ON_PYTHONANYWHERE" = false ] && [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual local..."
    source venv/bin/activate
fi

# 4. Instala dependências e projeto
echo "📦 Instalando dependências com pip install -e ."
pip install -e .

# 5. Executa main.py para gerar gráficos
echo "📊 Executando main.py..."
python main.py

# 6. Se estiver no PythonAnywhere, força reload da app
if [ "$ON_PYTHONANYWHERE" = true ]; then
    echo "🌐 Recarregando aplicação com touch no wsgi.py"
    touch /var/www/tsiqueira4_pythonanywhere_com_wsgi.py
    echo "✅ Deploy finalizado: https://tsiqueira4.pythonanywhere.com"
else
    echo "✅ Projeto atualizado localmente com sucesso!"
fi
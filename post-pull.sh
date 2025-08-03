#!/bin/bash

echo "🚀 Iniciando pós-pull..."

# 1. Ativar ambiente virtual (ajuste se estiver em outro caminho)
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual local..."
    source venv/bin/activate
else
    echo "⚠️ Ambiente virtual não encontrado. Pulei essa etapa."
fi

# 2. Instalar dependências e projeto em modo editável
echo "📦 Instalando dependências..."
pip install -e .

# 3. Rodar o main.py para gerar gráficos e tabelas
echo "📊 Executando main.py para gerar visualizações..."
python main.py

# 4. Mensagem final
echo "✅ Projeto atualizado com sucesso!"
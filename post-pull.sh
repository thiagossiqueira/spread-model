#!/bin/bash
echo "🔁 Iniciando post-pull automático..."

# 🧠 Detecta se estamos no PythonAnywhere
if [[ "$HOME" == "/home/tsiqueira4" ]]; then
    echo "🧠 Ambiente detectado: PythonAnywhere (produção)"
    ON_PYTHONANYWHERE=true
else
    echo "🧠 Ambiente detectado: Local (desenvolvimento)"
    ON_PYTHONANYWHERE=false
fi

# ⛔ Checa espaço livre antes de prosseguir (limite mínimo: 100MB)
MIN_FREE_SPACE_MB=100
FREE_MB=$(df -m . | tail -1 | awk '{print $4}')

if (( FREE_MB < MIN_FREE_SPACE_MB )); then
    echo "❌ ERRO: Espaço livre insuficiente (${FREE_MB}MB). Libere espaço antes de continuar."
    exit 1
fi

# 🧹 Sparse checkout apenas se não configurado
if ! git config core.sparseCheckout | grep -q true; then
    echo "🧾 Ativando sparse checkout..."
    git config core.sparseCheckout true
fi

# 🎯 Define arquivos permitidos via sparse
SPARSE_FILE=".git/info/sparse-checkout"
cat > "$SPARSE_FILE" <<EOF
/*
!datos_y_modelos/db/one-day_interbank_deposit_futures_contract_di/hist_di_curve_contracts_db.xlsx
!datos_y_modelos/db/one-day_interbank_deposit_futures_contract_di/hist_di_curve_contracts_db.v1.xlsx
!datos_y_modelos/db/brazil_domestic_equities/*
!datos_y_modelos/db/brazil_domestic_corp_bonds/brazil_debentures_universe/Resultado/resultado_parte*
EOF

# 🔄 Atualiza árvore de trabalho com sparse
git read-tree -mu HEAD

# 🔃 Atualiza repositório
echo "📥 Executando git pull..."
git pull origin master

# 🐍 Ativa venv local (se existir e ambiente for local)
if [ "$ON_PYTHONANYWHERE" = false ] && [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual local..."
    source venv/bin/activate
fi

# 🛠 Instala dependências
echo "📦 Instalando dependências com pip install -e ."
pip install -e . || {
    echo "❌ pip install falhou. Verifique espaço ou dependências quebradas."
    exit 1
}

# ▶️ Executa main.py
echo "📊 Executando main.py..."
python main.py || {
    echo "❌ Erro ao rodar main.py"
    exit 1
}

# 🔁 Reinicia app web se estiver em produção
if [ "$ON_PYTHONANYWHERE" = true ]; then
    echo "🌐 Recarregando aplicação com touch no wsgi.py"
    touch /var/www/tsiqueira4_pythonanywhere_com_wsgi.py
    echo "✅ Deploy finalizado: https://tsiqueira4.pythonanywhere.com"
else
    echo "✅ Projeto atualizado localmente com sucesso!"
fi

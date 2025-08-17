#!/bin/bash
echo "🔁 Iniciando post-pull automático..."

# Detecta se estamos no PythonAnywhere
if [[ "$HOME" == "/home/tsiqueira4" ]]; then
    echo "🧠 Ambiente detectado: PythonAnywhere (produção)"
    ON_PYTHONANYWHERE=true
else
    echo "🧠 Ambiente detectado: Local (desenvolvimento)"
    ON_PYTHONANYWHERE=false
fi

# Ativa sparse checkout e ignora arquivos pesados
echo "📦 Configurando sparse checkout..."
git config core.sparseCheckout true

cat > .git/info/sparse-checkout <<EOF
/*
!datos_y_modelos/db/one-day_interbank_deposit_futures_contract_di/hist_di_curve_contracts_db.xlsx
!datos_y_modelos/db/one-day_interbank_deposit_futures_contract_di/hist_di_curve_contracts_db.v1.xlsx
!datos_y_modelos/db/brazil_domestic_equities/*
!datos_y_modelos/db/brazil_domestic_corp_bonds/brazil_debentures_universe/Resultado/resultado_parte*
EOF

# Aplica sparse checkout e tenta git pull
echo "📥 Executando git pull com sparse checkout..."
git read-tree -mu HEAD
git pull origin master || echo "⚠️ Git pull falhou — possível erro de cota."

# Ativa ambiente virtual (apenas localmente)
if [ "$ON_PYTHONANYWHERE" = false ] && [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual local..."
    source venv/bin/activate
fi

# Instala dependências (tentativa — pode falhar por cota)
echo "📦 Instalando dependências com pip install -e ."
pip install -e . || echo "⚠️ Instalação de dependências falhou — verifique cota ou permissão."

# Executa o main.py
echo "📊 Executando main.py..."
python main.py

# Reinicia o app se estiver no PythonAnywhere
if [ "$ON_PYTHONANYWHERE" = true ]; then
    echo "🌐 Recarregando aplicação com touch no wsgi.py"
    touch /var/www/tsiqueira4_pythonanywhere_com_wsgi.py
    echo "✅ Deploy finalizado: https://tsiqueira4.pythonanywhere.com"
else
    echo "✅ Projeto atualizado localmente com sucesso!"
fi
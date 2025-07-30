# config.py
from pathlib import Path

# Detecta o diretório raiz do projeto automaticamente
REPO_ROOT = Path(__file__).resolve()
while not (REPO_ROOT / ".git").exists() and REPO_ROOT != REPO_ROOT.parent:
    REPO_ROOT = REPO_ROOT.parent

# Caminhos centralizados para os arquivos de dados
CONFIG = {
    "CORP_PATH": REPO_ROOT / "datos_y_modelos" / "Domestic" / "brazil_domestic_corp_db.xlsx",
    "YA_PATH": REPO_ROOT / "datos_y_modelos" / "db" / "brazil_domestic_corp_bonds" / "ya.xlsx",
    "DI_CURVE_PATH": REPO_ROOT / "datos_y_modelos" / "db" / "one-day_interbank_deposit_futures_contract_di" / "hist_di_curve_contracts_db.xlsx",


    "TENORS": {
        "13-year": 13.0, "10-year": 10.0, "5-year": 5.0, "3-year": 3.0,
        "2-year": 2.0, "1-year": 1.0, "6-month": 0.5,
        "3-month": 0.25, "1-month": 1.0 / 12,
    },
    "OBS_WINDOW": 540  # dias para janela de observação
}
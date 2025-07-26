# README.md

## 📈 Corporate Bond Spread Model

Projeto modular para cálculo e visualização dos spreads entre títulos corporativos brasileiros e a curva DI interpolada, utilizando dados históricos ponto-a-ponto.

---


### 📁 Estrutura do Projeto
```
spread-model/
├── main.py
├── config.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── README.md
├── src/
│   ├── calendars/
│   │   └── daycounts.py
│   ├── finmath/
│   │   └── analytics.py
│   ├── utils/
│   │   ├── file_io.py
│   │   ├── filters.py
│   │   ├── interpolation.py
│   │   └── plotting.py
│   ├── core/
│   │   ├── spread_calculator.py
│   │   └── windowing.py
├── datos_y_modelos/
│   ├── db/
│   │   ├── ODA_Comdty.xlsx
│   │   ├── bsrch.xlsx
│   │   └── ya.xlsx
│   └── Domestic/
│       └── brazil_domestic_corp_db.xlsx
├── tests/
│   ├── test_spread_calculator.py
│   └── test_interpolation.py
└── data/
    ├── skipped_yields.csv
    └── visualizations/
```

---

### ⚙️ Instalação
Requisitos:
- Python >= 3.8

Instale as dependências e o projeto no modo desenvolvimento:
```bash
pip install -e .
```

---

### 🚀 Execução
Execute a análise com:
```bash
python main.py
```

Isso irá:
- Carregar os dados de bonds e curva DI
- Interpolar os yields para tenores padrão
- Calcular os spreads históricos entre cada bond e a curva DI
- Mostrar uma superfície 3D interativa e uma tabela-resumo
- Exportar observações ignoradas para `data/skipped_yields.csv`

---

### 🧪 Testes
Execute os testes com `pytest`:
```bash
pytest
```

---

### 🔍 Visualizações
- Gráfico 3D de spreads observados (Plotly Surface)
- Tabela com comparativo de yields (bond x curva interpolada)

---

### 📦 Build e Metadados
Veja `pyproject.toml` para detalhes de empacotamento e configuração do projeto.

---

### 🧹 Arquivos Ignorados
O projeto inclui `.gitignore` para evitar versionamento de:
- Dados de saída (`data/`)
- Ambientes virtuais e caches
- Artefatos de build e IDEs

---

### 👨‍💻 Autor
Thiago Siqueira – [tsiqueira@hotmail.com](mailto:tsiqueira@hotmail.com)

Para dúvidas ou contribuições, fique à vontade para abrir uma issue ou entrar em contato.

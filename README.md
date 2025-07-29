

# README 

'''
## 📈 Modelo de Spread para Bonos Corporativos

Proyecto modular para el cálculo y visualización de los spreads entre bonos corporativos brasileños y la curva DI interpolada, utilizando datos históricos punto por punto. Incluye integración con **Flask** para visualizar los resultados en el navegador.

### 📁 Estructura del Proyecto

spread-model/
├── Makefile                     # Atajos para ejecutar, testear e instalar el proyecto
├── WSGI.py                      # Archivo de configuración WSGI para despliegue en PythonAnywhere
├── main.py                      # Genera los datos y visualizaciones
├── app.py                       # Aplicación Flask para visualización web
├── config.py                    # Parámetros globales y rutas
├── pyproject.toml               # Configuración del proyecto Python
├── requirements.txt             # Dependencias
├── .gitignore                   # Archivos ignorados por Git
├── README.md
│
├── src/                         # Código fuente modular (instalado vía setup)
│   ├── calendars/               # Cálculo de fechas hábiles
│   ├── finmath/                 # Funciones financieras
│   ├── utils/                   # I/O, interpolación, gráficos
│   └── core/                    # Cálculo de ventanas y spreads
│
├── datos_y_modelos/            # Archivos de datos (no incluidos si son privados)
│   ├── db/
│   │   ├── ODA_Comdty.xlsx
│   │   ├── bsrch.xlsx
│   │   └── ya.xlsx
│   └── Domestic/
│       └── brazil_domestic_corp_db.xlsx
│
├── static/                      # Gráficos HTML exportados
│   ├── spread_surface.html
│   └── summary_table.html
│
├── templates/                   # Plantillas para Flask
│   ├── index.html
│   ├── spread_iframe.html
│   └── summary_iframe.html
│
├── .github                      # Configuración de integración continua (CI)
│   └── workflows/
│       └── pytest.yml           # Workflow de GitHub Actions para ejecutar pytest automáticamente
│
├── tests/                       # Pruebas unitarias con pytest
└── data/
    ├── skipped_yields.csv       # Observaciones ignoradas
    └── visualizaciones/         # (opcional) salidas adicionales

'''

---

### ⚙️ Instalación
Requisitos:
- Python >= 3.8

Instalar el proyecto en modo desarrollo:
```bash
pip install -e .
```

Instalar también Flask:
```bash
pip install flask
```

---

### 🚀 Ejecución

#### Para generar los datos y los gráficos HTML:
```bash
python main.py
```

Esto generará los archivos:
- `static/spread_surface.html`
- `static/summary_table.html`

#### Para visualizar en el navegador vía Flask:
```bash
python app.py
```
Abrir el navegador en `http://127.0.0.1:5000`

---

### 🧪 Pruebas
Ejecutar pruebas con `pytest`:
```bash
pytest
```

---

### 🔍 Visualizaciones
- Gráfico 3D de spreads observados (Plotly Surface)
- Tabla comparativa de yields (bono vs curva DI interpolada)

---

### 📦 Build y Metadatos
Ver `pyproject.toml` para detalles de empaquetado y configuración del proyecto.

---

### 🧹 Archivos Ignorados
El proyecto incluye `.gitignore` para evitar versionar:
- Datos de salida (`data/`)
- Entornos virtuales y cachés
- Artefactos de build e IDEs

---

### 👨‍💻 Autor
Thiago Siqueira – [tsiqueira@hotmail.com](mailto:tsiqueira@hotmail.com)

Para dudas o contribuciones, no dudes en abrir un issue o ponerte en contacto.
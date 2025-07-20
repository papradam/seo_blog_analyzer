# 🧠 SEO Blog Analyzer

**SEO Blog Analyzer** es una aplicación interactiva desarrollada en Python que permite analizar artículos de blog desde una perspectiva de optimización para motores de búsqueda (SEO). Utiliza procesamiento de lenguaje natural, análisis de legibilidad y visualización de datos para evaluar la calidad editorial de contenidos y generar recomendaciones automáticas de mejora.

## 📌 Objetivo

Proporcionar una herramienta automatizada para analizar artículos web y generar reportes que ayuden a mejorar el posicionamiento orgánico de blogs, con foco en contenidos como los del sitio XP Investimentos.

---

## 🚀 Características principales

- 🧹 Limpieza del contenido HTML (excluye menús, anuncios, navegación).
- 📊 Análisis de legibilidad y nivel educativo requerido.
- 🔎 Identificación de palabras clave y entidades semánticas relevantes.
- 🔁 Detección de bloques repetitivos entre artículos.
- 📈 Visualizaciones gráficas (gráficos, nubes de palabras).
- 📝 Recomendaciones SEO automáticas basadas en análisis lingüístico.

---

## 🛠️ Tecnologías y bibliotecas utilizadas

- [Streamlit](https://streamlit.io) – Interfaz web interactiva  
- [Requests](https://docs.python-requests.org) – Descarga de HTML  
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) – Parsing de HTML  
- [Textstat](https://pypi.org/project/textstat/) – Legibilidad del texto  
- [spaCy](https://spacy.io) – Análisis semántico y entidades  
- [nltk](https://www.nltk.org/) – Procesamiento de texto básico  
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) – Comparación de textos  
- [matplotlib](https://matplotlib.org/) – Visualización gráfica  
- [wordcloud](https://amueller.github.io/word_cloud/) – Nubes de palabras  

---

## 🧩 Estructura del proyecto

seo_blog_analyzer/
│
├── app.py # Archivo principal con la interfaz Streamlit
├── utils/ # Funciones auxiliares (análisis, visualización, scraping)
│ ├── scraper.py
│ ├── analysis.py
│ └── visualizer.py
├── requirements.txt # Dependencias necesarias
└── README.md # Este archivo

yaml
Copiar
Editar

---

## 💻 Instalación

1. Clona este repositorio:

```bash
git clone https://github.com/tu-usuario/seo_blog_analyzer.git
cd seo_blog_analyzer
Crea un entorno virtual (opcional pero recomendado):

bash
Copiar
Editar
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
Instala las dependencias:

bash
Copiar
Editar
pip install -r requirements.txt
🧪 Uso del programa
Ejecuta la aplicación:

bash
Copiar
Editar
streamlit run app.py
Ingresa una URL de blog cuando se te solicite.

Explora el análisis SEO, visualizaciones y recomendaciones directamente en la interfaz web.

## 📌 Ejemplo de funcionalidades
Nivel de legibilidad: Fácil / Medio / Difícil

Palabras clave más frecuentes: investimento, ações, renda fixa

Entidades detectadas: XP Investimentos, CDI, Brasil

Recomendaciones:

Agrega más encabezados H2

Reduce la longitud de los párrafos

Reescribe contenido duplicado

##📋 Notas adicionales
Este proyecto está orientado a fines académicos y puede adaptarse fácilmente para otros blogs o CMS.

El análisis semántico puede ampliarse con modelos de lenguaje más avanzados.

La detección de contenido repetido se basa en similitud textual estructural, no en frases sueltas.

## 📚 Licencia
Este proyecto está bajo la licencia MIT. Libre para uso, modificación y distribución con fines educativos o profesionales.

##  🤝 Créditos
Desarrollado como parte de un proyecto de grado de Paola Andrea Prada Marín para el programa de Máster en Ciencia de Datos, con fines de innovación y automatización de análisis SEO.

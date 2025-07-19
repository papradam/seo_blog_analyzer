import streamlit as st
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import re

st.set_page_config(page_title="Bloque principal por URL", layout="wide")
st.title("🧪 Detección del contenido editorial único y completo")

def es_bloque_editorial(tag) -> bool:
    texto_total = tag.get_text(separator=" ", strip=True)
    if not texto_total or len(texto_total) < 100:
        return False

    num_p = len(tag.find_all('p'))
    num_h = len(tag.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    if (num_p + num_h) < 2:
        return False

    hijos_estructurales = tag.find_all(['div', 'section', 'article', 'main'])
    texto_hijos = " ".join(h.get_text(separator=" ", strip=True) for h in hijos_estructurales)
    len_total = len(texto_total)
    len_hijos = len(texto_hijos)
    if len_total == 0 or (len_hijos / len_total >= 0.8):
        return False

    if len(texto_total) >= 300 or re.search(r'[.!?]', texto_total):
        return True

    palabras = texto_total.split()
    cortas = [w for w in palabras if len(w) < 3]
    return len(cortas) / len(palabras) <= 0.3

def extraer_bloques_editoriales(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.body
        if not body:
            return [], [], []

        # Capturar h1 antes de limpiar
        h1s_originales = [
            h.get_text(separator=" ", strip=True) for h in soup.find_all("h1")
        ]

        for tag in body.find_all(['nav', 'header', 'footer', 'head', 'script', 'style']):
            tag.decompose()

        bloques = []
        h1s_en_bloques = []

        for tag in body.find_all(['div', 'section', 'article', 'main', 'span']):
            if not es_bloque_editorial(tag):
                continue

            texto = tag.get_text(separator="\n", strip=True)
            html = str(tag)

            bloques.append({"texto": texto.strip(), "html": html.strip()})

        # Verificar e insertar h1 si no está incluido
        for h1_tag in soup.find_all("h1"):
            h1_texto = " ".join(h1_tag.get_text(separator=" ", strip=True).split())

            ya_incluido = False
            for b in bloques:
                bloque_soup = BeautifulSoup(b["html"], "html.parser")
                for h1_dentro in bloque_soup.find_all("h1"):
                    texto_dentro = " ".join(h1_dentro.get_text(separator=" ", strip=True).split())
                    if texto_dentro == h1_texto:
                        ya_incluido = True
                        break
                if ya_incluido:
                    break

            if not ya_incluido:
                bloques.insert(0, {
                    "texto": h1_texto,
                    "html": str(h1_tag)
                })

        # Extraer los h1 presentes en los bloques
        for b in bloques:
            bloque_soup = BeautifulSoup(b["html"], "html.parser")
            h1s_en_bloques.extend([
                " ".join(h.get_text(separator=" ", strip=True).split())
                for h in bloque_soup.find_all("h1")
            ])

        return bloques, h1s_originales, h1s_en_bloques
    except:
        return [], [], []

# UI
urls_input = st.text_area("Introduce 3 URLs (una por línea)", height=150)

if st.button("Ejecutar análisis"):
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    if len(urls) != 3:
        st.error("Por favor introduce exactamente 3 URLs.")
    else:
        datos_por_url = {url: extraer_bloques_editoriales(url) for url in urls}

        # Detectar bloques repetidos globalmente
        repetidos_globales = set()
        for i in range(len(urls)):
            for j in range(i + 1, len(urls)):
                for b1 in datos_por_url[urls[i]][0]:
                    for b2 in datos_por_url[urls[j]][0]:
                        if fuzz.token_set_ratio(b1["texto"], b2["texto"]) >= 90:
                            repetidos_globales.add(b1["texto"])
                            repetidos_globales.add(b2["texto"])

        for url in urls:
            bloques, h1s_originales, h1s_en_bloques = datos_por_url[url]
            unicos = [b for b in bloques if b["texto"] not in repetidos_globales]

            st.markdown(f"## 🌐 {url}")

            st.markdown("### 🏷️ `<h1>` encontrados en el HTML original")
            for h1_text in h1s_originales:
                st.markdown(f"- `{h1_text}`")

            st.markdown("### 🧠 `<h1>` detectados dentro del contenido editorial")
            if h1s_en_bloques:
                for h in h1s_en_bloques:
                    st.markdown(f"- `{h}`")
            else:
                st.info("No hay etiquetas `<h1>` en los bloques editoriales.")

            if not unicos:
                st.warning(f"⚠️ No se encontró contenido único en {url}")
                continue

            st.markdown("### ✏️ Contenido único extraído")
            for i, bloque in enumerate(unicos, 1):
                with st.expander(f"📄 Bloque {i} (texto limpio)"):
                    for parrafo in bloque["texto"].split("\n"):
                        if parrafo.strip():
                            st.write(parrafo.strip())

                with st.expander(f"🧩 Bloque {i} (HTML original)"):
                    st.code(bloque["html"], language="html")

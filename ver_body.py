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
            return []

        for tag in body.find_all(['nav', 'header', 'footer', 'head', 'script', 'style']):
            tag.decompose()

        h1_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
        bloques = []

        for tag in body.find_all(['div', 'section', 'article', 'main', 'span']):
            if not es_bloque_editorial(tag):
                continue

            texto = tag.get_text(separator='\n', strip=True)
            html = str(tag)

            if h1_text and h1_text not in texto:
                texto = h1_text + "\n" + texto
                html = f"<h1>{h1_text}</h1>\n" + html

            bloques.append({"texto": texto.strip(), "html": html.strip()})

        return bloques
    except:
        return []

urls_input = st.text_area("Introduce 3 URLs (una por línea)", height=150)

if st.button("Ejecutar análisis"):
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    if len(urls) != 3:
        st.error("Por favor introduce exactamente 3 URLs.")
    else:
        bloques_por_url = {url: extraer_bloques_editoriales(url) for url in urls}

        # Detectar bloques repetidos solo por texto
        repetidos_globales = set()
        for i in range(len(urls)):
            for j in range(i + 1, len(urls)):
                for b1 in bloques_por_url[urls[i]]:
                    for b2 in bloques_por_url[urls[j]]:
                        if fuzz.token_set_ratio(b1["texto"], b2["texto"]) >= 90:
                            repetidos_globales.add(b1["texto"])
                            repetidos_globales.add(b2["texto"])

        # Mostrar bloques únicos en texto y HTML
        for url in urls:
            unicos = [b for b in bloques_por_url[url] if b["texto"] not in repetidos_globales]
            if not unicos:
                st.warning(f"⚠️ No se encontró contenido único en {url}")
                continue

            st.markdown(f"## 🌐 {url}")
            for i, bloque in enumerate(unicos, 1):
                with st.expander(f"📄 Bloque {i} (texto)"):
                    for parrafo in bloque["texto"].split("\n"):
                        if parrafo.strip():
                            st.write(parrafo.strip())

                with st.expander(f"🧩 Bloque {i} (HTML original)"):
                    st.code(bloque["html"], language="html")

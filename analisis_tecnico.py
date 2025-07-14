# analisis_tecnico.py

import requests
from bs4 import BeautifulSoup
import json

def analizar_tecnico(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        meta_description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_description = desc_tag['content'].strip()

        meta_keywords = ""
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_keywords = keywords_tag['content'].strip()

        h1 = ""
        h1_tag = soup.find("h1")
        if h1_tag:
            h1 = h1_tag.get_text(strip=True)

        imagenes = []
        peso_total = 0
        alt_imagenes = []

        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                img_url = requests.compat.urljoin(url, src)
                try:
                    r = requests.head(img_url, timeout=5)
                    size = int(r.headers.get("Content-Length", 0))
                    peso_total += size
                    imagenes.append(img_url)
                except:
                    imagenes.append(img_url)
            if img.get("alt"):
                alt_imagenes.append(img.get("alt"))

        datos_estructurados = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                datos = json.loads(script.string)
                datos_estructurados.append(datos)
            except:
                continue

        return {
            "title": title,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "h1": h1,
            "imagenes": imagenes,
            "peso_total": peso_total,
            "alt_imagenes": alt_imagenes,
            "datos_estructurados": datos_estructurados
        }

    except Exception as e:
        return {"error": str(e)}

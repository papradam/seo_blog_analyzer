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

        # Código de estado, robots y canonical (meta evaluados antes)
        codigo_estado = res.status_code
        robots = ""
        canonicals = []

        robots_tag = soup.find("meta", attrs={"name": "robots"})
        if robots_tag and robots_tag.get("content"):
            robots = robots_tag['content'].strip()

        for link in soup.find_all("link", rel="canonical"):
            href = link.get("href")
            if href:
                canonicals.append(href.strip())

        # Títulos
        titles = [tag.get_text(strip=True) for tag in soup.find_all("title") if tag.get_text(strip=True)]

        # Meta Descriptions
        meta_descriptions = [
            tag['content'].strip()
            for tag in soup.find_all("meta", attrs={"name": "description"})
            if tag.get("content")
        ]

        # Meta Keywords
        meta_keywords = [
            tag['content'].strip()
            for tag in soup.find_all("meta", attrs={"name": "keywords"})
            if tag.get("content")
        ]

        # H1
        h1s = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]

        # Imágenes
        imagenes_info = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "").strip() if img.has_attr("alt") else ""
            peso = 0

            if src:
                img_url = requests.compat.urljoin(url, src)
                try:
                    r = requests.head(img_url, timeout=5)
                    peso = int(r.headers.get("Content-Length", 0))
                except:
                    pass

                imagenes_info.append({
                    "URL": img_url,
                    "ALT": alt,
                    "Peso (bytes)": peso
                })

        # Datos estructurados
        datos_estructurados = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    datos_estructurados.extend(data)
                else:
                    datos_estructurados.append(data)
            except:
                continue

        return {
            "codigo": codigo_estado,
            "robots": robots,
            "canonicals": canonicals,
            "titles": titles,
            "meta_descriptions": meta_descriptions,
            "meta_keywords": meta_keywords,
            "h1s": h1s,
            "imagenes": imagenes_info,
            "datos_estructurados": datos_estructurados
        }

    except Exception as e:
        return {"error": str(e)}

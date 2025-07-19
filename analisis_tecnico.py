# analisis_tecnico.py

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def obtener_robots_y_canonicals(soup):
    robots = ""
    canonicals = []

    robots_tag = soup.find("meta", attrs={"name": "robots"})
    if robots_tag and robots_tag.get("content"):
        robots = robots_tag["content"].strip()

    for link in soup.find_all("link", rel="canonical"):
        href = link.get("href")
        if href:
            canonicals.append(href.strip())

    return robots, canonicals

def obtener_imagenes_info(soup, base_url):
    imagenes_info = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "").strip()
        peso = 0

        if src:
            img_url = urljoin(base_url, src)
            try:
                r = requests.head(img_url, timeout=5)
                peso = int(r.headers.get("Content-Length", 0))
            except Exception:
                peso = -1  # Error al obtener peso

            imagenes_info.append({
                "URL": img_url,
                "ALT": alt,
                "Peso (bytes)": peso
            })
    return imagenes_info

def obtener_datos_estructurados(soup):
    datos = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                datos.extend(data)
            else:
                datos.append(data)
        except Exception:
            continue
    return datos

def analizar_tecnico(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        codigo_estado = res.status_code
        robots, canonicals = obtener_robots_y_canonicals(soup)

        # Título principal desde <title>
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Meta Description
        meta_descriptions = [
            tag.get("content", "").strip()
            for tag in soup.find_all("meta", attrs={"name": "description"})
            if tag.get("content")
        ]

        # Meta Keywords
        meta_keywords = [
            tag.get("content", "").strip()
            for tag in soup.find_all("meta", attrs={"name": "keywords"})
            if tag.get("content")
        ]

        # H1s
        h1s = [
            h.get_text(strip=True)
            for h in soup.find_all("h1")
            if h.get_text(strip=True)
        ]

        # Imágenes y datos estructurados
        imagenes_info = obtener_imagenes_info(soup, url)
        datos_estructurados = obtener_datos_estructurados(soup)

        return {
            "codigo": codigo_estado,
            "robots": robots,
            "canonicals": canonicals,
            "titles": [title] if title else [],
            "meta_descriptions": meta_descriptions,
            "meta_keywords": meta_keywords,
            "h1s": h1s,
            "imagenes": imagenes_info,
            "datos_estructurados": datos_estructurados
        }

    except requests.RequestException as e:
        return {"error": f"Error de conexión: {str(e)}"}
    except Exception as e:
        return {"error": f"Error general: {str(e)}"}

import textstat
import nltk
from nltk.corpus import stopwords
from collections import Counter
from nltk.util import ngrams
import string
from bs4 import BeautifulSoup

nltk.download('stopwords')
stop_words = set(stopwords.words('spanish'))

# ------------------------
# Funciones auxiliares
# ------------------------

def limpiar_texto(texto):
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

def obtener_frases_clave(texto, top_n=10):
    tokens = limpiar_texto(texto).split()
    tokens_filtrados = [w for w in tokens if w not in stop_words and len(w) > 2]

    ngramas = []
    for n in [2, 3]:
        ng = list(ngrams(tokens_filtrados, n))
        frases = [' '.join(tupla) for tupla in ng]
        ngramas.extend(frases)

    frecuencia = Counter(ngramas)
    frases_validas = [(f, c) for f, c in frecuencia.items() if not any(w in stop_words for w in f.split())]
    return Counter(dict(frases_validas)).most_common(top_n)

def traducir_nivel_educativo(textstat_label):
    equivalencias = {
        '5th': 'Primaria media',
        '6th': 'Primaria alta',
        '7th': 'Secundaria baja',
        '8th': 'Secundaria media',
        '9th': 'Secundaria alta',
        '10th': 'Bachillerato',
        '11th': 'Bachillerato',
        '12th': 'Bachillerato',
        'College': 'Universidad',
        'College graduate': 'Profesional',
        '13th': 'Universidad avanzada',
        '14th': 'Universidad avanzada',
        '15th': 'Postgrado'
    }
    for key, val in equivalencias.items():
        if key in textstat_label:
            return val
    return "Desconocido"

def contar_parrafos_contenido(html):
    soup = BeautifulSoup(html, "html.parser")

    def es_parrafo_valido(tag):
        texto = tag.get_text(separator=" ", strip=True)
        palabras = texto.split()
        return len(palabras) >= 5

    parrafos = soup.find_all("p")
    items = soup.find_all("li")

    parrafos_validos = [p for p in parrafos if es_parrafo_valido(p)]
    items_validos = [li for li in items if es_parrafo_valido(li)]

    return len(parrafos_validos) + len(items_validos)

# ------------------------
# Función principal
# ------------------------

def analizar_texto(texto_plano, html):
    resultado = {}

    resultado['indice_legibilidad'] = textstat.flesch_reading_ease(texto_plano)
    nivel_crudo = textstat.text_standard(texto_plano, float_output=False)
    resultado['nivel_educativo'] = traducir_nivel_educativo(nivel_crudo)

    resultado['num_palabras'] = len(texto_plano.split())
    resultado['num_caracteres'] = len(texto_plano)
    resultado['num_parrafos'] = contar_parrafos_contenido(html)

    resultado['palabras_clave'] = obtener_frases_clave(texto_plano)

    return resultado

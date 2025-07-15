import textstat
import nltk
from nltk.corpus import stopwords
from collections import Counter
from nltk.util import ngrams
import string

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

# ------------------------
# Función principal
# ------------------------

def analizar_texto(texto):
    resultado = {}

    resultado['indice_legibilidad'] = textstat.flesch_reading_ease(texto)
    nivel_crudo = textstat.text_standard(texto, float_output=False)
    resultado['nivel_educativo'] = traducir_nivel_educativo(nivel_crudo)

    resultado['num_palabras'] = len(texto.split())
    resultado['num_caracteres'] = len(texto)
    resultado['num_parrafos'] = max(1, texto.count("\n\n") + 1)

    resultado['palabras_clave'] = obtener_frases_clave(texto)

    return resultado

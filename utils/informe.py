# informe.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud


def mostrar_informe_resultados():
    st.title("📊 Informe General del Análisis SEO")

    if not st.session_state.resultados_seo:
        st.warning("Aún no hay análisis de contenido disponibles.")
        return

    # Construir DataFrame base
    datos = []
    palabras_clave_totales = []
    detalle_urls = []

    for url, res in st.session_state.resultados_seo.items():
        datos.append({
            "URL": url,
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"]
        })
        palabras_clave_totales.extend([frase for frase, _ in res["palabras_clave"]])

        detalle_urls.append({
            "URL": url,
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Palabras clave": ", ".join([f"{frase} ({count})" for frase, count in res["palabras_clave"]]) or "-"
        })

    df = pd.DataFrame(datos)

    # Histograma por franjas de número de palabras
    st.markdown("### 📈 Distribución de longitud de contenidos (por franjas)")
    bins = [0, 300, 600, 900, 1200, 1500, 2000, 3000, 5000]
    df["Franja de palabras"] = pd.cut(df["Palabras"], bins)
    conteo_franjas = df["Franja de palabras"].value_counts().sort_index()

    fig1, ax1 = plt.subplots()
    conteo_franjas.plot(kind='bar', ax=ax1, color="#69b3a2")
    ax1.set_xlabel("Franja de palabras")
    ax1.set_ylabel("Número de artículos")
    ax1.set_title("Distribución por franja de longitud")
    st.pyplot(fig1)

    # Métricas promedio generales
    st.markdown("### 🧮 Métricas promedio generales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📖 Legibilidad promedio", f"{df['Legibilidad'].mean():.2f}")
    with col2:
        st.metric("📝 Palabras promedio", f"{df['Palabras'].mean():.0f}")
    with col3:
        st.metric("📄 Párrafos promedio", f"{df['Párrafos'].mean():.0f}")

    # Nivel educativo estimado
    st.markdown("### 🎓 Nivel educativo estimado (conteo)")
    nivel_counts = df["Nivel educativo"].value_counts()
    st.bar_chart(nivel_counts)

    # Palabras clave - Nube de palabras
    st.markdown("### ☁️ Nube de palabras clave")
    if palabras_clave_totales:
        texto_keywords = " ".join(palabras_clave_totales)
        wordcloud = WordCloud(width=800, height=300, background_color="white").generate(texto_keywords)
        fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.info("No se han identificado palabras clave en los análisis.")

    # Detalle por URL en tabla dentro de expander
    st.markdown("### 📄 Detalle por URL")
    with st.expander("Ver tabla completa de análisis por URL"):
        detalle_df = pd.DataFrame(detalle_urls).set_index("URL")
        st.dataframe(detalle_df, use_container_width=True)

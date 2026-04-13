import streamlit as st
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
import os
from backend_recomendador import preparar_backend_desde_csv, recomendar_discos_kpop
from llm_explanations import (generar_explicacion_radar,generar_explicacion_comparativo,generar_explicacion_recomendacion)

# CONFIGURACION GENERAL
st.set_page_config(
    page_title="K-vibe",
    page_icon="assets/icono.png",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Yeseva+One&family=Poppins:wght@400;500;600;700;800&display=swap');

/* Base general */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: #4A6644;
}

/* Fondo general claro */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #F8FAF4 0%, #FCEBF1 100%);
}

/* Fondo principal del contenido */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Header principal */
.main-header {
    text-align: center;
    margin-top: 0.5rem;
    margin-bottom: 2.2rem;
}

.main-title {
    text-align: center;
    font-family: 'Yeseva One', serif;
    font-size: 3.4rem;
    font-weight: 400;
    margin-top: 0.8rem;
    margin-bottom: 0.3rem;
    line-height: 1.15;
}

.title-green {
    color: #4A6644;
}

.title-pink {
    color: #C66F80;
}

.main-subtitle {
    font-family: 'Poppins', sans-serif;
    font-size: 1.05rem;
    font-style: italic;
    color: #4A6644;
    margin-top: 0.4rem;
    margin-bottom: 1.6rem;
    opacity: 0.95;
}

/* Encabezados de sección */
.section-title {
    font-family: 'Yeseva One', serif;
    font-size: 2.15rem;
    font-weight: 400;
    color: #4A6644;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

/* Cajas de secciones */
.inputs-box {
    background: #FCEBF1;
    border: 1px solid #F4C7D0;
    border-radius: 22px;
    padding: 1.3rem 1.3rem 1.5rem 1.3rem;
    margin-bottom: 1.7rem;
    box-shadow: 0 8px 24px rgba(198, 111, 128, 0.08);
}

.profile-box {
    background: #ECE3D2;
    border: 1px solid #D7DAB3;
    border-radius: 22px;
    padding: 1.3rem 1.3rem 1.5rem 1.3rem;
    margin-bottom: 1.7rem;
    box-shadow: 0 8px 24px rgba(159, 170, 116, 0.08);
}

.recs-box {
    background: #F8F6F0;
    border: 1px solid #D7DAB3;
    border-radius: 22px;
    padding: 1.3rem 1.3rem 1.5rem 1.3rem;
    margin-bottom: 1.7rem;
    box-shadow: 0 8px 24px rgba(74, 102, 68, 0.06);
}

/* Texto de resumen */
.resume-text {
    color: #4A6644;
    font-size: 1rem;
    line-height: 1.8;
    margin-bottom: 0.8rem;
}

/* MUST LISTEN */
.must-listen {
    font-size: 1.25rem;
    font-weight: 800;
    color: #C66F80;
    letter-spacing: 0.4px;
    margin-bottom: 0.5rem;
}

/* Labels */
.meta-label {
    color: #C66F80;
    font-weight: 600;
}

/* Explicación */
.explicacion-text {
    color: #4A6644;
    line-height: 1.75;
}

/* Labels de inputs */
div[data-testid="stTextInput"] label p,
div[data-testid="stTextInput"] label span,
div[data-testid="stTextInput"] label,
div[data-testid="stTextInputRootElement"] label p,
div[data-testid="stTextInputRootElement"] label span,
div[data-testid="stTextInputRootElement"] label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.08rem !important;
    color: #4A6644 !important;
    font-weight: 700 !important;
    letter-spacing: 0.15px !important;
    opacity: 1 !important;
}

/* Inputs */
div[data-baseweb="input"] input {
    font-family: 'Poppins', sans-serif;
    font-size: 1rem;
    color: #4A6644 !important;
    background-color: #FFFDFB !important;
}
div[data-baseweb="input"] input::placeholder {
    color: #9FAA74 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] input::-webkit-input-placeholder {
    color: #9FAA74 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] input::-moz-placeholder {
    color: #9FAA74 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] input:-ms-input-placeholder {
    color: #9FAA74 !important;
    opacity: 1 !important;
}
/* Cajas de input visibles */
div[data-baseweb="input"] > div {
    background-color: #FFFDFB !important;
    border: 1px solid #D7DAB3 !important;
    border-radius: 14px !important;
}

/* Botones primary de Streamlit */
.stButton > button,
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #0f3010 !important;
    color: white !important;
    border-radius: 14px !important;
    border: none !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.15rem !important;
    transition: background-color 0.2s ease, transform 0.2s ease !important;
}

.stButton > button:hover,
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #18481a !important;
    color: white !important;
    transform: translateY(-1px);
}

.stButton > button p,
.stButton > button span,
.stButton > button div,
div[data-testid="stButton"] > button[kind="primary"] p,
div[data-testid="stButton"] > button[kind="primary"] span,
div[data-testid="stButton"] > button[kind="primary"] div {
    color: white !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: white !important;
}

/* Quitar líneas/separadores feos */
hr {
    border: none !important;
    height: 0 !important;
    margin: 0.6rem 0 0.6rem 0 !important;
}

/* Texto general */
p, li, div {
    color: #4A6644;
}

/* Navbar custom resultados: solo botones secondary */
div[data-testid="stButton"] > button[kind="secondary"] {
    min-height: 48px !important;
    border-radius: 14px !important;
    border: none !important;
    background: transparent !important;
    color: transparent !important;
    box-shadow: none !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: transparent !important;
    color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Botón principal generar recomendaciones */
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #18481a !important;
    color: white !important;
    border-radius: 14px !important;
    border: none !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.15rem !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #4a801b !important;
    color: white !important;
}          

/* Botón Spotify */
.spotify-btn {
    display: block;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    padding: 12px 16px;
    border: none;
    border-radius: 12px;
    text-decoration: none !important;
    font-weight: 700;
    color: white !important;
    background-color: #18481a;
    box-shadow: 0 4px 12px rgba(15,48,16,0.18);
    transition: background-color 0.2s ease, transform 0.2s ease;
}
.spotify-btn:hover {
    background-color: #4a801b;
    color: white !important;
    transform: translateY(-1px);
}  

/* Footer */
.app-footer {
    margin-top: 3rem;
    padding-top: 1.2rem;
    padding-bottom: 0.8rem;
    text-align: center;
    border-top: 1px solid #D7DAB3;
    color: #4A6644 !important;
    font-size: 0.95rem;
    line-height: 1.6;
    opacity: 0.95;
}

.app-footer strong {
    color: #4A6644 !important;
    font-weight: 700;
}

.input-card {
    background: #F8F6F0;
    border: 1px solid #D7DAB3;
    border-radius: 20px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 8px 24px rgba(74, 102, 68, 0.06);        
}
.input-card-kicker {
    font-size: 0.88rem;
    font-weight: 700;
    color: #C66F80;
    margin-bottom: 0.35rem;
    letter-spacing: 0.3px;
}
.input-card-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #4A6644;
    margin-bottom: 0.8rem;
    line-height: 1.25;
}

.input-card-meta {
    color: #4A6644;
    margin-bottom: 0.25rem;
    line-height: 1.6;
}            
                                          
</style>
""", unsafe_allow_html=True)


# FUNCIONES DE CARGA
@st.cache_data
def cargar_backend(ruta_csv):
    """
    Carga y prepara todo lo necesario para el backend a partir del CSV.
    """
    df_modelo, anio_min, anio_max, dicc_pesos = preparar_backend_desde_csv(ruta_csv)
    return df_modelo, anio_min, anio_max, dicc_pesos

def formatear_explicacion(texto):
    """
    Mejora visualmente la explicación para mostrarla en la app.
    """
    if not texto:
        return "Sin explicación disponible."

    texto = str(texto).strip()

    # Capitalizar primera letra
    if texto:
        texto = texto[0].upper() + texto[1:]

    # Ajustes de estilo
    texto = texto.replace(". se ", ". Se ")
    texto = texto.replace(". además", ". Además,")
    texto = texto.replace(". y ", ". Y ")
    texto = texto.replace(". funciona ", ". Funciona ")
    texto = texto.replace(". mantiene ", ". Mantiene ")
    texto = texto.replace(". pertenece ", ". Pertenece ")
    texto = texto.replace("Must listen:", "Must listen.")
    texto = texto.replace("..", ".")
    texto = texto.replace(". .", ". ")
    texto = texto.replace("  ", " ")
    
    # Limpiar espacios antes de puntuación
    texto = texto.replace(" .", ".")
    texto = texto.replace(" ,", ",")

    while ".." in texto:
        texto = texto.replace("..", ".")

    # Asegurar punto final
    if texto and texto[-1] not in [".", "!", "?"]:
        texto += "."

    return texto

def construir_resumen_perfiles(perfiles_usuario, perfiles_validos):
    """
    Construye una leyenda simple para explicar al usuario qué inputs sí se encontraron
    y con cuáles se generaron las recomendaciones.
    """
    if not perfiles_usuario:
        return ["No se pudo construir ningún perfil de entrada."]

    lineas = []

    for i, perfil in enumerate(perfiles_usuario, start=1):
        status = perfil.get("discogs_match_status")
        album = perfil.get("input_album", "Desconocido")
        artista = perfil.get("input_artist", "Desconocido")
        anio = perfil.get("discogs_year")
        tags = perfil.get("discogs_tags_norm", [])

        tags_texto = ", ".join(tags[:5]) if isinstance(tags, list) and len(tags) > 0 else "sin tags disponibles"

        if status == "accepted_input":
            linea = (
                f"Álbum {i} encontrado. Los tags principales del álbum "
                f"{album} de {artista}"
            )
            if anio:
                linea += f" del año {anio}"
            linea += f" son: {tags_texto}."
        else:
            linea = f"Álbum {i} no encontrado o no válido para recomendación."

        lineas.append(linea)

    if len(perfiles_usuario) > len(perfiles_validos):
        invalidos = [
            perfil for perfil in perfiles_usuario
            if perfil.get("discogs_match_status") != "accepted_input"
        ]

        if len(invalidos) == 1:
            perfil_invalido = invalidos[0]
            album = perfil_invalido.get("input_album", "Desconocido")
            artista = perfil_invalido.get("input_artist", "Desconocido")
            lineas.append(
                f"No se pudo usar {album} de {artista} como referencia válida, "
                f"así que las recomendaciones se generaron únicamente con el disco válido."
            )
        elif len(invalidos) > 1:
            lineas.append(
                "Uno o más discos no pudieron usarse como referencia válida. "
                "Las recomendaciones se generaron únicamente con los discos válidos."
            )

    return lineas

def ambos_inputs_invalidos(perfiles_usuario):
    """
    Devuelve True si existen dos inputs y ambos quedaron inválidos
    para recomendación (no accepted_input).
    """
    if not isinstance(perfiles_usuario, list) or len(perfiles_usuario) != 2:
        return False

    return all(
        perfil.get("discogs_match_status") != "accepted_input"
        for perfil in perfiles_usuario
    )

def obtener_tags_eje(perfiles_validos, max_tags=6):
    """
    Obtiene los tags más repetidos solo a partir del perfil del usuario.
    Excluye k_pop.
    Si hay dos inputs válidos, los ejes salen de la combinación de ambos.
    """
    tags_excluidos = {"k_pop"}
    contador = Counter()

    for perfil in perfiles_validos:
        for tag in perfil.get("discogs_tags_norm", []):
            if tag not in tags_excluidos:
                contador[tag] += 1

    tags_eje = [tag for tag, _ in contador.most_common(max_tags)]
    return tags_eje

def obtener_tags_eje_comparativo(perfiles_validos, top_5, max_tags=6):
    """
    Obtiene los tags más repetidos combinando perfil usuario + recomendaciones.
    Se usa solo para el gráfico comparativo.
    """
    tags_excluidos = {"k_pop"}
    contador = Counter()

    for perfil in perfiles_validos:
        for tag in perfil.get("discogs_tags_norm", []):
            if tag not in tags_excluidos:
                contador[tag] += 1

    for _, fila in top_5.iterrows():
        for tag in fila.get("discogs_tags_norm", []):
            if tag not in tags_excluidos:
                contador[tag] += 1

    return [tag for tag, _ in contador.most_common(max_tags)]

def calcular_vector_tags_perfiles(perfiles_validos, tags_eje):
    """
    Calcula la presencia promedio de cada tag en los perfiles del usuario.
    Si hay dos inputs, esto representa el promedio de ambos.
    """
    if not perfiles_validos:
        return [0] * len(tags_eje)

    valores = []
    for tag in tags_eje:
        presencia = []
        for perfil in perfiles_validos:
            tags = perfil.get("discogs_tags_norm", [])
            presencia.append(1 if tag in tags else 0)
        valores.append(sum(presencia) / len(presencia))

    return valores

def calcular_vector_tags_perfil_individual(perfil, tags_eje):
    """
    Calcula el vector binario de tags para un único perfil.
    """
    tags = perfil.get("discogs_tags_norm", [])
    return [1 if tag in tags else 0 for tag in tags_eje]

def calcular_vector_tags_recomendaciones(top_5, tags_eje):
    """
    Calcula la presencia promedio de cada tag en las recomendaciones.
    """
    if top_5 is None or len(top_5) == 0:
        return [0] * len(tags_eje)

    valores = []
    for tag in tags_eje:
        presencia = []
        for _, fila in top_5.iterrows():
            tags = fila.get("discogs_tags_norm", [])
            presencia.append(1 if tag in tags else 0)
        valores.append(sum(presencia) / len(presencia))

    return valores

def construir_radar_chart(perfiles_validos, max_tags=6):
    """
    Construye radar chart interactivo con:
    - Álbum 1
    - Álbum 2 (si existe)
    - Perfil promedio
    """
    tags_eje = obtener_tags_eje(perfiles_validos, max_tags=max_tags)

    if len(tags_eje) < 3:
        return None

    fig = go.Figure()

    colores = ["#C66F80", "#9FAA74"]

    for i, perfil in enumerate(perfiles_validos):
        valores_individuales = calcular_vector_tags_perfil_individual(perfil, tags_eje)

        nombre_album = perfil.get("input_album", f"Álbum {i+1}")
        artista = perfil.get("input_artist", "")
        nombre_traza = f"{nombre_album}" if not artista else f"{nombre_album} · {artista}"

        fig.add_trace(go.Scatterpolar(
            r=valores_individuales + [valores_individuales[0]],
            theta=tags_eje + [tags_eje[0]],
            fill='toself',
            name=nombre_traza,
            line=dict(color=colores[i % len(colores)], width=3),
            fillcolor='rgba(198,111,128,0.18)' if i == 0 else 'rgba(159,170,116,0.18)'
        ))

    valores_promedio = calcular_vector_tags_perfiles(perfiles_validos, tags_eje)

    fig.add_trace(go.Scatterpolar(
        r=valores_promedio + [valores_promedio[0]],
        theta=tags_eje + [tags_eje[0]],
        fill='toself',
        name='Perfil promedio',
        line=dict(color='#4A6644', width=3, dash='dash'),
        fillcolor='rgba(74,102,68,0.10)'
    ))

    fig.update_layout(
        title=dict(
            text="Radar de tags principales",
            x=0.02,
            xanchor="left"
        ),
        paper_bgcolor="#F3F5EC",
        plot_bgcolor="#F3F5EC",
        font=dict(color="#18421a", family="Poppins"),
        title_font=dict(color="#18421a", family="Poppins", size=22),
        polar=dict(
            bgcolor="#F3F5EC",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color="#18421a"),
                gridcolor="#D7DAB3",
                linecolor="#D7DAB3"
            ),
            angularaxis=dict(
                tickfont=dict(color="#18421a"),
                gridcolor="#D7DAB3",
                linecolor="#D7DAB3"
            )
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="#18421a", family="Poppins"),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02
        ),
        margin=dict(l=40, r=140, t=70, b=40),
        height=430
    )

    return fig


def construir_df_comparativo_tags(perfiles_validos, top_5, max_tags=6):
    """
    Crea dataframe comparativo usuario vs recomendaciones para bar chart.
    Excluye k_pop.
    """
    tags_eje = obtener_tags_eje_comparativo(perfiles_validos, top_5, max_tags=max_tags)

    if len(tags_eje) == 0:
        return pd.DataFrame()

    valores_usuario = calcular_vector_tags_perfiles(perfiles_validos, tags_eje)
    valores_recs = calcular_vector_tags_recomendaciones(top_5, tags_eje)

    filas = []
    for tag, v_user, v_rec in zip(tags_eje, valores_usuario, valores_recs):
        filas.append({"tag": tag, "grupo": "Perfil usuario", "valor": v_user})
        filas.append({"tag": tag, "grupo": "Recomendaciones", "valor": v_rec})

    return pd.DataFrame(filas)

def construir_df_timeline(perfiles_validos, top_5):
    """
    Construye dataframe para línea de tiempo con:
    - discos input válidos
    - recomendaciones top_5

    Reglas:
    - se ignoran años 0, vacíos o inválidos
    - todos parten de una misma línea temporal
    - se aplica jitter vertical leve cuando comparten año
    - las etiquetas se alternan arriba/abajo
    """
    filas = []

    for perfil in perfiles_validos:
        anio = perfil.get("discogs_year")

        try:
            anio = int(float(anio))
        except Exception:
            continue

        if anio <= 0:
            continue

        filas.append({
            "anio": anio,
            "nombre": perfil.get("input_album"),
            "artista": perfil.get("input_artist"),
            "grupo": "Input usuario"
        })

    if top_5 is not None and len(top_5) > 0:
        for _, fila in top_5.iterrows():
            anio = fila.get("release_year")

            try:
                anio = int(float(anio))
            except Exception:
                continue

            if anio <= 0:
                continue

            filas.append({
                "anio": anio,
                "nombre": fila.get("nombre_album"),
                "artista": fila.get("spotify_artist_name"),
                "grupo": "Recomendación"
            })

    df = pd.DataFrame(filas)

    if df.empty:
        return df

    # Jitter vertical por año
    offsets = [-0.06, 0.06, -0.11, 0.11, -0.16, 0.16]
    y_vals = []
    text_positions = []

    for _, grupo_df in df.groupby("anio", sort=True):
        n = len(grupo_df)

        for i in range(n):
            offset = offsets[i] if i < len(offsets) else 0
            y_vals.append(1 + offset)
            text_positions.append("top center" if i % 2 == 0 else "bottom center")

    df = df.sort_values("anio").copy()
    df["y"] = y_vals
    df["hover_label"] = (
        df["nombre"].fillna("").astype(str)
        + " · "
        + df["artista"].fillna("").astype(str)
        + " · "
        + df["anio"].astype(str)
    )
    return df

def render_card_recomendacion(fila):
    artista = fila.get("spotify_artist_name", "Desconocido")
    explicacion_bonita = formatear_explicacion(fila.get("explicacion", ""))

    card_img, card_info = st.columns([0.9, 1.6], gap="small")

    with card_img:
        if fila.get("album_image_url"):
            st.image(fila["album_image_url"], width=250)

        if fila.get("url_album"):
            st.markdown(
                f"""
                <div style="width: 250px; margin-top: 12px;">
                    <a href="{fila['url_album']}" target="_blank" class="spotify-btn">
                        Escuchar en Spotify
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

    with card_info:
        st.markdown('<div class="top5-card">', unsafe_allow_html=True)

        if fila.get("must_listen"):
            st.markdown('<div class="must-listen">⭐ MUST LISTEN</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size: 1.35rem; font-weight: 700; color: #4A6644; margin-bottom: 0.8rem;">{fila.get("nombre_album", "Álbum sin nombre")}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div><span class="meta-label">Artista:</span> <span style="font-weight: 600;">{artista}</span></div>',
            unsafe_allow_html=True
        )

        if fila.get("release_year"):
            anio = fila["release_year"]
            try:
                anio = int(float(anio))
            except Exception:
                pass

            st.markdown(
                f'<div><span class="meta-label">Año de lanzamiento:</span> <span style="font-weight: 600;">{anio}</span></div>',
                unsafe_allow_html=True
            )

        tags = fila.get("discogs_tags_norm", [])
        tags_texto = ", ".join(tags[:5]) if isinstance(tags, list) and len(tags) > 0 else "Sin tags disponibles"

        st.markdown(
            f'<div><span class="meta-label">Tags principales:</span> <span style="font-weight: 600;">{tags_texto}</span></div>',
            unsafe_allow_html=True
        )

        score = fila.get("score_total_promedio", 0)
        try:
            porcentaje_match = int(round(float(score) * 100))
        except Exception:
            porcentaje_match = 0

        porcentaje_match = max(0, min(100, porcentaje_match))

        st.markdown(
            f'<div><span class="meta-label">Match:</span> <span style="font-weight: 600;">{porcentaje_match}%</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                width: 100%;
                height: 12px;
                background-color: #D7DAB3;
                border-radius: 999px;
                overflow: hidden;
                margin-top: 6px;
                margin-bottom: 14px;
            ">
                <div style="
                    width: {porcentaje_match}%;
                    height: 100%;
                    background-color: #18421a;
                    border-radius: 999px;
                "></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="explicacion-text"><span class="meta-label">Explicación:</span> <span style="font-weight: 600;">{explicacion_bonita}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

def mostrar_loader(personalizado_texto="Generando las mejores recomendaciones k-pop para ti..."):
    st.markdown("""
    <style>
    .custom-loader {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 600;
        color: #4A6644;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .custom-loader-spinner {
        width: 22px;
        height: 22px;
        border: 4px solid #D7DAB3;
        border-top: 4px solid #C66F80;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="custom-loader">
            <div class="custom-loader-spinner"></div>
            <div>{personalizado_texto}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_card_input(perfil, numero_input=1):
    status = perfil.get("discogs_match_status")
    album = perfil.get("input_album", "Desconocido")
    artista = perfil.get("input_artist", "Desconocido")
    anio = perfil.get("discogs_year")
    tags = perfil.get("discogs_tags_norm", [])

    tags_texto = ", ".join(tags[:5]) if isinstance(tags, list) and len(tags) > 0 else "Sin tags disponibles"

    image_url = (
        perfil.get("album_image_url")
        or perfil.get("cover_image")
        or perfil.get("discogs_cover_url")
        or perfil.get("thumb")
    )

    estado_texto = "Validado" if status == "accepted_input" else "No válido"
    estado_color = "#4A6644" if status == "accepted_input" else "#C66F80"

    card_img, card_info = st.columns([0.9, 1.6], gap="small")

    with card_img:
        if image_url:
            st.markdown(
                f"""
                <div style="
                    width:250px;
                    height:250px;
                    border-radius:16px;
                    overflow:hidden;
                    background:#F8F6F0;
                    border:1px solid #D7DAB3;
                ">
                    <img src="{image_url}" style="
                        width:100%;
                        height:100%;
                        object-fit:cover;
                        display:block;
                    ">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="
                    width:250px;
                    height:250px;
                    border-radius:16px;
                    background:#F8F6F0;
                    border:1px solid #D7DAB3;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#9FAA74;
                    font-weight:600;
                    text-align:center;
                    padding:12px;
                    box-sizing:border-box;
                ">
                    Portada no disponible
                </div>
                """,
                unsafe_allow_html=True
            )

    with card_info:
        st.markdown(
            f'<div style="font-size: 1.05rem; font-weight: 800; color: #C66F80; margin-bottom: 0.6rem;">Input {numero_input}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div style="font-size: 1.35rem; font-weight: 700; color: #4A6644; margin-bottom: 0.8rem;">{album}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div><span class="meta-label">Artista:</span> <span style="font-weight: 600;">{artista}</span></div>',
            unsafe_allow_html=True
        )

        if anio:
            st.markdown(
                f'<div><span class="meta-label">Año:</span> <span style="font-weight: 600;">{anio}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div><span class="meta-label">Estado:</span> <span style="font-weight: 700; color: {estado_color};">{estado_texto}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="explicacion-text"><span class="meta-label">Tags principales:</span> <span style="font-weight: 600;">{tags_texto}</span></div>',
            unsafe_allow_html=True
        )

if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Resumen"

def render_navbar_resultados():
    opciones = ["Resumen", "Perfil", "Recomendaciones", "Timeline"]
    cols = st.columns(len(opciones), gap="small")

    for col, opcion in zip(cols, opciones):
        activo = st.session_state.seccion_activa == opcion
        color_fondo = "#C66F80" if activo else "#4A6644"
        color_borde = "#C66F80" if activo else "#4A6644"
        color_texto = "white"

        with col:
            st.markdown(
                f"""
                <div
                   style="
                       display: block;
                       width: 100%;
                       text-align: center;
                       padding: 0.72rem 0.9rem;
                       border-radius: 14px;
                       background-color: {color_fondo};
                       border: 1px solid {color_borde};
                       color: {color_texto};
                       font-weight: 700;
                       margin-bottom: -3.15rem;
                       position: relative;
                       z-index: 0;
                       user-select: none;
                   ">
                    {opcion}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(" ", key=f"nav_{opcion}", use_container_width=True):
                st.session_state.seccion_activa = opcion
                st.rerun()

# INTERFAZ
col_logo_1, col_logo_2, col_logo_3 = st.columns([1.6, 0.6, 1.4])

with col_logo_2:
    st.image("assets/log.PNG", width=220)

st.markdown(
    """
    <div class="main-header">
        <div class="main-title">
            <span class="title-green">K-vibe</span> <span class="title-pink">Match</span>
        </div>
        <div class="main-subtitle">
            ¡Descubre tu álbum de K-pop a partir de uno o dos de tus discos favoritos!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

RUTA_CSV = "data/df_modelo_final.csv"
TOKEN_DISCOGS = st.secrets.get("TOKEN_DISCOGS", os.getenv("TOKEN_DISCOGS", ""))


st.markdown(
    '<div class="resume-text" style="margin-top: 0.3rem; margin-bottom: 0.8rem;font-weight:600; font-size: 1.08rem;">Introduce 1 o 2 discos que te gusten para descubrir tu perfil musical y recomendaciones similares.</div>',
    unsafe_allow_html=True
)
col1, col2 = st.columns(2)

with col1:
    artista_1 = st.text_input("Artista 1", placeholder="Escribe tu artista #1 (Ej. Taylor Swift)")

with col2:
    album_1 = st.text_input("Álbum 1", placeholder="Escribe tu disco favorito de este artista #1 (Ej. 1989)")


col3, col4 = st.columns(2)

with col3:
    artista_2 = st.text_input("Artista 2 (Opcional)", placeholder="Escribe tu artista #2 (Ej. Demi Lovato)")

with col4:
    album_2 = st.text_input("Álbum 2 (Opcional)", placeholder="Escribe tu disco favorito de este artista (Ej. It's not that deep)")

boton = st.button("Generar recomendaciones",type="primary")

salida_guardada = st.session_state.get("salida_recomendador")
salida = salida_guardada if salida_guardada is not None else None

if not boton and salida is not None:
    pass
# EJECUCION
if boton:
    if not artista_1.strip() or not album_1.strip():
        st.error("El input 1 es obligatorio.")
        st.stop()

    artista_2_final = artista_2.strip() if artista_2.strip() else None
    album_2_final = album_2.strip() if album_2.strip() else None

    if (artista_2_final and not album_2_final) or (album_2_final and not artista_2_final):
        st.error("Si usas el input 2, debes llenar artista y álbum.")
        st.stop()

    if not TOKEN_DISCOGS:
        st.error("No se encontró un token de Discogs válido.")
        st.stop()

    loader_placeholder = st.empty()

    with loader_placeholder.container():
        mostrar_loader("Generando las mejores recomendaciones k-pop para ti...")

    try:
        df_modelo, anio_min, anio_max, dicc_pesos = cargar_backend(RUTA_CSV)

        salida = recomendar_discos_kpop(
            artista_1=artista_1,
            album_1=album_1,
            artista_2=artista_2_final,
            album_2=album_2_final,
            token_discogs=TOKEN_DISCOGS,
            anio_min=anio_min,
            anio_max=anio_max,
            df_modelo=df_modelo,
            dicc_pesos=dicc_pesos
        )

    except Exception as e:
        loader_placeholder.empty()
        st.error(f"Ocurrió un error al generar las recomendaciones: {e}")
        st.stop()
    finally:
        pass

    if not isinstance(salida, dict):
        st.error(f"La salida del recomendador no es válida: {type(salida)}")
        st.stop()

    claves_requeridas = ["status", "mensaje", "perfiles_usuario", "perfiles_validos", "recomendaciones"]
    faltantes = [clave for clave in claves_requeridas if clave not in salida]

    if faltantes:
        st.error(f"La salida del recomendador está incompleta. Faltan claves: {faltantes}")
        st.stop()

    # =========================
    # GENERAR EXPLICACIONES LLM
    # =========================
    try:
        perfiles_validos = salida.get("perfiles_validos", [])
        recomendaciones = salida.get("recomendaciones")

        tags_excluir_llm = {"k_pop", "kpop", "k_rock", "krock"}

        tags_input_1 = []
        tags_input_2 = []

        if len(perfiles_validos) >= 1:
            tags_input_1 = [
                t for t in perfiles_validos[0].get("discogs_tags_norm", [])
                if t not in tags_excluir_llm
            ][:5]

        if len(perfiles_validos) >= 2:
            tags_input_2 = [
                t for t in perfiles_validos[1].get("discogs_tags_norm", [])
                if t not in tags_excluir_llm
            ][:5]

        tags_promedio = []
        for perfil in perfiles_validos:
            tags_promedio.extend([
                t for t in perfil.get("discogs_tags_norm", [])
                if t not in tags_excluir_llm
            ])

        tags_promedio = list(dict.fromkeys(tags_promedio))[:6]

        tags_compartidos = []
        if len(perfiles_validos) >= 2:
            set_1 = set(tags_input_1)
            set_2 = set(tags_input_2)
            tags_compartidos = list(set_1 & set_2)[:4]

        explicacion_radar = generar_explicacion_radar(
            tags_input_1,
            tags_input_2,
            tags_compartidos,
            tags_promedio
        )

        tags_recs = []
        if recomendaciones is not None and len(recomendaciones) > 0:
            for _, fila in recomendaciones.iterrows():
                tags_recs.extend(fila.get("discogs_tags_norm", []))
        tags_recs = list(set(tags_recs))[:6]

        explicacion_comparativo = generar_explicacion_comparativo(tags_promedio, tags_recs)

        salida["explicaciones_graficas"] = {
            "radar": explicacion_radar,
            "comparativo": explicacion_comparativo
        }

        if recomendaciones is not None and len(recomendaciones) > 0:
            for idx, fila in recomendaciones.iterrows():
                album = fila.get("nombre_album", "")
                artist = fila.get("spotify_artist_name", "")
                tags_album = fila.get("discogs_tags_norm", [])

                shared_tags = list(set(tags_album) & set(tags_promedio))[:3]
                otros_tags = []
                for jdx, otra_fila in recomendaciones.iterrows():
                    if jdx != idx:
                        otros_tags.extend(otra_fila.get("discogs_tags_norm", []))

                otros_tags = set(otros_tags)
                distinct_tags = [t for t in tags_album if t not in otros_tags and t not in shared_tags][:2]

                explicacion = generar_explicacion_recomendacion(
                    album,
                    artist,
                    shared_tags,
                    distinct_tags
                )

                salida["recomendaciones"].at[idx, "explicacion"] = explicacion

    except Exception as e:
        st.error(f"Error generando explicaciones LLM: {e}")
    loader_placeholder.empty()
    st.session_state["salida_recomendador"] = salida

    if salida["status"] != "ok":
        if ambos_inputs_invalidos(salida.get("perfiles_usuario", [])):
            st.error("Lo siento, ninguno de los dos discos pudo validarse. Revisa artista y/o álbum e inténtalo de nuevo.")
        else:
            st.error(salida["mensaje"])
        st.stop()   

#SACAR
salida = st.session_state.get("salida_recomendador")

if salida is not None:
    st.success("Listo. Analizamos tus discos y generamos tu perfil musical junto con recomendaciones personalizadas.")
    st.markdown(
        '<div class="resume-text" style="margin-bottom: 0.8rem; font-weight: 600;">Haz clic en cada sección para explorar tus resultados.</div>',
        unsafe_allow_html=True
    )   
    render_navbar_resultados()

    if st.session_state.seccion_activa == "Resumen":
        st.markdown('<div class="section-title">Resumen de inputs</div>', unsafe_allow_html=True)

        perfiles_usuario = salida.get("perfiles_usuario", [])

        if perfiles_usuario:
            for i in range(0, len(perfiles_usuario), 2):
                col_izq, col_der = st.columns(2, gap="medium")
                grupo = perfiles_usuario[i:i+2]

                for j, (col, perfil) in enumerate(zip([col_izq, col_der], grupo), start=i+1):
                    with col:
                        render_card_input(perfil, numero_input=j)

                if i + 2 < len(perfiles_usuario):
                    st.write("---")
                    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        else:
            st.info("No se encontraron inputs para mostrar.")


    if st.session_state.seccion_activa == "Perfil":
        # PERFIL DEL USUARIO
        st.markdown('<div class="section-title">Perfil del usuario detectado</div>', unsafe_allow_html=True)

        fig_radar = construir_radar_chart(
            salida["perfiles_validos"],
            max_tags=6
        )

        df_tags_comp = construir_df_comparativo_tags(
            salida["perfiles_validos"],
            salida["recomendaciones"],
            max_tags=6
        )

        col_graf_1, col_graf_2 = st.columns(2, gap="large")

        with col_graf_1:
            if fig_radar is not None:
                st.markdown(
                    '<div class="resume-text" style="margin-bottom: 0.45rem;font-weight:600;">Cada línea representa uno de tus discos y la línea punteada muestra el perfil final detectado.</div>',
                    unsafe_allow_html=True
                )
                st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")
                st.markdown(
                        f'<div class="resume-text">{salida.get("explicaciones_graficas", {}).get("radar", "Aquí se resume cómo los discos ingresados construyen tu perfil musical detectado.")}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("No hubo suficientes tags para construir el radar.")

        with col_graf_2:
            if not df_tags_comp.empty:
                fig_tags = px.bar(
                    df_tags_comp,
                    x="valor",
                    y="tag",
                    color="grupo",
                    barmode="group",
                    orientation="h",
                    title="Comparación de tags: usuario vs recomendaciones",
                    color_discrete_map={
                        "Perfil usuario": "#C66F80",
                        "Recomendaciones": "#4A6644"
                    }
                )

                fig_tags.update_layout(
                    paper_bgcolor="#F3F5EC",
                    plot_bgcolor="#F3F5EC",
                    font=dict(color="#18421a", family="Poppins"),
                    title_font=dict(color="#18421a", family="Poppins", size=22),
                    yaxis_title="",
                    xaxis_title="Presencia promedio",
                    height=430,
                    legend_title_text="",
                    legend=dict(
                        font=dict(color="#18421a", family="Poppins"),
                        yanchor="top",
                        y=0.98,
                        xanchor="left",
                        x=1.02
                    ),
                    margin=dict(l=20, r=120, t=60, b=40)
                )

                fig_tags.update_xaxes(
                    gridcolor="#D7DAB3",
                    zerolinecolor="#D7DAB3",
                    tickfont=dict(color="#18421a"),
                    title_font=dict(color="#18421a")
                )
                fig_tags.update_yaxes(
                    gridcolor="#D7DAB3",
                    tickfont=dict(color="#18421a"),
                    title_font=dict(color="#18421a")
                )
                st.markdown(
                    '<div class="resume-text" style="margin-bottom: 0.45rem;font-weight:600;">Estas barras muestran qué rasgos de tu perfil también aparecen en las recomendaciones con mejor match.</div>',
                    unsafe_allow_html=True
                )
                st.plotly_chart(fig_tags, use_container_width=True, key="bar_tags_chart")
                st.markdown(
                    f'<div class="resume-text">{salida.get("explicaciones_graficas", {}).get("comparativo", "Aquí se explica de forma sencilla qué rasgos de tu perfil también aparecen en las recomendaciones con mejor match.")}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("No hubo suficientes datos para construir la comparación de tags.")

    if st.session_state.seccion_activa == "Recomendaciones":
        # =========================
        # TOP 5 RECOMENDACIONES
        # =========================
        st.markdown('<div class="section-title">Top 5 recomendaciones k-pop</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="resume-text">* El porcentaje de match indica qué tan parecido es cada álbum a tu perfil musical detectado.</div>',
            unsafe_allow_html=True
        )
        top_5 = salida["recomendaciones"].copy()
        top_5 = top_5.sort_values(
            by=["must_listen", "score_total_promedio"],
            ascending=[False, False]
        ).reset_index(drop=True)

        for i in range(0, len(top_5), 2):
            fila_izq, fila_der = st.columns(2, gap="medium")
            grupo = top_5.iloc[i:i+2].to_dict("records")

            for col, fila in zip([fila_izq, fila_der], grupo):
                with col:
                    render_card_recomendacion(fila)

            st.write("---")
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    if st.session_state.seccion_activa == "Timeline":
        # =========================
        # LÍNEA DE TIEMPO
        # =========================
        st.markdown('<div class="section-title">Estas recomendaciones en el tiempo</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="resume-text">Si ubicamos tus discos de referencia y las recomendaciones generadas en una línea temporal, esta sería su distribución.</div>',
            unsafe_allow_html=True
        )

        df_timeline = construir_df_timeline(
            salida["perfiles_validos"],
            salida["recomendaciones"]
        )

        def partir_titulo(texto, max_chars_linea=18):
            palabras = texto.split()
            lineas = []
            linea_actual = ""

            for palabra in palabras:
                test = f"{linea_actual} {palabra}".strip()
                if len(test) <= max_chars_linea:
                    linea_actual = test
                else:
                    if linea_actual:
                        lineas.append(linea_actual)
                    linea_actual = palabra

            if linea_actual:
                lineas.append(linea_actual)

            return lineas[:2]

        if not df_timeline.empty:
            # Parámetros del SVG
            SVG_W = 900
            SVG_H = 420
            YEAR_MIN = df_timeline["anio"].min() - 3
            YEAR_MAX = df_timeline["anio"].max() + 3
            X_LEFT = 70
            X_RIGHT = SVG_W - 50
            AXIS_Y = 210

            def year_to_x(year):
                return X_LEFT + (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN) * (X_RIGHT - X_LEFT)

            # Separar grupos
            inputs = df_timeline[df_timeline["grupo"] == "Input usuario"].to_dict("records")
            recs   = df_timeline[df_timeline["grupo"] == "Recomendación"].to_dict("records")

            COLOR_INPUT = "#C66F80"
            COLOR_REC   = "#4A6644"
            FONT        = "Poppins, sans-serif"

            lines = []

            # ── Eje ──────────────────────────────────────────────────────────
            lines.append(
                f'<line x1="{X_LEFT}" y1="{AXIS_Y}" x2="{X_RIGHT}" y2="{AXIS_Y}" '
                f'stroke="#D7DAB3" stroke-width="2" stroke-linecap="round"/>'
            )

            # Ticks de año
            ticks = sorted(set(
                list(range((YEAR_MIN // 10 + 1) * 10, YEAR_MAX + 1, 10)) + [2015, 2025]
            ))

            for yr in ticks:
                if YEAR_MIN <= yr <= YEAR_MAX:
                    x = year_to_x(yr)
                    lines.append(
                        f'<line x1="{x:.1f}" y1="{AXIS_Y - 5}" x2="{x:.1f}" y2="{AXIS_Y + 10}" '
                        f'stroke="#D7DAB3" stroke-width="1.5"/>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{AXIS_Y + 26}" text-anchor="middle" '
                        f'font-size="9" font-weight="600" fill="#18421a" opacity="0.75" font-family="{FONT}">{yr}</text>'
                    )
            def partir_en_dos_lineas(texto, max_palabras_linea=4):
                palabras = texto.split()
                if len(palabras) <= max_palabras_linea:
                    return [texto]

                linea1 = " ".join(palabras[:max_palabras_linea])
                linea2 = " ".join(palabras[max_palabras_linea:])
                return [linea1, linea2]

            # ── Inputs (arriba del eje) ──────────────────────────────────────
            # Escalonar verticalmente para evitar solapamientos
            inputs_sorted = sorted(inputs, key=lambda r: r["anio"])
            label_h = 28   # alto de la tarjeta
            label_w = 90  # ancho estimado
            tip_offsets = []  # (x, tip_y) ya usados

            for i, row in enumerate(inputs_sorted):
                x = year_to_x(row["anio"])
                # Alternar alturas para evitar colisiones
                base_tip = AXIS_Y - 50 - (i % 3) * 48
                tip_y = base_tip
                box_y = tip_y - label_h - 4
                bx = x - label_w / 2

                nombre_completo = row.get("nombre", "")[:40]
                nombre_lineas = partir_titulo(nombre_completo, max_chars_linea=16)
                artista = row.get("artista", "")[:18]
                anio = int(row["anio"])

                box_h = 30 if len(nombre_lineas) == 1 else 36

                lines.append(
                    f'<line x1="{x:.1f}" y1="{AXIS_Y}" x2="{x:.1f}" y2="{tip_y:.1f}" '
                    f'stroke="{COLOR_INPUT}" stroke-width="1.1" stroke-dasharray="4 4" opacity="0.55"/>'
                )
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{AXIS_Y}" r="6" fill="{COLOR_INPUT}"/>'
                )
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{AXIS_Y}" r="3" fill="white" opacity="0.6"/>'
                )
                lines.append(
                    f'<rect x="{bx:.1f}" y="{box_y:.1f}" width="{label_w}" height="{box_h}" '
                    f'rx="6" fill="{COLOR_INPUT}" opacity="0.10"/>'
                )
                lines.append(
                    f'<rect x="{bx:.1f}" y="{box_y:.1f}" width="{label_w}" height="{box_h}" '
                    f'rx="6" fill="none" stroke="{COLOR_INPUT}" stroke-width="0.8"/>'
                )
                if len(nombre_lineas) == 1:
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 12:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="8" font-weight="600" fill="{COLOR_INPUT}" font-family="{FONT}">{nombre_lineas[0]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 21:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="6.8" fill="{COLOR_INPUT}" opacity="0.85" font-family="{FONT}">{artista} · {anio}</text>'
                    )
                else:
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 12.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="7.8" font-weight="600" fill="{COLOR_INPUT}" font-family="{FONT}">{nombre_lineas[0]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 20.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="7.8" font-weight="600" fill="{COLOR_INPUT}" font-family="{FONT}">{nombre_lineas[1]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 29.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="6.6" fill="{COLOR_INPUT}" opacity="0.85" font-family="{FONT}">{artista} · {anio}</text>'
                    )
            

            # ── Recomendaciones (debajo del eje) ─────────────────────────────
            recs_sorted = sorted(recs, key=lambda r: r["anio"])

            for i, row in enumerate(recs_sorted):
                x = year_to_x(row["anio"])
                base_tip = AXIS_Y + 50 + (i % 3) * 48
                tip_y = base_tip
                box_y = tip_y + 4
                bx = x - label_w / 2

                nombre_completo = row.get("nombre", "")[:40]
                nombre_lineas = partir_titulo(nombre_completo, max_chars_linea=18)
                artista = row.get("artista", "")[:18]
                anio = int(row["anio"])

                box_h = 30 if len(nombre_lineas) == 1 else 44

                lines.append(
                    f'<line x1="{x:.1f}" y1="{AXIS_Y}" x2="{x:.1f}" y2="{tip_y:.1f}" '
                    f'stroke="{COLOR_REC}" stroke-width="1.1" stroke-dasharray="4 4" opacity="0.55"/>'
                )
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{AXIS_Y}" r="6" fill="{COLOR_REC}"/>'
                )
                lines.append(
                    f'<circle cx="{x:.1f}" cy="{AXIS_Y}" r="3" fill="white" opacity="0.6"/>'
                )
                lines.append(
                    f'<rect x="{bx:.1f}" y="{box_y:.1f}" width="{label_w}" height="{box_h}" '
                    f'rx="6" fill="{COLOR_REC}" opacity="0.10"/>'
                )
                lines.append(
                    f'<rect x="{bx:.1f}" y="{box_y:.1f}" width="{label_w}" height="{box_h}" '
                    f'rx="6" fill="none" stroke="{COLOR_REC}" stroke-width="0.8"/>'
                )
                if len(nombre_lineas) == 1:
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 12:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="8" font-weight="600" fill="{COLOR_REC}" font-family="{FONT}">{nombre_lineas[0]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 21:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="6.8" fill="{COLOR_REC}" opacity="0.85" font-family="{FONT}">{artista} · {anio}</text>'
                    )
                else:
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 12.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="7.8" font-weight="600" fill="{COLOR_REC}" font-family="{FONT}">{nombre_lineas[0]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 20.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="7.8" font-weight="600" fill="{COLOR_REC}" font-family="{FONT}">{nombre_lineas[1]}</text>'
                    )
                    lines.append(
                        f'<text x="{x:.1f}" y="{box_y + 29.5:.1f}" text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="6.6" fill="{COLOR_REC}" opacity="0.85" font-family="{FONT}">{artista} · {anio}</text>'
                    )
            

            # ── Leyenda ───────────────────────────────────────────────────────
            lines.append(
                f'<circle cx="55" cy="18" r="6" fill="{COLOR_INPUT}"/>'
            )
            lines.append(
                f'<text x="67" y="22" font-size="7" fill="#18421a" font-family="{FONT}">Input usuario</text>'
            )
            lines.append(
                f'<circle cx="175" cy="18" r="6" fill="{COLOR_REC}"/>'
            )
            lines.append(
                f'<text x="187" y="22" font-size="7" fill="#18421a" font-family="{FONT}">Recomendación</text>'
            )

            svg_body = "\n".join(lines)
            svg = f"""
            <svg xmlns="http://www.w3.org/2000/svg"
                width="100%" viewBox="0 0 {SVG_W} {SVG_H}"
                style="background:#F3F5EC; border-radius:12px; padding:8px;">
            {svg_body}
            </svg>
            """

            st.markdown(svg, unsafe_allow_html=True)

        else:
            st.info("No hubo suficientes años válidos para construir la línea de tiempo.")

st.markdown(
    """
    <div class="app-footer">
        <strong>K-vibe Match</strong><br>
        Descubre tu álbum ideal de K-pop a partir de tus discos favoritos.<br>
        Proyecto académico · Bethsua Lizbeth Beltrán Aguilar · 2026
    </div>
    """,
    unsafe_allow_html=True
)

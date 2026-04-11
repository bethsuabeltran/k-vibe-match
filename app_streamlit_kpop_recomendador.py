import streamlit as st
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

from backend_recomendador import preparar_backend_desde_csv, recomendar_discos_kpop

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

/* Botón principal de generar */
.stButton > button {
    background-color: #0f3010 !important;
    color: white !important;
    border-radius: 14px;
    border: none !important;
    font-weight: 700;
    padding: 0.65rem 1.15rem;
}

.stButton > button:hover {
    background-color: #18481a !important;
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
</style>
""", unsafe_allow_html=True)

# CONFIGURACION GENERAL
st.set_page_config(
    page_title="K-vibe",
    page_icon="assets/icono.png",
    layout="wide"
)

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
    Construye radar chart solo del perfil del usuario.
    Si hay dos inputs válidos, representa el promedio de ambos.
    """
    tags_eje = obtener_tags_eje(perfiles_validos, max_tags=max_tags)

    if len(tags_eje) < 3:
        return None

    valores_usuario = calcular_vector_tags_perfiles(perfiles_validos, tags_eje)

    tags_plot = tags_eje + [tags_eje[0]]
    valores_usuario_plot = valores_usuario + [valores_usuario[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores_usuario_plot,
        theta=tags_plot,
        fill='toself',
        name='Perfil usuario',
        line=dict(color='#C66F80', width=3),
        fillcolor='rgba(198,111,128,0.30)'
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
        showlegend=False,
        margin=dict(l=40, r=40, t=70, b=40),
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
    """
    filas = []

    for perfil in perfiles_validos:
        anio = perfil.get("discogs_year")
        if pd.notna(anio):
            filas.append({
                "anio": int(anio),
                "nombre": perfil.get("input_album"),
                "artista": perfil.get("input_artist"),
                "grupo": "Input usuario"
            })

    if top_5 is not None and len(top_5) > 0:
        for _, fila in top_5.iterrows():
            anio = fila.get("release_year")
            if pd.notna(anio):
                try:
                    anio = int(float(anio))
                except Exception:
                    continue

                filas.append({
                    "anio": anio,
                    "nombre": fila.get("nombre_album"),
                    "artista": fila.get("spotify_artist_name"),
                    "grupo": "Recomendación"
                })

    return pd.DataFrame(filas)

# INTERFAZ
st.image("assets/log.PNG", width=220)

st.markdown(
    '<div class="main-title"><span class="title-green">K-vibe</span> <span class="title-pink">Match</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">¡Descubre tu álbum de K-pop a partir de uno o dos de tus discos favoritos!</div>',
    unsafe_allow_html=True
)

RUTA_CSV = "data/df_modelo_final.csv"
TOKEN_DISCOGS = st.secrets["TOKEN_DISCOGS"]

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

boton = st.button("Generar recomendaciones")



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

    with st.spinner("Generando las mejores recomendaciones k-pop para ti..."):
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

    if salida["status"] != "ok":
        if ambos_inputs_invalidos(salida.get("perfiles_usuario", [])):
            st.error("Lo siento, los dos artistas que introdujiste están mal escritos. Inténtalo de nuevo.")
        else:
            st.error(salida["mensaje"])
        st.stop()

    st.success(salida["mensaje"])

    # RESUMEN DE INPUTS
    st.markdown('<div class="section-title">Resumen de inputs</div>', unsafe_allow_html=True)
    lineas_resumen = construir_resumen_perfiles(
        salida["perfiles_usuario"],
        salida["perfiles_validos"]
    )
    
    for linea in lineas_resumen:
        st.markdown(f'<div class="resume-text">{linea}</div>', unsafe_allow_html=True)


    # PERFIL DEL USUARIO
    st.markdown('<div class="section-title">Perfil del usuario detectado</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="resume-text">A partir de los álbumes introducidos, ¡obtuvimos tu perfil musical!</div>',
        unsafe_allow_html=True
    )

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
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown(
                '<div class="resume-text">Este radar muestra los tags más representativos de tu perfil musical detectado. Si ingresaste dos discos, el gráfico refleja el promedio entre ambos.</div>',
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

            st.plotly_chart(fig_tags, use_container_width=True)
            st.markdown(
                '<div class="resume-text">Aquí puedes comparar qué tan bien reflejan las recomendaciones los tags más representativos de tu perfil musical.</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("No hubo suficientes datos para construir la comparación de tags.")

    # =========================
    # TOP 5 RECOMENDACIONES
    # =========================
    st.markdown('<div class="section-title">Top 5 recomendaciones</div>', unsafe_allow_html=True)

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
                                <a href="{fila['url_album']}" target="_blank"
                                    style="
                                        display: block;
                                        width: 100%;
                                        box-sizing: border-box;
                                        text-align: center;
                                        padding: 12px 16px;
                                        border: none;
                                        border-radius: 12px;
                                        text-decoration: none;
                                        font-weight: 700;
                                        color: white;
                                        background-color: #18421a;
                                        box-shadow: 0 4px 12px rgba(15,48,16,0.18);
                                    ">
                                    Escuchar en Spotify
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                with card_info:
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

        st.write("---")
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

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

    if not df_timeline.empty:
        fig_timeline = px.scatter(
            df_timeline,
            x="anio",
            y="grupo",
            color="grupo",
            hover_data=["nombre", "artista"],
            color_discrete_map={
                "Input usuario": "#C66F80",
                "Recomendación": "#4A6644"
            },
            title="Ubicación temporal de inputs y recomendaciones"
        )

        fig_timeline.update_traces(marker=dict(size=14))

        fig_timeline.update_layout(
            paper_bgcolor="#F3F5EC",
            plot_bgcolor="#F3F5EC",
            font=dict(color="#18421a", family="Poppins"),
            title_font=dict(color="#18421a", family="Poppins", size=22),
            yaxis_title="",
            xaxis_title="Año",
            height=380,
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

        fig_timeline.update_xaxes(
            gridcolor="#D7DAB3",
            zerolinecolor="#D7DAB3",
            tickfont=dict(color="#18421a"),
            title_font=dict(color="#18421a")
        )
        fig_timeline.update_yaxes(
            gridcolor="#D7DAB3",
            tickfont=dict(color="#18421a"),
            title_font=dict(color="#18421a")
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No hubo suficientes años válidos para construir la línea de tiempo.")

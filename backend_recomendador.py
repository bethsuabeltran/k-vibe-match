
#Imports
import ast
import re
import time
import unicodedata
from collections import Counter
import pandas as pd
import requests
import random
from difflib import SequenceMatcher

#Constantes
COLUMNAS_LISTA = ["discogs_genres_norm","discogs_styles_norm","discogs_tags_norm","tags_dominantes","tags_especificos",]

#Utilidades generales
def normalizar_texto(texto):
    """
    Normaliza texto:
    - minúsculas
    - sin acentos
    - elimina signos de puntuación comunes
    - sin espacios extra
    """
    if pd.isna(texto):
        return ""

    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[\(\)\[\]\{\}\!\?\,\.\:\;\'\"\-_/]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def parsear_lista(valor):
    """
    Convierte strings tipo "['a', 'b']" en listas reales.
    Si ya es lista, la deja igual.
    Si está vacío o falla, devuelve [].
    """
    if isinstance(valor, list):
        return valor

    if pd.isna(valor):
        return []

    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            return []

        try:
            convertido = ast.literal_eval(valor)
            if isinstance(convertido, list):
                return convertido
            return []
        except Exception:
            return []

    return []

def aplicar_parseo_columnas_lista(df, columnas_lista=COLUMNAS_LISTA):
    """
    Aplica parseo a columnas que deben ser listas.
    """
    df = df.copy()

    for col in columnas_lista:
        if col in df.columns:
            df[col] = df[col].apply(parsear_lista)

    return df

def cargar_df_modelo(ruta_csv):
    """
    Carga el dataset final del modelo y reconstruye columnas lista.
    """
    df = pd.read_csv(ruta_csv)
    df = aplicar_parseo_columnas_lista(df)
    return df

def obtener_rango_anios(df, columna_anio="release_year"):
    """
    Devuelve año mínimo y máximo del dataset.
    """
    anio_min = int(df[columna_anio].min())
    anio_max = int(df[columna_anio].max())
    return anio_min, anio_max

def construir_dicc_pesos_tags(df, columna_tags="discogs_tags_norm"):
    """
    Construye diccionario de pesos de tags a partir de la frecuencia
    observada en el dataset.

    Nota:
    aquí dejamos una versión base. Luego la ajustamos para que copie
    exactamente tu lógica del notebook.
    """
    contador = Counter()

    for lista_tags in df[columna_tags]:
        if isinstance(lista_tags, list):
            contador.update(lista_tags)

    df_frecuencia = pd.DataFrame(
        contador.items(),
        columns=["tag", "frecuencia"]
    ).sort_values("frecuencia", ascending=False)

    total = df_frecuencia["frecuencia"].sum()

    if total == 0:
        return {}

    df_frecuencia["proporcion"] = df_frecuencia["frecuencia"] / total

    # peso inverso simple provisional
    df_frecuencia["peso_tag"] = 1 / (df_frecuencia["proporcion"] + 1e-9)

    dicc_pesos_tags = dict(zip(df_frecuencia["tag"], df_frecuencia["peso_tag"]))
    return dicc_pesos_tags

#Funciones de Discogs
def discogs_get(
    endpoint,
    token_discogs,
    params=None,
    ultima_solicitud=0,
    intervalo_minimo=1.0,
    url_base="https://api.discogs.com"
):
    """
    Hace una solicitud GET a la API de Discogs respetando una pausa mínima
    entre peticiones para evitar errores por rate limit.

    Parámetros:
    - endpoint: ruta de la API o URL completa
    - token_discogs: token personal de Discogs
    - params: parámetros de la consulta
    - ultima_solicitud: timestamp de la última petición
    - intervalo_minimo: tiempo mínimo entre solicitudes
    - url_base: base de la API de Discogs

    Devuelve:
    - json de respuesta
    - headers de la respuesta
    - nuevo timestamp de última solicitud
    """
    ahora = time.time()
    tiempo_espera = ultima_solicitud + intervalo_minimo - ahora

    if tiempo_espera > 0:
        time.sleep(tiempo_espera + random.uniform(0, 0.2))

    url = endpoint if endpoint.startswith("http") else f"{url_base}{endpoint}"

    headers = {
        "Authorization": f"Discogs token={token_discogs}",
        "User-Agent": "kpop-recomendador/1.0"
    }

    respuesta = requests.get(url, headers=headers, params=params, timeout=30)
    nueva_ultima_solicitud = time.time()

    if respuesta.status_code == 429:
        retry_after = respuesta.headers.get("Retry-After")
        espera_segundos = int(retry_after) if retry_after and retry_after.isdigit() else 60

        print(f"429 en Discogs. Esperando {espera_segundos} segundos...")
        time.sleep(espera_segundos + 1)

        return discogs_get(
            endpoint=endpoint,
            token_discogs=token_discogs,
            params=params,
            ultima_solicitud=nueva_ultima_solicitud,
            intervalo_minimo=intervalo_minimo,
            url_base=url_base
        )

    if not respuesta.ok:
        raise requests.HTTPError(
            f"Error en Discogs: {respuesta.status_code} - {respuesta.text}"
        )
    return respuesta.json(), respuesta.headers, nueva_ultima_solicitud

def similarity(a, b):
    """
    Calcula similitud entre dos textos ya normalizados internamente.

    Usa SequenceMatcher y devuelve un valor entre 0 y 1:
    - 1 = textos idénticos
    - 0 = completamente distintos
    """
    return SequenceMatcher(None, normalizar_texto(a), normalizar_texto(b)).ratio()

def separar_titulo_discogs(titulo_resultado):
    """
    Separa títulos de Discogs del formato:
    'Artista - Álbum'

    Devuelve:
    - artista_resultado
    - album_resultado

    Si no encuentra separador, devuelve:
    - artista vacío
    - título completo como álbum
    """
    if not titulo_resultado:
        return "", ""

    partes = str(titulo_resultado).split(" - ", 1)

    if len(partes) == 2:
        return partes[0].strip(), partes[1].strip()

    return "", str(titulo_resultado).strip()

def buscar_release_discogs(
    nombre_artista,
    nombre_album,
    token_discogs,
    anio=None,
    tipo_album=None,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Busca releases en Discogs usando varios intentos de consulta.

    Estrategia:
    1. búsqueda estructurada por artist + release_title
    2. búsqueda por title combinado: 'artista - álbum'
    3. búsqueda libre con q

    Parámetros:
    - nombre_artista: nombre del artista
    - nombre_album: nombre del álbum/disco
    - token_discogs: token personal de Discogs
    - anio: año opcional para afinar la búsqueda
    - tipo_album: parámetro opcional, se conserva por compatibilidad
    - ultima_solicitud: timestamp de última petición
    - intervalo_minimo: pausa mínima entre peticiones

    Devuelve:
    - resultados: lista de resultados
    - headers: headers de la última respuesta
    - params_usados: parámetros de la búsqueda que sí devolvió resultados
    - ultima_solicitud: timestamp actualizado
    """
    intentos_busqueda = []

    # 1. Búsqueda estructurada
    params_1 = {
        "artist": nombre_artista,
        "release_title": nombre_album,
        "type": "release",
        "per_page": 10,
        "page": 1
    }

    if pd.notna(anio):
        params_1["year"] = int(anio)

    intentos_busqueda.append(params_1)

    # 2. Búsqueda por título combinado
    params_2 = {
        "title": f"{nombre_artista} - {nombre_album}",
        "type": "release",
        "per_page": 10,
        "page": 1
    }

    if pd.notna(anio):
        params_2["year"] = int(anio)

    intentos_busqueda.append(params_2)

    # 3. Búsqueda libre
    texto_busqueda = f"{nombre_artista} {nombre_album}"

    if pd.notna(anio):
        texto_busqueda += f" {int(anio)}"

    params_3 = {
        "q": texto_busqueda,
        "type": "release",
        "per_page": 10,
        "page": 1
    }

    intentos_busqueda.append(params_3)

    ultimos_headers = None

    for params in intentos_busqueda:
        datos, headers, ultima_solicitud = discogs_get(
            endpoint="/database/search",
            token_discogs=token_discogs,
            params=params,
            ultima_solicitud=ultima_solicitud,
            intervalo_minimo=intervalo_minimo
        )

        ultimos_headers = headers
        resultados = datos.get("results", [])

        if resultados:
            return resultados, headers, params, ultima_solicitud

    return [], ultimos_headers, None, ultima_solicitud

def puntuar_resultado_discogs(resultado, nombre_artista, nombre_album, anio=None, tipo_album=None):
    """
    Calcula un puntaje de qué tan buen match es un resultado de Discogs
    respecto al artista y disco buscados por el usuario.

    Criterios que usa:
    - similitud del artista
    - similitud del álbum
    - cercanía del año
    - penalización por ruido (DVD, tour, live, etc.)
    - bonus leve por tipo de lanzamiento

    Parámetros:
    - resultado: diccionario individual devuelto por Discogs
    - nombre_artista: artista buscado
    - nombre_album: álbum/disco buscado
    - anio: año esperado opcional
    - tipo_album: tipo esperado opcional ("single" o "album")

    Devuelve:
    - puntaje final entre 0 y 100
    """
    titulo_resultado = resultado.get("title", "")
    artista_resultado, album_resultado = separar_titulo_discogs(titulo_resultado)
    anio_resultado = resultado.get("year")

    texto_titulo = str(titulo_resultado).lower()
    formatos = resultado.get("format", [])
    texto_formatos = " ".join(map(str, formatos)).lower() if isinstance(formatos, list) else str(formatos).lower()

    # Similitud del artista
    similitud_artista = similarity(
        nombre_artista,
        artista_resultado if artista_resultado else titulo_resultado
    ) * 100

    # Similitud del álbum
    similitud_album = similarity(
        nombre_album,
        album_resultado if album_resultado else titulo_resultado
    ) * 100

    puntaje = 0.0

    # Pesos principales
    puntaje += similitud_artista * 0.45
    puntaje += similitud_album * 0.45

    # Bonus o penalización por cercanía del año
    if pd.notna(anio) and pd.notna(anio_resultado):
        try:
            diferencia = abs(int(anio) - int(anio_resultado))

            if diferencia == 0:
                puntaje += 10
            elif diferencia == 1:
                puntaje += 6
            elif diferencia <= 3:
                puntaje += 2
            else:
                puntaje -= 8
        except Exception:
            pass

    # Penalizaciones por resultados ruidosos
    palabras_ruido = [
        "dvd", "blu-ray", "bluray", "world tour", "tour", "live",
        "final in seoul", "unofficial", "japan tour", "concert"
    ]

    for palabra in palabras_ruido:
        if palabra in texto_titulo or palabra in texto_formatos:
            puntaje -= 20

    # Bonus leve por tipo de lanzamiento
    if tipo_album == "single" and "single" in texto_formatos:
        puntaje += 5

    if tipo_album == "album" and ("album" in texto_formatos or "lp" in texto_formatos):
        puntaje += 5

    # Limitar el resultado al rango 0-100
    puntaje = max(0, min(100, puntaje))

    return round(puntaje, 2)

def get_discogs_release_details(
    release_id,
    token_discogs,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Obtiene los detalles completos de un release de Discogs a partir de su release_id.

    Parámetros:
    - release_id: id del release en Discogs
    - token_discogs: token personal de Discogs
    - ultima_solicitud: timestamp de la última petición a Discogs
    - intervalo_minimo: pausa mínima entre solicitudes

    Devuelve:
    - diccionario con metadata del release
    - headers de la respuesta
    - ultima_solicitud actualizada
    """
    if pd.isna(release_id) or release_id is None:
        return {
            "discogs_release_id": None,
            "discogs_title": None,
            "discogs_year": None,
            "discogs_country": None,
            "discogs_genres": None,
            "discogs_styles": None,
            "discogs_labels": None,
            "discogs_thumb": None,
            "discogs_cover_image": None,
            "discogs_album_image_url": None,
            "discogs_error": "release_id vacío"
        }, None, ultima_solicitud

    try:
        datos, headers, ultima_solicitud = discogs_get(
            endpoint=f"/releases/{int(release_id)}",
            token_discogs=token_discogs,
            params=None,
            ultima_solicitud=ultima_solicitud,
            intervalo_minimo=intervalo_minimo
        )

        labels_raw = datos.get("labels", [])
        labels = []

        if isinstance(labels_raw, list):
            for item in labels_raw:
                if isinstance(item, dict):
                    nombre_label = item.get("name")
                    if nombre_label:
                        labels.append(nombre_label)
                elif pd.notna(item):
                    labels.append(str(item))

        return {
            "discogs_release_id": datos.get("id"),
            "discogs_title": datos.get("title"),
            "discogs_year": datos.get("year"),
            "discogs_country": datos.get("country"),
            "discogs_genres": datos.get("genres"),
            "discogs_styles": datos.get("styles"),
            "discogs_labels": labels,
            "discogs_thumb": datos.get("thumb"),
            "discogs_cover_image": datos.get("cover_image"),
            "discogs_album_image_url": (
                datos.get("cover_image")
                or (
                    datos.get("images", [{}])[0].get("uri")
                    if isinstance(datos.get("images"), list) and len(datos.get("images")) > 0
                    else None
                )
                or datos.get("thumb")
            ),
            "discogs_error": None
        }, headers, ultima_solicitud

    except Exception as e:
        return {
            "discogs_release_id": release_id,
            "discogs_title": None,
            "discogs_year": None,
            "discogs_country": None,
            "discogs_genres": None,
            "discogs_styles": None,
            "discogs_labels": None,
            "discogs_thumb": None,
            "discogs_cover_image": None,
            "discogs_album_image_url": None,
            "discogs_error": str(e)
        }, None, ultima_solicitud

def normalizar_lista_tags(lista_tags):
    """
    Normaliza una lista de tags/textos usando la función normalizar_texto.
    Elimina vacíos y duplicados conservando el orden.
    """
    if not isinstance(lista_tags, list):
        return []

    tags_norm = []
    vistos = set()

    for tag in lista_tags:
        tag_norm = normalizar_texto(tag)
        if tag_norm and tag_norm not in vistos:
            tags_norm.append(tag_norm)
            vistos.add(tag_norm)

    return tags_norm


#Funciones de perfil de usuario
def limpiar_texto_input(texto):
    """
    Limpia texto ingresado por el usuario para prepararlo antes de buscar
    en Discogs.

    Por ahora:
    - convierte NaN en string vacío
    - quita espacios al inicio y al final
    """
    if pd.isna(texto):
        return ""

    texto = str(texto).strip()
    return texto

def construir_consulta_usuario(nombre_artista, nombre_album):
    """
    Construye una consulta limpia del usuario a partir del artista y álbum.

    Devuelve un diccionario con:
    - nombre_artista
    - nombre_album
    """
    nombre_artista = limpiar_texto_input(nombre_artista)
    nombre_album = limpiar_texto_input(nombre_album)

    return {
        "nombre_artista": nombre_artista,
        "nombre_album": nombre_album
    }


def buscar_input_usuario_discogs(
    nombre_artista,
    nombre_album,
    token_discogs,
    anio=None,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Busca en Discogs el disco ingresado por el usuario.

    Devuelve:
    - resultados encontrados
    - parámetros de búsqueda usados
    - timestamp actualizado de última solicitud
    """
    resultados, _, busqueda_usada, ultima_solicitud = buscar_release_discogs(
        nombre_artista=nombre_artista,
        nombre_album=nombre_album,
        token_discogs=token_discogs,
        anio=anio,
        tipo_album=None,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )

    return resultados, busqueda_usada, ultima_solicitud

def resolver_mejor_match_usuario(
    nombre_artista,
    nombre_album,
    token_discogs,
    anio=None,
    puntaje_minimo=50,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Encuentra el mejor match en Discogs para el input del usuario.

    Flujo:
    1. busca resultados
    2. puntúa cada candidato
    3. elige el mejor
    4. si el puntaje es bajo, lo marca como manual_review
    5. si el puntaje es suficiente, obtiene detalles completos del release

    Devuelve:
    - diccionario con el mejor resultado resuelto
    - timestamp actualizado de última solicitud
    """
    resultados, busqueda_usada, ultima_solicitud = buscar_input_usuario_discogs(
        nombre_artista=nombre_artista,
        nombre_album=nombre_album,
        token_discogs=token_discogs,
        anio=anio,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )

    if not resultados:
        return {
            "input_artist": nombre_artista,
            "input_album": nombre_album,
            "discogs_match_status": "not_found",
            "discogs_match_score": None,
            "discogs_candidate_title": None,
            "discogs_candidate_id": None,
            "discogs_search_used": str(busqueda_usada),
            "discogs_error": None
        }, ultima_solicitud

    resultados_puntuados = []

    for resultado in resultados:
        puntaje = puntuar_resultado_discogs(
            resultado=resultado,
            nombre_artista=nombre_artista,
            nombre_album=nombre_album,
            anio=anio,
            tipo_album=None
        )
        resultados_puntuados.append((puntaje, resultado))

    resultados_puntuados.sort(key=lambda x: x[0], reverse=True)
    mejor_puntaje, mejor_resultado = resultados_puntuados[0]

    if mejor_puntaje < puntaje_minimo:
        return {
            "input_artist": nombre_artista,
            "input_album": nombre_album,
            "discogs_match_status": "manual_review",
            "discogs_match_score": round(mejor_puntaje, 2),
            "discogs_candidate_title": mejor_resultado.get("title"),
            "discogs_candidate_id": mejor_resultado.get("id"),
            "discogs_search_used": str(busqueda_usada),
            "discogs_error": None
        }, ultima_solicitud

    detalles, _, ultima_solicitud = get_discogs_release_details(
        release_id=mejor_resultado.get("id"),
        token_discogs=token_discogs,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )

    detalles["input_artist"] = nombre_artista
    detalles["input_album"] = nombre_album
    detalles["discogs_match_status"] = "accepted_input"
    detalles["discogs_match_score"] = round(mejor_puntaje, 2)
    detalles["discogs_candidate_title"] = mejor_resultado.get("title")
    detalles["discogs_candidate_id"] = mejor_resultado.get("id")
    detalles["discogs_search_used"] = str(busqueda_usada)
    detalles["discogs_thumb"] = detalles.get("discogs_thumb") or mejor_resultado.get("thumb")
    detalles["discogs_cover_image"] = detalles.get("discogs_cover_image") or mejor_resultado.get("cover_image")
    detalles["discogs_album_image_url"] = (
        detalles.get("discogs_album_image_url")
        or mejor_resultado.get("cover_image")
        or mejor_resultado.get("thumb")
    )

    return detalles, ultima_solicitud

def construir_perfil_input_usuario(
    nombre_artista,
    nombre_album,
    token_discogs,
    anio_min,
    anio_max,
    anio=None,
    puntaje_minimo=50,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Construye el perfil final del input del usuario a partir del mejor match
    encontrado en Discogs.

    El perfil incluye:
    - metadatos del release
    - genres, styles y tags
    - versiones normalizadas
    - año normalizado
    - metadata del match en Discogs
    """
    resultado, ultima_solicitud = resolver_mejor_match_usuario(
        nombre_artista=nombre_artista,
        nombre_album=nombre_album,
        token_discogs=token_discogs,
        anio=anio,
        puntaje_minimo=puntaje_minimo,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )

    genres = resultado.get("discogs_genres")
    styles = resultado.get("discogs_styles")

    if not isinstance(genres, list):
        genres = []

    if not isinstance(styles, list):
        styles = []

    tags = list(dict.fromkeys(genres + styles))

    genres_norm = normalizar_lista_tags(genres)
    styles_norm = normalizar_lista_tags(styles)
    tags_norm = normalizar_lista_tags(tags)

    release_year_input = resultado.get("discogs_year")

    if pd.notna(release_year_input) and (anio_max - anio_min) != 0:
        release_year_norm_input = round(
            (float(release_year_input) - anio_min) / (anio_max - anio_min),
            4
        )
    else:
        release_year_norm_input = None

    perfil = {
        "input_artist": resultado.get("input_artist"),
        "input_album": resultado.get("input_album"),
        "discogs_title": resultado.get("discogs_title"),
        "discogs_year": release_year_input,
        "discogs_year_norm": release_year_norm_input,
        "discogs_genres": genres,
        "discogs_styles": styles,
        "discogs_tags": tags,
        "discogs_genres_norm": genres_norm,
        "discogs_styles_norm": styles_norm,
        "discogs_tags_norm": tags_norm,
        "album_image_url": resultado.get("discogs_album_image_url"),
        "discogs_thumb": resultado.get("discogs_thumb"),
        "discogs_cover_image": resultado.get("discogs_cover_image"),
        "discogs_match_status": resultado.get("discogs_match_status"),
        "discogs_match_score": resultado.get("discogs_match_score"),
        "discogs_candidate_title": resultado.get("discogs_candidate_title"),
        "discogs_candidate_id": resultado.get("discogs_candidate_id"),
        "discogs_search_used": resultado.get("discogs_search_used"),
        "discogs_error": resultado.get("discogs_error")
    }

    return perfil, ultima_solicitud

def construir_perfiles_usuario(
    artista_1,
    album_1,
    token_discogs,
    anio_min,
    anio_max,
    artista_2=None,
    album_2=None,
    puntaje_minimo=50,
    ultima_solicitud=0,
    intervalo_minimo=1.0
):
    """
    Construye uno o dos perfiles de usuario a partir de los discos ingresados.

    Parámetros:
    - artista_1, album_1: input obligatorio
    - artista_2, album_2: input opcional
    - token_discogs: token de Discogs
    - anio_min, anio_max: rango de años del dataset del modelo

    Devuelve:
    - lista de perfiles
    - timestamp actualizado de última solicitud
    """
    perfiles = []

    perfil_1, ultima_solicitud = construir_perfil_input_usuario(
        nombre_artista=artista_1,
        nombre_album=album_1,
        token_discogs=token_discogs,
        anio_min=anio_min,
        anio_max=anio_max,
        puntaje_minimo=puntaje_minimo,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )
    perfiles.append(perfil_1)

    if artista_2 and album_2:
        perfil_2, ultima_solicitud = construir_perfil_input_usuario(
            nombre_artista=artista_2,
            nombre_album=album_2,
            token_discogs=token_discogs,
            anio_min=anio_min,
            anio_max=anio_max,
            puntaje_minimo=puntaje_minimo,
            ultima_solicitud=ultima_solicitud,
            intervalo_minimo=intervalo_minimo
        )
        perfiles.append(perfil_2)

    return perfiles, ultima_solicitud

def perfiles_usuario_validos(perfiles):
    """
    Filtra los perfiles del usuario y conserva solo los utilizables
    por el recomendador.

    Un perfil se considera válido si:
    - el match en Discogs fue accepted_input
    - tiene una lista de tags normalizados no vacía

    Devuelve:
    - lista de perfiles válidos
    """
    perfiles_validos = []

    for perfil in perfiles:
        tags = perfil.get("discogs_tags_norm")
        status = perfil.get("discogs_match_status")

        if status == "accepted_input" and isinstance(tags, list) and len(tags) > 0:
            perfiles_validos.append(perfil)

    return perfiles_validos

#Funciones de similitud/ranking
def similitud_tags_ponderada(tags_input, tags_candidato, dicc_pesos):
    """
    Calcula similitud entre dos listas de tags usando una variante de Jaccard
    ponderada por pesos de tags.

    Parámetros:
    - tags_input: lista de tags del perfil del usuario
    - tags_candidato: lista de tags del disco candidato
    - dicc_pesos: diccionario con pesos por tag

    Devuelve:
    - score entre 0 y 1
    """
    if not isinstance(tags_input, list) or not isinstance(tags_candidato, list):
        return 0.0

    set_input = set(tags_input)
    set_candidato = set(tags_candidato)

    if len(set_input) == 0 or len(set_candidato) == 0:
        return 0.0

    interseccion = set_input.intersection(set_candidato)
    union = set_input.union(set_candidato)

    peso_interseccion = sum(dicc_pesos.get(tag, 1.0) for tag in interseccion)
    peso_union = sum(dicc_pesos.get(tag, 1.0) for tag in union)

    if peso_union == 0:
        return 0.0

    return round(peso_interseccion / peso_union, 4)

def similitud_anio(anio_input_norm, anio_candidato_norm):
    """
    Calcula similitud entre dos años ya normalizados.

    Convierte la distancia en un score:
    - 1.0 = misma posición temporal
    - 0.0 = muy alejados

    Devuelve:
    - score entre 0 y 1
    """
    if pd.isna(anio_input_norm) or pd.isna(anio_candidato_norm):
        return 0.0

    diferencia = abs(anio_input_norm - anio_candidato_norm)
    score = max(0, 1 - diferencia)

    return round(score, 4)

def calcular_score_candidato(perfil_usuario, fila_candidato, dicc_pesos, peso_tags=0.85, peso_anio=0.15):
    """
    Calcula el score total de un disco candidato frente a un perfil de usuario.

    Combina:
    - similitud por tags
    - similitud por año

    Devuelve:
    - score_tags
    - score_anio
    - score_total
    """
    tags_input = perfil_usuario.get("discogs_tags_norm", [])
    anio_input_norm = perfil_usuario.get("discogs_year_norm", None)

    tags_candidato = fila_candidato.get("discogs_tags_norm", [])
    anio_candidato_norm = fila_candidato.get("release_year_norm", None)

    score_tags = similitud_tags_ponderada(tags_input, tags_candidato, dicc_pesos)
    score_anio = similitud_anio(anio_input_norm, anio_candidato_norm)

    score_total = (score_tags * peso_tags) + (score_anio * peso_anio)

    return {
        "score_tags": round(score_tags, 4),
        "score_anio": round(score_anio, 4),
        "score_total": round(score_total, 4)
    }

def calcular_score_promedio_candidato(
    perfiles_usuario,
    fila_candidato,
    dicc_pesos,
    peso_tags=0.85,
    peso_anio=0.15
):
    """
    Calcula el score de un candidato contra uno o varios perfiles de usuario.

    Si hay:
    - 1 input: el score promedio coincide con ese input
    - 2 inputs: calcula score por input y score promedio

    También asigna una orientación de recomendación:
    - mezcla_ambos
    - ligeramente_input_1 / 2
    - claramente_input_1 / 2
    - alineado_input_1
    """
    scores = []

    for i, perfil in enumerate(perfiles_usuario, start=1):
        resultado = calcular_score_candidato(
            perfil_usuario=perfil,
            fila_candidato=fila_candidato,
            dicc_pesos=dicc_pesos,
            peso_tags=peso_tags,
            peso_anio=peso_anio
        )

        resultado["input_idx"] = i
        resultado["input_album"] = perfil.get("input_album")
        resultado["input_artist"] = perfil.get("input_artist")
        scores.append(resultado)

    if len(scores) == 0:
        return {
            "score_tags_promedio": 0.0,
            "score_anio_promedio": 0.0,
            "score_total_promedio": 0.0,
            "score_total_input_1": 0.0,
            "score_total_input_2": None,
            "orientacion_recomendacion": "sin_perfiles"
        }

    score_tags_promedio = sum(x["score_tags"] for x in scores) / len(scores)
    score_anio_promedio = sum(x["score_anio"] for x in scores) / len(scores)
    score_total_promedio = sum(x["score_total"] for x in scores) / len(scores)

    score_total_input_1 = scores[0]["score_total"] if len(scores) >= 1 else None
    score_total_input_2 = scores[1]["score_total"] if len(scores) >= 2 else None

    if len(scores) == 1:
        orientacion = "alineado_input_1"
    else:
        diferencia_inputs = abs(score_total_input_1 - score_total_input_2)
        score_min = min(score_total_input_1, score_total_input_2)

        if diferencia_inputs <= 0.06 and score_min >= 0.45:
            orientacion = "mezcla_ambos"
        elif diferencia_inputs <= 0.12:
            if score_total_input_1 > score_total_input_2:
                orientacion = "ligeramente_input_1"
            else:
                orientacion = "ligeramente_input_2"
        else:
            if score_total_input_1 > score_total_input_2:
                orientacion = "claramente_input_1"
            else:
                orientacion = "claramente_input_2"

    return {
        "score_tags_promedio": round(score_tags_promedio, 4),
        "score_anio_promedio": round(score_anio_promedio, 4),
        "score_total_promedio": round(score_total_promedio, 4),
        "score_total_input_1": round(score_total_input_1, 4) if score_total_input_1 is not None else None,
        "score_total_input_2": round(score_total_input_2, 4) if score_total_input_2 is not None else None,
        "orientacion_recomendacion": orientacion
    }

def construir_explicacion_recomendacion(perfiles_usuario, fila_candidato):
    """
    Construye una explicación breve y legible para justificar por qué
    se recomienda un disco candidato.

    Usa:
    - tags compartidos
    - orientación respecto a uno o dos inputs
    - cercanía temporal
    """
    tags_usuario = set()
    titulos_input = []

    for perfil in perfiles_usuario:
        tags = perfil.get("discogs_tags_norm", [])
        if isinstance(tags, list):
            tags_usuario.update(tags)

        titulo_input = perfil.get("discogs_title") or perfil.get("input_album")
        if titulo_input:
            titulos_input.append(str(titulo_input))

    tags_candidato = fila_candidato.get("discogs_tags_norm", [])
    if not isinstance(tags_candidato, list):
        tags_candidato = []

    tags_compartidos = sorted(list(tags_usuario.intersection(set(tags_candidato))))[:4]

    anios_usuario = []
    for perfil in perfiles_usuario:
        anio = perfil.get("discogs_year")
        if pd.notna(anio):
            anios_usuario.append(anio)

    anio_candidato = fila_candidato.get("release_year")
    orientacion = fila_candidato.get("orientacion_recomendacion")
    grupo_orientacion = fila_candidato.get("grupo_orientacion")

    partes = []

    if tags_compartidos:
        partes.append("Comparte tags como " + ", ".join(tags_compartidos))

    if grupo_orientacion == "mezcla_ambos" and len(titulos_input) >= 2:
        partes.append(f"funciona como punto medio entre {titulos_input[0]} y {titulos_input[1]}")
    elif orientacion == "ligeramente_input_1" and len(titulos_input) >= 1:
        partes.append(f"se inclina un poco más hacia el mood de {titulos_input[0]}")
    elif orientacion == "ligeramente_input_2" and len(titulos_input) >= 2:
        partes.append(f"se inclina un poco más hacia el mood de {titulos_input[1]}")
    elif orientacion == "claramente_input_1" and len(titulos_input) >= 1:
        partes.append(f"se acerca claramente más al mood de {titulos_input[0]}")
    elif orientacion == "claramente_input_2" and len(titulos_input) >= 2:
        partes.append(f"se acerca claramente más al mood de {titulos_input[1]}")
    elif orientacion == "alineado_input_1" and len(titulos_input) >= 1:
        partes.append(f"toma como referencia principal {titulos_input[0]}")

    if len(anios_usuario) > 0 and pd.notna(anio_candidato):
        anio_promedio_usuario = sum(anios_usuario) / len(anios_usuario)
        diferencia = abs(anio_promedio_usuario - anio_candidato)

        if diferencia <= 3:
            partes.append("además pertenece a una época muy cercana")
        elif diferencia <= 7:
            partes.append("y mantiene cierta cercanía temporal")

    if len(partes) == 0:
        return "Presenta afinidad general con el perfil musical ingresado"

    return ". ".join(partes)[:260]


def rankear_candidatos_kpop(perfiles_usuario, df_modelo, dicc_pesos, peso_tags=0.85, peso_anio=0.15):
    """
    Recorre todos los discos candidatos del dataset, calcula sus scores
    frente al perfil del usuario y devuelve un ranking ordenado.

    También:
    - agrega explicación
    - elimina duplicados visibles para el usuario
    """
    filas_rankeadas = []

    for _, fila in df_modelo.iterrows():
        scores = calcular_score_promedio_candidato(
            perfiles_usuario=perfiles_usuario,
            fila_candidato=fila,
            dicc_pesos=dicc_pesos,
            peso_tags=peso_tags,
            peso_anio=peso_anio
        )

        fila_dict = fila.to_dict()
        fila_dict.update(scores)
        fila_dict["explicacion"] = construir_explicacion_recomendacion(perfiles_usuario, fila_dict)

        filas_rankeadas.append(fila_dict)

    df_ranking = pd.DataFrame(filas_rankeadas)

    df_ranking = df_ranking.sort_values("score_total_promedio", ascending=False).reset_index(drop=True)

    df_ranking["clave_recomendacion"] = (
        df_ranking["spotify_artist_name"].astype(str).str.strip().str.lower()
        + " | " +
        df_ranking["nombre_album"].astype(str).str.strip().str.lower()
    )

    df_ranking = df_ranking.drop_duplicates(subset=["clave_recomendacion"], keep="first").reset_index(drop=True)

    return df_ranking

def limitar_recomendaciones_por_artista(df_ranking, max_por_artista=2):
    """
    Limita el número máximo de recomendaciones por artista para evitar
    que el top final quede demasiado concentrado.
    """
    filas_filtradas = []
    conteo_artistas = {}

    for _, fila in df_ranking.iterrows():
        artista = fila["spotify_artist_name"]
        conteo_actual = conteo_artistas.get(artista, 0)

        if conteo_actual < max_por_artista:
            filas_filtradas.append(fila)
            conteo_artistas[artista] = conteo_actual + 1

    return pd.DataFrame(filas_filtradas).reset_index(drop=True)

def obtener_top_5_recomendaciones(
    perfiles_usuario,
    df_modelo,
    dicc_pesos,
    peso_tags=0.85,
    peso_anio=0.15,
    max_por_artista=2
):
    """
    Genera el top 5 final de recomendaciones.

    Reglas:
    - máximo 2 discos por artista
    - si hay 1 input: top 5 por score promedio
    - si hay 2 inputs: intenta balancear híbrido + lado input 1 + lado input 2
    - marca 2 discos como must listen
    """
    df_ranking = rankear_candidatos_kpop(
        perfiles_usuario=perfiles_usuario,
        df_modelo=df_modelo,
        dicc_pesos=dicc_pesos,
        peso_tags=peso_tags,
        peso_anio=peso_anio
    ).copy()

    df_ranking = limitar_recomendaciones_por_artista(
        df_ranking,
        max_por_artista=max_por_artista
    ).copy()

    if len(perfiles_usuario) == 1:
        top_5 = df_ranking.sort_values("score_total_promedio", ascending=False).head(5).copy().reset_index(drop=True)
        top_5["must_listen"] = False

        if len(top_5) >= 1:
            top_5.loc[0, "must_listen"] = True
        if len(top_5) >= 2:
            top_5.loc[1, "must_listen"] = True

        top_5["grupo_orientacion"] = "input_unico"
        top_5["explicacion"] = top_5.apply(
            lambda fila: construir_explicacion_recomendacion(perfiles_usuario, fila.to_dict()),
            axis=1
        )

        return top_5

    df_ranking["score_total_input_1"] = pd.to_numeric(df_ranking["score_total_input_1"], errors="coerce").fillna(0)
    df_ranking["score_total_input_2"] = pd.to_numeric(df_ranking["score_total_input_2"], errors="coerce").fillna(0)
    df_ranking["score_total_promedio"] = pd.to_numeric(df_ranking["score_total_promedio"], errors="coerce").fillna(0)

    df_ranking["diferencia_inputs"] = (
        df_ranking["score_total_input_1"] - df_ranking["score_total_input_2"]
    ).abs()

    df_ranking["es_hibrido_real"] = (
        (df_ranking["score_total_input_1"] >= 0.40) &
        (df_ranking["score_total_input_2"] >= 0.40) &
        (df_ranking["diferencia_inputs"] <= 0.12)
    )

    df_ranking["score_hibrido"] = (
        df_ranking["score_total_promedio"] - (0.8 * df_ranking["diferencia_inputs"])
    )

    df_ranking["ventaja_input_1"] = df_ranking["score_total_input_1"] - df_ranking["score_total_input_2"]
    df_ranking["ventaja_input_2"] = df_ranking["score_total_input_2"] - df_ranking["score_total_input_1"]

    df_ranking["score_lado_input_1"] = (
        (0.7 * df_ranking["score_total_input_1"]) +
        (0.3 * df_ranking["ventaja_input_1"])
    )

    df_ranking["score_lado_input_2"] = (
        (0.7 * df_ranking["score_total_input_2"]) +
        (0.3 * df_ranking["ventaja_input_2"])
    )

    def asignar_orientacion_fina(fila):
        if fila["es_hibrido_real"]:
            return "mezcla_ambos"
        elif fila["score_total_input_1"] > fila["score_total_input_2"]:
            return "claramente_input_1" if fila["diferencia_inputs"] > 0.18 else "ligeramente_input_1"
        else:
            return "claramente_input_2" if fila["diferencia_inputs"] > 0.18 else "ligeramente_input_2"

    df_ranking["orientacion_recomendacion"] = df_ranking.apply(asignar_orientacion_fina, axis=1)

    def asignar_grupo(fila):
        if fila["es_hibrido_real"]:
            return "mezcla_ambos"
        elif fila["score_total_input_1"] > fila["score_total_input_2"]:
            return "lado_input_1"
        else:
            return "lado_input_2"

    df_ranking["grupo_orientacion"] = df_ranking.apply(asignar_grupo, axis=1)

    seleccion = []
    claves_usadas = set()

    def clave_fila(fila):
        return (
            str(fila["spotify_artist_name"]).strip().lower()
            + " | " +
            str(fila["nombre_album"]).strip().lower()
        )

    def agregar_mejor_fila(df_fuente):
        nonlocal seleccion, claves_usadas

        for _, fila in df_fuente.iterrows():
            clave = clave_fila(fila)
            if clave in claves_usadas:
                continue

            seleccion.append(fila.to_dict())
            claves_usadas.add(clave)
            return

    df_hibrido = df_ranking[df_ranking["es_hibrido_real"]].sort_values("score_hibrido", ascending=False)
    agregar_mejor_fila(df_hibrido)

    df_lado_1 = df_ranking[
        (~df_ranking["es_hibrido_real"]) &
        (df_ranking["score_total_input_1"] > df_ranking["score_total_input_2"])
    ].sort_values("score_lado_input_1", ascending=False)
    agregar_mejor_fila(df_lado_1)

    df_lado_2 = df_ranking[
        (~df_ranking["es_hibrido_real"]) &
        (df_ranking["score_total_input_2"] > df_ranking["score_total_input_1"])
    ].sort_values("score_lado_input_2", ascending=False)
    agregar_mejor_fila(df_lado_2)

    df_global = df_ranking.sort_values("score_total_promedio", ascending=False)

    for _, fila in df_global.iterrows():
        if len(seleccion) >= 5:
            break

        clave = clave_fila(fila)
        if clave in claves_usadas:
            continue

        seleccion.append(fila.to_dict())
        claves_usadas.add(clave)

    top_5 = pd.DataFrame(seleccion).head(5).copy().reset_index(drop=True)

    top_5["explicacion"] = top_5.apply(
        lambda fila: construir_explicacion_recomendacion(perfiles_usuario, fila.to_dict()),
        axis=1
    )

    top_5["must_listen"] = False

    idx_hibrido = top_5.index[top_5["grupo_orientacion"] == "mezcla_ambos"].tolist()
    if len(idx_hibrido) > 0:
        top_5.loc[idx_hibrido[0], "must_listen"] = True

    while top_5["must_listen"].sum() < 2:
        restantes = top_5[~top_5["must_listen"]].copy()
        if len(restantes) == 0:
            break

        idx_siguiente = restantes["score_total_promedio"].idxmax()
        top_5.loc[idx_siguiente, "must_listen"] = True

    return top_5

def ajustar_explicacion_must_listen(df_top):
    """
    Añade un prefijo a la explicación de los discos marcados como must listen.
    """
    df_top = df_top.copy()

    for i in df_top.index:
        if df_top.loc[i, "must_listen"]:
            explicacion_actual = df_top.loc[i, "explicacion"]
            df_top.loc[i, "explicacion"] = "Must listen: " + explicacion_actual

    return df_top

#Función final del recomendador
def recomendar_discos_kpop(
    artista_1,
    album_1,
    token_discogs,
    anio_min,
    anio_max,
    artista_2=None,
    album_2=None,
    df_modelo=None,
    dicc_pesos=None,
    puntaje_minimo=50,
    intervalo_minimo=1.0
):
    """
    Pipeline completo de recomendación.

    Flujo:
    1. construye perfiles del usuario
    2. filtra perfiles válidos
    3. obtiene top 5 recomendaciones
    4. ajusta explicación de must listen

    Devuelve un diccionario con:
    - status
    - mensaje
    - perfiles_usuario
    - perfiles_validos
    - recomendaciones
    """
    if df_modelo is None:
        raise ValueError("Debes proporcionar df_modelo.")

    if dicc_pesos is None:
        raise ValueError("Debes proporcionar dicc_pesos.")
   
    if not token_discogs:
        raise ValueError("No se proporcionó un token de Discogs válido.")


    ultima_solicitud = 0

    perfiles_usuario, ultima_solicitud = construir_perfiles_usuario(
        artista_1=artista_1,
        album_1=album_1,
        token_discogs=token_discogs,
        anio_min=anio_min,
        anio_max=anio_max,
        artista_2=artista_2,
        album_2=album_2,
        puntaje_minimo=puntaje_minimo,
        ultima_solicitud=ultima_solicitud,
        intervalo_minimo=intervalo_minimo
    )

    perfiles_validos = perfiles_usuario_validos(perfiles_usuario)

    if len(perfiles_validos) == 0:
        return {
            "status": "sin_perfiles_validos",
            "mensaje": "No se pudieron obtener tags válidos para los discos ingresados. Intenta con otros discos.",
            "perfiles_usuario": perfiles_usuario,
            "perfiles_validos": [],
            "recomendaciones": None
        }

    top_5 = obtener_top_5_recomendaciones(
        perfiles_usuario=perfiles_validos,
        df_modelo=df_modelo,
        dicc_pesos=dicc_pesos
    )

    top_5 = ajustar_explicacion_must_listen(top_5)

    return {
        "status": "ok",
        "mensaje": "Recomendaciones generadas correctamente.",
        "perfiles_usuario": perfiles_usuario,
        "perfiles_validos": perfiles_validos,
        "recomendaciones": top_5
    }

def preparar_backend_desde_csv(ruta_csv):
    """
    Prepara todo lo necesario para correr el recomendador a partir
    del CSV final del modelo.

    Flujo:
    1. carga el dataset
    2. reconstruye columnas tipo lista
    3. calcula rango de años
    4. construye diccionario de pesos de tags

    Devuelve:
    - df_modelo
    - anio_min
    - anio_max
    - dicc_pesos_tags
    """
    df_modelo = cargar_df_modelo(ruta_csv)
    anio_min, anio_max = obtener_rango_anios(df_modelo)
    dicc_pesos_tags = construir_dicc_pesos_tags(df_modelo)

    return df_modelo, anio_min, anio_max, dicc_pesos_tags

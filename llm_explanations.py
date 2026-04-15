import os
import streamlit as st
from openai import OpenAI

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

if not OPENAI_API_KEY:
    raise ValueError("No se encontró OPENAI_API_KEY en secrets ni en variables de entorno.")

client = OpenAI(api_key=OPENAI_API_KEY)

# PERFIL (RADAR)
def generar_explicacion_radar(tags_input_1, tags_input_2=None, tags_compartidos=None, tags_promedio=None):
    prompt = f"""
Redacta una explicación breve y natural sobre el perfil musical detectado.

Datos:
- Tags del disco 1: {tags_input_1}
- Tags del disco 2: {tags_input_2 if tags_input_2 else []}
- Tags compartidos entre ambos discos: {tags_compartidos if tags_compartidos else []}
- Tags del perfil final del usuario: {tags_promedio if tags_promedio else []}

Reglas:
- No inventes nada.
- No enumeres todos los géneros.
- Identifica 2 o 3 rasgos principales del perfil (ej: energético, melódico, experimental, emocional, etc.).
- Describe el perfil como una identidad musical, no como una lista.
- Explica brevemente qué aporta cada disco al perfil.
- Si hay conexión entre ambos discos, explícalo de forma natural.
- Evita frases genéricas como "diverso", "vibrante", "mezcla de géneros".
- Máximo 45 palabras.
- Un solo párrafo.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()


# COMPARATIVO
def generar_explicacion_comparativo(tags_usuario, tags_recs):
    prompt = f"""
Redacta una explicación breve, clara y alegre sobre la comparación entre el perfil del usuario y las recomendaciones.

Datos:
- Tags del perfil del usuario: {tags_usuario}
- Tags de las recomendaciones: {tags_recs}

Reglas:
- No inventes nada.
- No repitas los mismos géneros.
- Explica qué tipo de sonido o estilo se mantiene entre usuario y recomendaciones.
- Describe el tipo de experiencia musical (ej: más emocional, más energética, más experimental).
- Evita frases genéricas como "coinciden perfectamente".
- Haz que la explicación aporte algo nuevo.
- Máximo 45 palabras.
- Un solo párrafo.
"""
    prompt += "\nEmpieza directamente con la explicación, sin introducción."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

# RECOMENDACIÓN INDIVIDUAL
def generar_explicacion_recomendacion(album, artist, shared_tags, distinct_tags):
    prompt = f"""
Redacta una explicación breve sobre por qué este álbum aparece en el top de recomendaciones.

Datos:
- Álbum: {album}
- Artista: {artist}
- Tags compartidos con el perfil del usuario: {shared_tags}
- Tags que lo diferencian frente a otras recomendaciones: {distinct_tags}

Reglas:
- Usa únicamente estos datos.
- No inventes nada.
- No expliques que es k-pop.
- Si hay tags distintivos, menciona primero qué comparte con el perfil y después qué lo diferencia.
- Si no hay tags distintivos, explica por qué hace match con el perfil del usuario y lo que caracteriza a ese disco.
- Nunca digas que "no tiene tags distintivos".
- Evita frases genéricas como "sonido fresco", "ideal para disfrutar" o similares.
- Sé específico: describe el tipo de energía, estilo o sensación del álbum.
- Da un dato especifico sobre las letras o temática del álbum.
- Identifica si la sugerencia representan una mezcla equilibrada entre ambos inputs o si están más orientadas a uno de ellos.
- Haz que cada explicación suene distinta entre sí.
- Máximo 60 palabras.
- Un solo párrafo.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

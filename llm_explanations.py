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
Redacta una explicación breve, natural y alegre sobre el perfil musical detectado.

Datos:
- Tags del disco 1: {tags_input_1}
- Tags del disco 2: {tags_input_2 if tags_input_2 else []}
- Tags compartidos entre ambos discos: {tags_compartidos if tags_compartidos else []}
- Tags del perfil final del usuario: {tags_promedio if tags_promedio else []}

Reglas:
- Usa únicamente estos datos.
- No inventes nada.
- Lo más importante es describir el perfil final del usuario.
- Primero explica cómo es el perfil del usuario detectado.
- Después menciona brevemente qué aporta el disco 1.
- Si existe disco 2, menciona brevemente qué aporta el disco 2.
- Si hay tags compartidos, úsalos para explicar qué une ambos discos.
- No exageres ni uses frases demasiado floridas.
- El tono debe ser natural, claro y alegre, sin exagerar.
- Redacta como texto explicativo, no como mensaje conversacional.
- Máximo 45 palabras.
- Un solo párrafo.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
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
- Usa únicamente estos datos.
- No inventes nada.
- No saludes y no cierres con frases tipo "listo para disfrutar".
- Redacta como texto explicativo, no como mensaje conversacional.
- Explica en lenguaje sencillo qué rasgos definen al usuario.
- Luego explica porque las recomendaciones dadas son el mejor match con el usuario ya que conservan esos mismos rasgos.
- El tono debe ser natural, claro y alegre, sin exagerar.
- Máximo 45 palabras.
- Un solo párrafo.
"""
    prompt += "\nEmpieza directamente con la explicación, sin introducción."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
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
- Si no hay tags distintivos, explica solo por qué hace match con el perfil del usuario.
- Nunca digas que "no tiene tags distintivos".
- El tono debe ser natural, claro y alegre, sin exagerar.
- Máximo 40 palabras.
- Un solo párrafo.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
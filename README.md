# K-vibe Match 

K-vibe Match es una aplicación interactiva desarrollada en Streamlit que recomienda álbumes de K-pop a partir de uno o dos discos de referencia ingresados por el usuario.

La herramienta construye un perfil musical basado en tags (géneros y estilos) y genera recomendaciones explicables, mostrando:

- Perfil musical detectado  
- Comparación entre usuario y recomendaciones  
- Top 5 álbumes recomendados  
- Distribución temporal de los discos  

Además, incorpora generación de explicaciones mediante modelos de lenguaje para interpretar los resultados de forma clara y accesible.

---

## Instalación

1. Clona este repositorio y sitúate en su carpeta raíz:
    ```bash
    git clone https://github.com/tu-usuario/k-vibe-match.git
    cd k-vibe-match
    ```
2. Crea un entorno virtual (recomendado Python 3.10+):
    ```bash
    python -m venv .venv
    ```
3. Activa el entorno
   ```bash
    source .venv/bin/activate
    ```
4. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
5. Configura tus crendenciales (API Keys) creando el archivo:
    ```bash
    .streamlit/secrets.toml
    ```
    con el siguiente contenido
    ```bash
    TOKEN_DISCOGS = "tu_token_discogs"
    OPENAI_API_KEY = "tu_api_key_openai"
    ```
6. Ejecuta la aplicación:
    ```bash
    streamlit run app_streamlit_kpop_recomendador.py
    ```
---

## ¿Cómo funciona?
El sistema sigue este flujo:

1. El usuario introduce uno o dos álbumes
2. Se consultan datos desde la API de Discogs
3. Se construye un perfil musical basado en tags
4. Se comparan los perfiles contra un dataset de álbumes K-pop
5. Se calcula similitud mediante:
   - Tags ponderados (principal)
   - Año de lanzamiento (secundario)
8. Se generan recomendaciones y explicaciones interpretables

---

## Estructura del proyecto
k-vibe-match/
├── app_streamlit_kpop_recomendador.py
├── backend_recomendador.py
├── llm_explanations.py
├── requirements.txt
├── assets/
    └── icono.png
    └── log.PNG
└── data/
    └── df_modelo_final.csv

---

## Dependencias principales
- streamlit
- pandas
- plotly
- requests
- openai
  
---

## Notas importantes:
- Este proyecto utiliza la API de Discogs para obtener metadata de álbumes.
- Las explicaciones se generan mediante modelos de lenguaje (OpenAI).
- No se incluyen claves API en el repositorio por seguridad.

---

## Proyecto académico
Desarrollado como proyecto final enfocado en sistemas de recomendación y experiencia de usuario aplicada a música K-pop.
Elaborado por: Bethsua Beltrán Aguilar - Diplomado en Ciencia de Datos - Generación 30


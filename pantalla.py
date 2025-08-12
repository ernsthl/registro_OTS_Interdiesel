from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database_mysql import obtener_ordenes_pantalla

# Configuración general
st.set_page_config(page_title="Pantalla de Producción", layout="wide")
st.image("Logo_interdiesel.jpg", width=400)
st.markdown(
    "<h1 style='text-align: center; font-size: 50px;'>🖥️ Órdenes de Trabajo en Producción</h1>",
    unsafe_allow_html=True
)

JSON_PATH = "last_update.json"

def obtener_last_update_json():
    if not os.path.exists(JSON_PATH):
        return None
    try:
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
        return data.get("last_update")
    except Exception as e:
        st.error(f"Error leyendo {JSON_PATH}: {e}")
        return None

# Estilos generales para la tabla con tamaños dinámicos
table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '2vw'),        # Escala con el ancho de la pantalla
        ('text-align', 'center'),
        ('background-color', '#003366'),
        ('color', 'white'),
        ('padding', '1vw')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', '1.5vw'),      # Escala con el ancho de la pantalla
        ('text-align', 'center'),
        ('padding', '0.8vw')
    ]}
]

# Colores según estado
def color_fila(row):
    estado = row["Estado"].lower()
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #28a745; color: white"  # Verde
    elif estado in ["diagnóstico", "diagnostico"]:
        color = "background-color: #ffc107; color: black"  # Amarillo
    elif estado == "cotizado":
        color = "background-color: #007bff; color: white"  # Azul
    elif estado == "despachado":
        color = "background-color: #6c757d; color: white"  # Gris
    elif estado == "r-urg":
        color = "background-color: #dc3545; color: white"  # Rojo
    else:
        color = ""
    return [color] * len(row)

# Refresco automático cada 15 segundos
st_autorefresh(interval=15_000, key="datarefresh")

# Estado inicial
if "last_update_guardado" not in st.session_state:
    st.session_state.last_update_guardado = None

last_update_actual = obtener_last_update_json()

if last_update_actual != st.session_state.last_update_guardado:
    st.session_state.last_update_guardado = last_update_actual

# Datos
ordenes = obtener_ordenes_pantalla()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
else:
    df = pd.DataFrame(ordenes, columns=[
        "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ])
    df['Estado'] = df['Estado'].astype(str)

    # Aplicar estilos
    styled_df = df.style.apply(color_fila, axis=1).set_table_styles(table_styles)

    # Convertir a HTML y ajustar ancho al 100% con columnas fijas
    html = styled_df.to_html()
    html = html.replace(
        '<table ',
        '<table style="width:100%; table-layout:fixed; word-wrap:break-word;" '
    )

    st.markdown(html, unsafe_allow_html=True)



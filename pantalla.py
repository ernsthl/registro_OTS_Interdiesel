from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database_mysql import obtener_ordenes_pantalla

# Configuración de página
st.set_page_config(page_title="Pantalla de Producción", layout="wide")

# Quitar padding superior de Streamlit y estilos generales
st.markdown("""
    <style>
        /* Quitar padding superior */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        /* Logo y título en la misma línea */
        .logo-title {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 5px 0;
        }
        /* Tabla ajustada */
        table {
            width: 100% !important;
            border-collapse: collapse;
            table-layout: auto; /* evita deformar columnas */
            word-break: keep-all; /* evita cortar palabras */
            white-space: normal; /* permite saltos de línea */
        }
    </style>
""", unsafe_allow_html=True)

# Logo y título juntos
st.markdown("""
<div class="logo-title">
    <img src="Logo_interdiesel.jpg" alt="Logo" style="height:100px;">
    <h1 style="margin:0; font-size:40px;">🖥️ Órdenes de Trabajo en Producción</h1>
</div>
""", unsafe_allow_html=True)

# Ruta JSON
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

# Estilos para la tabla
table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '28px'),  # encabezado más pequeño
        ('text-align', 'center'),
        ('background-color', '#003366'),
        ('color', 'white'),
        ('padding', '8px')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', '22px'),
        ('text-align', 'center'),
        ('padding', '5px')
    ]}
]

# Colores por estado
def color_fila(row):
    estado = row["Estado"].lower()
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #28a745; color: white"
    elif estado in ["diagnóstico", "diagnostico"]:
        color = "background-color: #ffc107; color: black"
    elif estado == "cotizado":
        color = "background-color: #007bff; color: white"
    elif estado == "despachado":
        color = "background-color: #6c757d; color: white"
    elif estado == "r-urg":
        color = "background-color: #dc3545; color: white"
    else:
        color = ""
    return [color] * len(row)

# Refrescar automáticamente cada 15 segundos
count = st_autorefresh(interval=15_000, key="datarefresh")

if "last_update_guardado" not in st.session_state:
    st.session_state.last_update_guardado = None

last_update_actual = obtener_last_update_json()

if last_update_actual != st.session_state.last_update_guardado:
    st.session_state.last_update_guardado = last_update_actual

# Mostrar datos
ordenes = obtener_ordenes_pantalla()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
else:
    df = pd.DataFrame(ordenes, columns=[
        "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ])
    df['Estado'] = df['Estado'].astype(str)
    styled_df = df.style.apply(color_fila, axis=1).set_table_styles(table_styles)
    html = styled_df.to_html()
    st.markdown(html, unsafe_allow_html=True)


from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database_mysql import obtener_ordenes_pantalla

# Configuración de página
st.set_page_config(page_title="Pantalla de Producción", layout="wide")

# Logo + Título en la misma fila
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Logo_interdiesel.jpg", use_container_width=True)
with col2:
    st.markdown("""
    <h2 style='margin:0; padding-top:10px;'>
    🖥️ Órdenes de Trabajo en Producción
    </h2>
    """, unsafe_allow_html=True)

# Ruta del archivo JSON
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

# Estilos para tabla
table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', 'clamp(16px, 1.2vw, 28px)'),
        ('text-align', 'center'),
        ('background-color', '#003366'),
        ('color', 'white'),
        ('padding', '6px')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', 'clamp(14px, 1vw, 20px)'),
        ('text-align', 'center'),
        ('padding', '4px')
    ]}
]

# CSS para evitar cortes de palabras y ocupar ancho total
st.markdown("""
<style>
table {
    width: 100% !important;
    table-layout: auto !important;
}
th, td {
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)

# Función para colorear filas según estado
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

# Refrescar cada 15 segundos
count = st_autorefresh(interval=15_000, key="datarefresh")

# Estado inicial
if "last_update_guardado" not in st.session_state:
    st.session_state.last_update_guardado = None

# Obtener última actualización
last_update_actual = obtener_last_update_json()
if last_update_actual != st.session_state.last_update_guardado:
    st.session_state.last_update_guardado = last_update_actual

# Cargar datos
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

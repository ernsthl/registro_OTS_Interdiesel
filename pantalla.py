from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database_mysql import obtener_ordenes_pantalla

# Configuración de página
st.set_page_config(page_title="Pantalla de Producción", layout="wide")

# Logo
st.image("Logo_interdiesel.jpg", width=400)

# Título responsivo
st.markdown("""
<h1 style='text-align: center; font-size: clamp(30px, 4vw, 60px);'>
🖥️ Órdenes de Trabajo en Producción
</h1>
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

# Estilos dinámicos para tabla
table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', 'clamp(20px, 2vw, 40px)'),
        ('text-align', 'center'),
        ('background-color', '#003366'),
        ('color', 'white'),
        ('padding', 'clamp(10px, 1vw, 20px)')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', 'clamp(16px, 1.5vw, 32px)'),
        ('text-align', 'center'),
        ('padding', 'clamp(8px, 0.8vw, 15px)')
    ]}
]

# CSS extra para ancho completo y evitar deformaciones
st.markdown("""
<style>
table {
    width: 100% !important;
    table-layout: fixed !important;
    word-wrap: break-word;
}
th, td {
    white-space: normal !important;
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
        color = "background-c

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database_mysql import obtener_ordenes_pantalla
from streamlit_autorefresh import st_autorefresh

# -------------------- Configuración inicial --------------------
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

def color_fila(row):
    estado = row["Estado"].lower()
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #90ee90"
    elif estado in ["diagnóstico", "diagnostico"]:
        color = "background-color: #fffacd"
    elif estado == "cotizado":
        color = "background-color: #add8e6"
    elif estado == "despachado":
        color = "background-color: #d3d3d3"
    elif estado == "r-urg":
        color = "background-color: #ff7f7f; color: white"
    else:
        color = ""
    return [color] * len(row)

table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '40px'),
        ('text-align', 'center'),
        ('background-color', '#f0f0f0'),
        ('padding', '15px')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', '30px'),
        ('text-align', 'center'),
        ('padding', '10px')
    ]}
]

# Refrescar automáticamente cada 15 segundos
st_autorefresh(interval=15_000, key="datarefresh")

# Guarda el último update leído en la sesión
if "last_update_guardado" not in st.session_state:
    st.session_state.last_update_guardado = None

last_update_actual = obtener_last_update_json()

# Solo recarga datos si el last_update cambió
if last_update_actual != st.session_state.last_update_guardado:
    st.session_state.last_update_guardado = last_update_actual
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
        st.dataframe(styled_df, use_container_width=True)

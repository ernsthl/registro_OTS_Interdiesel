# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:48:37 2025

@author: ernst
"""

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
            padding-top: 1rem;
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

# --- Cabecera con logo y título ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Logo_interdiesel.jpg", use_column_width=True)
with col2:
    st.markdown("""
    <h2 style='margin:0; padding-top:10px;'>
    🖥️ Órdenes de Trabajo en Producción
    </h2>
    """, unsafe_allow_html=True)

# --- 📌 Obtener órdenes y preparar filtro ---
ordenes = obtener_ordenes_pantalla()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
    st.stop()
else:
    df_init = pd.DataFrame(ordenes, columns=[
        "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ])
    df_init['Estado'] = df_init['Estado'].astype(str)

    tecnicos = sorted(df_init["Técnico"].dropna().unique())
    tecnico_seleccionado = st.selectbox(
        "👷 Seleccione Técnico",
        options=["Todos"] + list(tecnicos),
        index=0
    )

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
        ('font-size', '28px'),
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

# -----------------------------
# 🔄 Refrescar datos
# -----------------------------
ordenes = obtener_ordenes_pantalla()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
else:
    df = pd.DataFrame(ordenes, columns=[
        "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ])
    df['Estado'] = df['Estado'].astype(str)

    # 👇 Aplicamos filtro aquí (justo antes de ordenar y mostrar)
    if tecnico_seleccionado and tecnico_seleccionado != "Todos":
        df = df[df["Técnico"] == tecnico_seleccionado]

    # 👇 Validamos si después del filtro quedó vacío
    if df.empty:
        st.warning("⚠️ No hay órdenes para el técnico seleccionado.")
    else:
        # Definir prioridad de estados
        prioridad = {
            "autorizado": 2,
            "r-urg": 1,
            "diagnóstico": 3,
            "diagnostico": 3,  # por si llega sin tilde
            "cotizado": 4
        }

        df["prioridad_estado"] = df["Estado"].str.lower().map(prioridad).fillna(99)
        df = df.sort_values(by=["prioridad_estado", "Fecha Registro"], ascending=[True, False])
        df = df.drop(columns=["prioridad_estado"])

        # Render tabla
        styled_df = df.style.apply(color_fila, axis=1).set_table_styles(table_styles)
        html = styled_df.to_html()
        st.markdown(html, unsafe_allow_html=True)

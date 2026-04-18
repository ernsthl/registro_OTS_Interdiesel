# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:48:37 2025

@author: ernst
"""

from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
from database_mysql import obtener_ordenes_pantalla
from database_mysql import obtener_last_update_db

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
            table-layout: auto;
            word-break: keep-all;
            white-space: normal;
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

# -----------------------------
# 🔄 Funciones auxiliares
# -----------------------------

# def obtener_last_update_json():
#     """Obtiene el timestamp del log_sync para invalidar la caché solo si hay cambios."""
#     try:
#         return obtener_last_update_db()
#     except Exception as e:
#         st.error(f"Error obteniendo log_sync: {e}")
#         return None

# ✅ Cacheamos la consulta a BD
@st.cache_data(ttl=300, show_spinner=False)
def cargar_ordenes(last_update: str):
    _ = last_update  # solo para cache key
    return obtener_ordenes_pantalla()

# -----------------------------
# 🎨 Estilos tabla y colores
# -----------------------------
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

# -----------------------------
# 🔄 Refrescar automáticamente cada 15s
# -----------------------------
count = st_autorefresh(interval=60000, key="datarefresh")

# -----------------------------
# 📥 Cargar datos con cache
# -----------------------------
@st.cache_data(ttl=60)
def obtener_last_update_cached():
    return obtener_last_update_db()

try:
    last_update = obtener_last_update_cached()
except Exception as e:
    st.error(f"Error obteniendo actualización: {e}")
    last_update = str(pd.Timestamp.now())

ordenes = cargar_ordenes(last_update)

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
    st.stop()

# Convertir a DataFrame
df = pd.DataFrame(ordenes, columns=[
    "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
    "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
])
df['Estado'] = df['Estado'].astype(str)

# -----------------------------
# 👷 Filtro de técnicos
# -----------------------------
tecnicos_unicos = (
    df["Técnico"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .unique()
)

tecnico_seleccionado = st.selectbox(
    "👷 Seleccione Técnico",
    options=["Todos"] + sorted(tecnicos_unicos),
    index=0
)

# Aplicar filtro
if tecnico_seleccionado and tecnico_seleccionado != "Todos":
    df = df[df["Técnico"].str.contains(tecnico_seleccionado, case=False, na=False)]

# -----------------------------
# 📊 Mostrar datos
# -----------------------------
if df.empty:
    st.warning("⚠️ No hay órdenes para el técnico seleccionado.")
else:
    # Prioridad de estados
    prioridad = {
        "autorizado": 2,
        "r-urg": 1,
        "diagnóstico": 3,
        "diagnostico": 3,
        "cotizado": 4
    }

    df["prioridad_estado"] = df["Estado"].str.lower().map(prioridad).fillna(99)
    df = df.sort_values(by=["prioridad_estado", "Fecha Registro"], ascending=[True, False])
    df = df.drop(columns=["prioridad_estado"])

    # Render tabla
    styled_df = df.style.apply(color_fila, axis=1).set_table_styles(table_styles)
    html = styled_df.to_html()
    st.markdown(html, unsafe_allow_html=True)


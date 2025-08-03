import streamlit as st
from database import init_db, obtener_ordenes
import pandas as pd

st.set_page_config(page_title="Pantalla Taller", layout="wide")
init_db()

st.title("📺 Vista de Producción - Órdenes de Trabajo")

ordenes = obtener_ordenes()

df = pd.DataFrame(ordenes, columns=[
    "ID", "FECHA REGISTRO OT", "OT", "CLIENTE", "TIPO SERVICIO",
    "TECNICO", "ESTADO", "FECHA ENTREGA", "HORA ENTREGA"
])

# Separamos en dos: activas y despachadas
df_activas = df[df["ESTADO"].str.upper() != "DESPACHADO"]
df_despachadas = df[df["ESTADO"].str.upper() == "DESPACHADO"]

def colorear_estado(estado):
    colores = {
        "DIAGNOSTICO": "background-color: orange",
        "COTIZADO": "background-color: yellow",
        "AUTORIZADO": "background-color: lightgreen",
        "DESPACHADO": "background-color: lightblue",
        "R-URG": "background-color: red; color: white"
    }
    return colores.get(estado.upper(), "")

st.subheader("🟢 Órdenes Activas")
df_activas["COLOR ESTADO"] = df_activas["ESTADO"].apply(lambda x: x.upper())
st.dataframe(df_activas.style.map(colorear_estado, subset=["COLOR ESTADO"]), use_container_width=True)

if not df_despachadas.empty:
    st.subheader("📦 Órdenes Despachadas")
    st.dataframe(df_despachadas, use_container_width=True)

# Auto-actualización cada 30 segundos
st.rerun()

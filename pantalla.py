# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 22:07:15 2025

@author: ernst
"""

import streamlit as st
import pandas as pd
from database_mysql import obtener_ordenes, obtener_timestamp_sync
from datetime import datetime

st.set_page_config(page_title="Pantalla OTs", layout="wide")
st.title("📺 Visualización de Órdenes de Trabajo")

# Control de sincronización
if "last_check" not in st.session_state:
    st.session_state.last_check = None

current_sync = obtener_timestamp_sync()
if st.session_state.last_check is None:
    st.session_state.last_check = current_sync
elif current_sync != st.session_state.last_check:
    st.session_state.last_check = current_sync
    st.experimental_rerun()

# Obtener datos
datos = obtener_ordenes()

if datos:
    columnas = [
        "Fecha Registro", "Número OT", "Cliente", "marca_modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ]
    df = pd.DataFrame(datos, columns=columnas)
    df.drop("ID", axis=1, inplace=True)

    # Colorear según estado
    colores = {
        "diagnóstico": "#FFFACD",
        "cotizado": "#ADD8E6",
        "autorizado": "#90EE90",
        "despachado": "#D3D3D3",
        "R-URG": "#FF7F7F"
    }

    def resaltar_estado(val):
        color = colores.get(val, "#FFFFFF")
        return f"background-color: {color}"

    df_estilo = df.style.applymap(resaltar_estado, subset=["Estado"])

    # Mostrar activas
    st.subheader("Órdenes Activas")
    df_activas = df[df["Estado"] != "despachado"]
    st.dataframe(df_activas.style.applymap(resaltar_estado, subset=["Estado"]), use_container_width=True)

    # Mostrar despachadas
    st.subheader("📦 Órdenes Despachadas")
    df_despachadas = df[df["Estado"] == "despachado"]
    st.dataframe(df_despachadas.style.applymap(resaltar_estado, subset=["Estado"]), use_container_width=True)
else:
    st.info("No hay órdenes registradas.")


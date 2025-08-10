import time
import mysql.connector
import pandas as pd
import streamlit as st

# --- Configuración ---
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        table {
            font-size: 28px !important;
        }
        thead th {
            font-weight: bold !important;
            font-size: 32px !important;
            background-color: #f0f0f0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Conexión ---
def conectar():
    return mysql.connector.connect(
        host="us-phx-web1166.main-hosting.eu",
        user="u978404744_admin",
        password="91AW9S:IPj&",
        database="u978404744_control_ots"
    )

# --- Funciones ---
def obtener_timestamp():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT ultima_actualizacion FROM log_sync WHERE id = 1")
    ts = cur.fetchone()[0]
    conn.close()
    return ts

def obtener_ordenes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero_ot, fecha_registro, cliente, marca_modelo, tipo_servicio,
               tecnico, estado, fecha_entrega, hora_entrega
        FROM orden_trabajo
        WHERE estado != 'Despachado'
        ORDER BY fecha_registro DESC
    """)
    data = cur.fetchall()
    conn.close()

    df = pd.DataFrame(data, columns=[
        "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
        "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
    ])

    # Pintar filas en verde si estado es "Actualizado"
    df_html = df.style.apply(
        lambda row: ['background-color: lightgreen' if row["Estado"] == "Actualizado" else '' for _ in row],
        axis=1
    ).to_html()
    return df_html

# --- UI ---
st.title("🖥️ Órdenes de Trabajo en Producción")

ultima_version = obtener_timestamp()
tabla = st.empty()
tabla.markdown(obtener_ordenes(), unsafe_allow_html=True)

while True:
    time.sleep(2)  # Revisa cada 2 segundos
    nueva_version = obtener_timestamp()
    if nueva_version != ultima_version:
        ultima_version = nueva_version
        tabla.markdown(obtener_ordenes(), unsafe_allow_html=True)

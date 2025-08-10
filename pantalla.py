import time
import streamlit as st
import pandas as pd
from database_mysql import obtener_ordenes_pantalla

# -------------------- Configuración inicial --------------------
st.set_page_config(page_title="Pantalla de Producción", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 24px;
    }
    th {
        font-weight: bold;
        font-size: 28px !important;
        text-align: center !important;
        background-color: #333333 !important;
        color: white !important;
        padding: 12px !important;
    }
    td {
        font-size: 24px !important;
        text-align: center !important;
        padding: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("Logo_interdiesel.jpg", width=500)
st.markdown("<h1 style='text-align: center; color: white;'>🖥️ Órdenes de Trabajo en Producción</h1>", unsafe_allow_html=True)

def obtener_timestamp():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT ultima_actualizacion FROM log_sync WHERE id = 1")
    ts = cur.fetchone()[0]
    conn.close()
    return ts

# Cargar datos
ordenes = obtener_ordenes_pantalla()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
    st.stop()

# Convertir a DataFrame
df = pd.DataFrame(ordenes, columns=[
    "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
    "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
])

# Primera carga
ultima_version = obtener_timestamp()
df = obtener_ordenes()
tabla = st.empty()
tabla.dataframe(df, use_container_width=True)

# Loop de escucha
while True:
    time.sleep(2)  # Revisa cada 2 segundos
    nueva_version = obtener_timestamp()
    if nueva_version != ultima_version:
        ultima_version = nueva_version
        df = obtener_ordenes()
        tabla.dataframe(df, use_container_width=True)
        
# Normalizar estado
df['Estado'] = df['Estado'].astype(str).str.strip().str.lower()

# Eliminar duplicados
df = df.drop_duplicates(subset=["Número OT"])

# Función para colorear filas
def color_fila(row):
    estado = row["Estado"]
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #2ecc71; color: white"  # Verde brillante
    elif estado in ["diagnóstico", "diagnostico"]:
        color = "background-color: #f1c40f; color: black"  # Amarillo fuerte
    elif estado == "cotizado":
        color = "background-color: #3498db; color: white"  # Azul fuerte
    elif estado == "despachado":
        color = "background-color: #7f8c8d; color: white"  # Gris oscuro
    elif estado == "r-urg":
        color = "background-color: #e74c3c; color: white"  # Rojo fuerte
    else:
        color = "background-color: #bdc3c7; color: black"  # Gris claro
    return [color] * len(row)

# Estilo de tabla grande
styled_df = (
    df.style
      .apply(color_fila, axis=1)
      .set_table_styles([
          {'selector': 'th', 'props': [('font-size', '28px'), ('text-align', 'center')]},
          {'selector': 'td', 'props': [('font-size', '24px'), ('text-align', 'center')]}
      ])
)

# Mostrar tabla completa
st.markdown(styled_df.to_html(), unsafe_allow_html=True)



import streamlit as st
import pandas as pd
from database_mysql import obtener_ordenes

st.set_page_config(page_title="Pantalla de Producción", layout="wide")
st.title("🖥️ Órdenes de Trabajo en Producción")

# Cargar datos
ordenes = obtener_ordenes()

if not ordenes:
    st.info("No hay órdenes registradas actualmente.")
    st.stop()

# Convertir a DataFrame
df = pd.DataFrame(ordenes, columns=[
    "ID", "Fecha Registro", "Número OT", "Cliente", "Marca Modelo", "Tipo Servicio",
    "Técnico", "Estado", "Fecha Entrega", "Hora Entrega", "Registrado Por"
])

# Filtrar solo OTs no despachadas
df_activo = df[df["Estado"] != "despachado"].copy()

# Aplicar colores según estado
def color_estado(row):
    color = ""
    estado = row["Estado"]
    if estado == "diagnóstico":
        color = "background-color: lightgray"
    elif estado == "cotizado":
        color = "background-color: orange"
    elif estado == "autorizado":
        color = "background-color: lightgreen"
    elif estado == "R-URG":
        color = "background-color: red; color: white"
    return [color if col == "Estado" else "" for col in df_activo.columns]

# Mostrar tabla estilizada
st.dataframe(
    df_activo.style.apply(color_estado, axis=1),
    use_container_width=True,
    height=700
)

# OTs despachadas (en panel aparte)
df_despachadas = df[df["Estado"] == "despachado"].copy()
if not df_despachadas.empty:
    with st.expander("📦 Órdenes Despachadas"):
        st.dataframe(df_despachadas, use_container_width=True)

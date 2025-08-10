import streamlit as st
import pandas as pd
from database_mysql import obtener_ordenes_pantalla

# -------------------- Configuración inicial --------------------
st.set_page_config(page_title="Pantalla de Producción", layout="wide")
st.image("Logo_interdiesel.jpg", width=400)
st.title("🖥️ Órdenes de Trabajo en Producción")

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

# Normalizar estado
df['Estado'] = df['Estado'].astype(str).str.strip().str.lower()

# Eliminar duplicados
df = df.drop_duplicates(subset=["Número OT"])

# Función para colorear filas según estado
def color_fila(row):
    estado = row["Estado"]
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #90ee90"      # Verde claro
    elif estado in ["diagnóstico", "diagnostico"]:
        color = "background-color: #fffacd"      # Amarillo claro
    elif estado == "cotizado":
        color = "background-color: #add8e6"      # Azul claro
    elif estado == "despachado":
        color = "background-color: #d3d3d3"      # Gris
    elif estado == "r-urg":
        color = "background-color: #ff7f7f; color: white"  # Rojo con texto blanco
    else:
        color = ""
    return [color] * len(row)

# Estilos de tabla
styled_df = (
    df.style
      .apply(color_fila, axis=1)
      .set_table_styles([
          {'selector': 'th', 'props'

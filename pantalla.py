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

df['Estado'] = df['Estado'].astype(str).str.strip().str.lower()  # Normalizar estado a minúsculas

# Eliminar duplicados si hay (por ejemplo, por Número OT)
df = df.drop_duplicates(subset=["Número OT"])

# Función para colorear toda la fila según estado
def color_fila(row):
    estado = row["Estado"]
    if estado == "actualizado" or estado == "autorizado":
        color = "background-color: #90ee90"  # verde claro
    elif estado == "diagnóstico" or estado == "diagnostico":
        color = "background-color: #fffacd"  # amarillo claro
    elif estado == "cotizado":
        color = "background-color: #add8e6"  # azul claro
    elif estado == "despachado":
        color = "background-color: #d3d3d3"  # gris claro
    elif estado == "r-urg":
        color = "background-color: #ff7f7f; color: white"  # rojo con texto blanco
    else:
        color = ""  # sin color

    return [color] * len(row)

# Mostrar tabla estilizada con filas coloreadas
st.dataframe(
    df.style.apply(color_fila, axis=1),
    use_container_width=True,
    height=700
)

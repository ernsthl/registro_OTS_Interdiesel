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

df['Estado'] = df['Estado'].astype(str).str.strip().str.lower()

# Eliminar duplicados
df = df.drop_duplicates(subset=["Número OT"])

def color_fila(row):
    estado = row["Estado"]
    if estado == "actualizado" or estado == "autorizado":
        color = "background-color: #90ee90"
    elif estado == "diagnóstico" or estado == "diagnostico":
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

header_styles = [{
    'selector': 'th',
    'props': [
        ('font-weight', 'bold'),
        ('font-size', '14px'),
        ('text-align', 'center'),
        ('background-color', '#f0f0f0')
    ]
}]

st.dataframe(
    df.style
      .apply(color_fila, axis=1)
      .set_table_styles(header_styles),
    use_container_width=True,
    height=700
)

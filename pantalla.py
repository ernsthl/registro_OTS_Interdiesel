import streamlit as st
import pandas as pd
import time
from database_mysql import obtener_ordenes_pantalla, conectar

# -------------------- Configuración inicial --------------------
st.set_page_config(page_title="Pantalla de Producción", layout="wide")
st.image("Logo_interdiesel.jpg", width=400)
st.markdown(
    "<h1 style='text-align: center; font-size: 50px;'>🖥️ Órdenes de Trabajo en Producción</h1>",
    unsafe_allow_html=True
)

# Función para obtener el valor actual de last_update
def obtener_last_update():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT last_update FROM log_sync LIMIT 1")
    last_update = cur.fetchone()[0]
    conn.close()
    return str(last_update)

# Función para dar color a las filas según estado
def color_fila(row):
    estado = row["Estado"].lower()
    if estado in ["actualizado", "autorizado"]:
        color = "background-color: #90ee90"
    elif estado in ["diagnóstico", "diagnostico"]:
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

# Estilos de tabla
table_styles = [
    {'selector': 'th', 'props': [
        ('font-weight', 'bold'),
        ('font-size', '40px'),
        ('text-align', 'center'),
        ('background-color', '#f0f0f0'),
        ('padding', '15px')
    ]},
    {'selector': 'td', 'props': [
        ('font-size', '30px'),
        ('text-align', 'center'),
        ('padding', '10px')
    ]}
]

# Inicializar valor de last_update
last_update_guardado = obtener_last_update()

# Cargar datos iniciales
df_placeholder = st.empty()

def cargar_datos():
    ordenes = obtener_ordenes_pantalla()
    if not ordenes:
        df_placeholder.info("No hay órdenes registradas actualmente.")
    else:
        df = pd.DataFrame(ordenes, columns=[
            "Número OT", "Fecha Registro", "Cliente", "Marca Modelo", "Tipo Servicio",
            "Técnico", "Estado", "Fecha Entrega", "Hora Entrega"
        ])
        df['Estado'] = df['Estado'].astype(str)
        styled_df = df.style.apply(color_fila, axis=1).set_table_styles(table_styles)
        df_placeholder.dataframe(styled_df, use_container_width=True)

# Mostrar datos iniciales
cargar_datos()

# Loop de verificación con menor frecuencia
while True:
    last_update_actual = obtener_last_update()
    if last_update_actual != last_update_guardado:
        last_update_guardado = last_update_actual
        cargar_datos()
    time.sleep(15)  # revisa cada 15 segundos

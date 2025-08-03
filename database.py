import sqlite3
from pathlib import Path

DB_PATH = Path("data/ordenes.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

def insertar_orden(fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orden_trabajo (fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega))
    conn.commit()
    conn.close()

def obtener_ordenes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def actualizar_estado(numero_ot, nuevo_estado, nueva_fecha=None, nueva_hora=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if nueva_fecha and nueva_hora:
        cur.execute("""
            UPDATE orden_trabajo SET estado = ?, fecha_entrega = ?, hora_entrega = ? WHERE numero_ot = ?
        """, (nuevo_estado, nueva_fecha, nueva_hora, numero_ot))
    else:
        cur.execute("""
            UPDATE orden_trabajo SET estado = ? WHERE numero_ot = ?
        """, (nuevo_estado, numero_ot))
    conn.commit()
    conn.close()

def obtener_numeros_ot():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT numero_ot FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

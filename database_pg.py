# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 12:18:04 2026

@author: ernst
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# ⚠️ REEMPLAZA CON TUS DATOS DE NEON
DB_CONFIG = {
    "host": "ep-super-art-amtlmle8-pooler.c-5.us-east-1.aws.neon.tech",
    "database": "DB_control_ots",
    "user": "neondb_owner",
    "password": "npg_HZluioE4P9bq",
    "port": 5432,
    "sslmode": "require"
}

# -------------------- CONEXIÓN --------------------
def conectar():
    return psycopg2.connect(**DB_CONFIG)

# -------------------- INSERTAR OT --------------------
def insertar_orden(fecha_registro, numero_ot, cliente, marca_modelo,
                   tipo_servicio, tecnico, estado,
                   fecha_entrega, hora_entrega, usuario):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orden_trabajo (
            fecha_registro, numero_ot, cliente, marca_modelo,
            tipo_servicio, tecnico, estado,
            fecha_entrega, hora_entrega,
            usuario_modificacion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        fecha_registro, numero_ot, cliente, marca_modelo,
        tipo_servicio, tecnico, estado,
        fecha_entrega, hora_entrega,
        usuario
    ))

    # ✅ AUDITORÍA (AGREGADO)
    cur.execute("""
        INSERT INTO log_auditoria (operacion, numero_ot, estado_anterior, estado_nuevo, usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, ("registro", numero_ot, None, estado, usuario))

    cur.execute("UPDATE log_sync SET last_update = CURRENT_TIMESTAMP WHERE id = 1")

    conn.commit()
    conn.close()

# -------------------- OBTENER TODAS --------------------
def obtener_ordenes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, fecha_registro, numero_ot, cliente, marca_modelo,
               tipo_servicio, tecnico, estado,
               fecha_entrega, hora_entrega,
               usuario_modificacion, fecha_modificacion
        FROM orden_trabajo
        ORDER BY fecha_registro DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------- OBTENER PARA PANTALLA --------------------
def obtener_ordenes_pantalla():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero_ot, fecha_registro, cliente, marca_modelo,
               tipo_servicio, tecnico, estado,
               fecha_entrega, hora_entrega
        FROM orden_trabajo
        WHERE estado != 'Despachado'
        ORDER BY fecha_registro DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------- NUMEROS OT --------------------
def obtener_numeros_ot():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT numero_ot FROM orden_trabajo")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

# -------------------- LOGIN --------------------
def verificar_credenciales(usuario, contrasena):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM usuarios
        WHERE nombre_usuario = %s AND contrasena = %s
    """, (usuario, contrasena))
    result = cur.fetchone()
    conn.close()
    return result is not None

# -------------------- OBTENER OT POR NUMERO --------------------
def obtener_orden_por_numero(numero_ot):
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM orden_trabajo
        WHERE numero_ot = %s
    """, (numero_ot,))

    row = cur.fetchone()
    conn.close()
    return row

# -------------------- ACTUALIZAR OT --------------------
def actualizar_ot(numero_ot, cliente, marca_modelo,
                  tipo_servicio, tecnico, estado,
                  fecha_entrega, hora_entrega, usuario):

    conn = conectar()
    cur = conn.cursor()

    # Obtener estado anterior
    cur.execute("SELECT estado FROM orden_trabajo WHERE numero_ot = %s", (numero_ot,))
    row = cur.fetchone()
    estado_anterior = row[0] if row else None

    campos = [
        "cliente = %s",
        "marca_modelo = %s",
        "tipo_servicio = %s",
        "tecnico = %s",
        "estado = %s",
        "usuario_modificacion = %s",
        "fecha_modificacion = CURRENT_TIMESTAMP"
    ]

    valores = [cliente, marca_modelo, tipo_servicio, tecnico, estado, usuario]

    if fecha_entrega is not None:
        campos.append("fecha_entrega = %s")
        valores.append(fecha_entrega)

    if hora_entrega is not None:
        campos.append("hora_entrega = %s")
        valores.append(hora_entrega)

    valores.append(numero_ot)

    sql = f"UPDATE orden_trabajo SET {', '.join(campos)} WHERE numero_ot = %s"
    cur.execute(sql, valores)

    # ✅ AUDITORÍA
    cur.execute("""
        INSERT INTO log_auditoria (operacion, numero_ot, estado_anterior, estado_nuevo, usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, ("actualizacion", numero_ot, estado_anterior, estado, usuario))

    cur.execute("UPDATE log_sync SET last_update = CURRENT_TIMESTAMP WHERE id = 1")

    conn.commit()
    conn.close()

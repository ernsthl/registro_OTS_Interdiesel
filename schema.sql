CREATE TABLE IF NOT EXISTS orden_trabajo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_registro TEXT,
    numero_ot TEXT,
    cliente TEXT,
    tipo_servicio TEXT,
    tecnico TEXT,
    estado TEXT,
    fecha_entrega TEXT,
    hora_entrega TEXT
);

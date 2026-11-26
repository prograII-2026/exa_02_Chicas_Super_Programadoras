import random
from datetime import datetime, timedelta

from db import db


def _fecha_aleatoria():
    base = datetime(2024, 1, 1)
    f = base + timedelta(seconds=random.randint(0, 2 * 365 * 24 * 3600 - 1))
    texto = f.strftime("%Y-%m-%d %H:%M:%S")                 # texto -> datetime (lo pide la guía)
    return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S")


def _telemetria():
    """El documento embebido puede faltar completo o tener solo algunos campos."""
    if random.random() < 0.10:
        return None
    t = {}
    if random.random() < 0.85:
        t["visibilidad_km"] = round(random.uniform(0.5, 30.0), 1)
    if random.random() < 0.85:
        t["nubosidad_pct"] = random.randint(0, 100)
    if random.random() < 0.85:
        t["viento_nudos"] = round(random.uniform(0.0, 40.0), 1)
    return t or None


def generar_avistamientos(cantidad=10000, lote=1000, limpiar=True, semilla=None) -> int:
    if semilla is not None:
        random.seed(semilla)
    ubicaciones = list(db.ubicaciones.find({}, {"_id": 0, "tipo_zona": 0}))
    ids_cat = [c["_id"] for c in db.categorias_fenomeno.find({}, {"_id": 1})]
    ids_obs = [o["_id"] for o in db.observadores.find({}, {"_id": 1})]
    if not (ubicaciones and ids_cat and ids_obs):
        raise RuntimeError("Primero cargue ubicaciones, categorías y observadores (carga_datos.py)")

    if limpiar:
        db.avistamientos.drop()

    insertados, buffer = 0, []
    for n in range(1, cantidad + 1):
        codigo = f"REP-{n:08d}"
        doc = {
            "_id": codigo,
            "codigo_reporte": codigo,
            "fecha_evento": _fecha_aleatoria(),
            "id_categoria": random.choice(ids_cat),
            "id_observador": random.choice(ids_obs),
            "ubicacion": random.choice(ubicaciones),
        }

        if random.random() < 0.95:
            doc["duracion_seg"] = random.randint(1, 900)
        tel = _telemetria()
        if tel:
            doc["telemetria_entorno"] = tel
        if random.random() < 0.30:
            doc["notas"] = random.choice(["Visible a simple vista", "Registrado con cámara",
                                          "Sin sonido", "Acompañado de zumbido"])
        if random.random() < 0.25:
            doc["confirmado_por_radar"] = random.choice([True, False])
        if random.random() < 0.15:
            doc["cantidad_objetos"] = random.randint(1, 5)
        buffer.append(doc)

        if len(buffer) == lote:
            db.avistamientos.insert_many(buffer)
            insertados += len(buffer)
            buffer = []
    if buffer:
        db.avistamientos.insert_many(buffer)
        insertados += len(buffer)
    return insertados


if __name__ == "__main__":
    print(f"Avistamientos generados: {generar_avistamientos()}")
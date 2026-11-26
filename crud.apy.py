from db import db

def _siguiente_id(col) -> int:
    ultimo = col.find_one(sort=[("_id", -1)])
    return (ultimo["_id"] + 1) if ultimo else 1


def _insertar(col, doc: dict):
    doc = dict(doc)
    if doc.get("_id") is None:
        doc["_id"] = _siguiente_id(col)
    if col.find_one({"_id": doc["_id"]}):
        raise ValueError(f"Ya existe un documento con _id={doc['_id']}")
    col.insert_one(doc)
    return doc


def _modificar(col, _id: int, cambios: dict) -> bool:
    cambios.pop("_id", None)
    if not cambios:
        raise ValueError("No hay campos para modificar")
    return col.update_one({"_id": _id}, {"$set": cambios}).matched_count == 1


def _borrar(col, _id: int) -> bool:
    return col.delete_one({"_id": _id}).deleted_count == 1

def insertar_categoria(doc: dict):
    if not doc.get("nombre"):
        raise ValueError("'nombre' es obligatorio")
    return _insertar(db.categorias_fenomeno, doc)

def modificar_categoria(_id: int, cambios: dict) -> bool:
    return _modificar(db.categorias_fenomeno, _id, cambios)

def borrar_categoria(_id: int) -> bool:
    if db.avistamientos.find_one({"id_categoria": _id}):
        raise ValueError("No se puede borrar: hay avistamientos que usan esta categoría")
    return _borrar(db.categorias_fenomeno, _id)

def obtener_categoria(_id: int):
    return db.categorias_fenomeno.find_one({"_id": _id})

def listar_categorias():
    return list(db.categorias_fenomeno.find().sort("_id", 1))


def _validar_observador(doc: dict, parcial=False):
    if "indice_confiabilidad" in doc and not 0.0 <= float(doc["indice_confiabilidad"]) <= 1.0:
        raise ValueError("indice_confiabilidad debe estar entre 0.0 y 1.0")
    if not parcial and not doc.get("alias_o_estacion"):
        raise ValueError("'alias_o_estacion' es obligatorio")

def insertar_observador(doc: dict):
    _validar_observador(doc)
    return _insertar(db.observadores, doc)

def modificar_observador(_id: int, cambios: dict) -> bool:
    _validar_observador(cambios, parcial=True)
    return _modificar(db.observadores, _id, cambios)

def borrar_observador(_id: int) -> bool:
    if db.avistamientos.find_one({"id_observador": _id}):
        raise ValueError("No se puede borrar: hay avistamientos de este observador")
    return _borrar(db.observadores, _id)

def obtener_observador(_id: int):
    return db.observadores.find_one({"_id": _id})

def listar_observadores():
    return list(db.observadores.find().sort("_id", 1))
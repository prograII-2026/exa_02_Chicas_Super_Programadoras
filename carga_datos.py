
import csv
import random

from db import db
from subrutinas import _norm, clasificar_tipo_zona


ALIAS = {
    "id_sector": ["id_sector", "sector", "id", "codigo", "cod_sector"],
    "provincia": ["provincia"],
    "canton": ["canton"],
    "distrito": ["distrito"],
    "localidad": ["poblado", "localidad", "nombre_poblado", "barrio"],
}

CATEGORIAS = [
    {"_id": 1, "nombre": "Luminaria estacionaria",
     "descripcion": "Luz fija en el cielo sin desplazamiento aparente."},
    {"_id": 2, "nombre": "Eco radar no identificado",
     "descripcion": "Retorno de radar sin transpondedor ni plan de vuelo."},
    {"_id": 3, "nombre": "Estela luminosa",
     "descripcion": "Trazo luminoso prolongado en el cielo."},
    {"_id": 4, "nombre": "Objeto Volador NO Identificado",
     "descripcion": "Objeto observado que no pudo ser identificado."},
]

ROLES = ["Testigo ciudadano", "Operador radar", "Estación meteorológica"]


def _mapear_columnas(encabezados):
    norm = {_norm(h): h for h in encabezados}
    mapa = {}
    for campo, opciones in ALIAS.items():
        for op in opciones:
            if op in norm:
                mapa[campo] = norm[op]
                break
    faltan = [c for c in ("provincia", "canton", "localidad") if c not in mapa]
    if faltan:
        raise ValueError(f"No encontré las columnas {faltan}. Encabezados del CSV: {list(encabezados)}. "
                         "Ajuste el diccionario ALIAS en carga_datos.py")
    return mapa


def cargar_ubicaciones(ruta_csv="ubicaciones.csv", limpiar=True) -> int:
    if limpiar:
        db.ubicaciones.drop()
    docs = []
    with open(ruta_csv, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
        f.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
        except csv.Error:
            dialecto = csv.excel
        lector = csv.DictReader(f, dialect=dialecto)
        mapa = _mapear_columnas(lector.fieldnames)
        for i, fila in enumerate(lector, start=1):
            prov = fila[mapa["provincia"]].strip()
            cant = fila[mapa["canton"]].strip()
            dist = fila[mapa["distrito"]].strip() if "distrito" in mapa else ""
            loc = fila[mapa["localidad"]].strip()
            sector = fila[mapa["id_sector"]].strip() if "id_sector" in mapa else f"SEC-{i:05d}"
            docs.append({
                "id_sector": sector, "provincia": prov, "canton": cant,
                "distrito": dist, "localidad": loc,
                "tipo_zona": clasificar_tipo_zona(prov, cant, loc),
            })
    if docs:
        db.ubicaciones.insert_many(docs)
    return len(docs)


def cargar_categorias(limpiar=True) -> int:
    if limpiar:
        db.categorias_fenomeno.drop()
    for cat in CATEGORIAS:                       # la guía pide insert_one
        db.categorias_fenomeno.insert_one(dict(cat))
    return len(CATEGORIAS)


def cargar_observadores(cantidad=30, limpiar=True) -> int:
    if limpiar:
        db.observadores.drop()
    random.seed(7)
    docs = []
    for i in range(1, cantidad + 1):
        rol = random.choice(ROLES)
        docs.append({
            "_id": i,
            "alias_o_estacion": f"{rol.split()[0][:4].upper()}-{i:03d}",
            "rol": rol,
            "indice_confiabilidad": round(random.uniform(0.3, 1.0), 2),
        })
    db.observadores.insert_many(docs)            # la guía pide insert_many
    return len(docs)


def cargar_todo(ruta_csv="ubicaciones.csv"):
    return {
        "ubicaciones": cargar_ubicaciones(ruta_csv),
        "categorias_fenomeno": cargar_categorias(),
        "observadores": cargar_observadores(),
    }


if __name__ == "__main__":
    print(cargar_todo())

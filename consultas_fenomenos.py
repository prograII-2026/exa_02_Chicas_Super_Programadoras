
from db import db
from subrutinas import formatear_fecha, parsear_fecha



def consulta_filtrada(provincia=None, canton=None, id_categoria=None, limite=20):
    filtro = {}
    if provincia:
        filtro["ubicacion.provincia"] = {"$eq": provincia}
    if canton:
        filtro["ubicacion.canton"] = {"$eq": canton}
    if id_categoria is not None:
        filtro["id_categoria"] = {"$eq": int(id_categoria)}
    proyeccion = {"_id": 0, "codigo_reporte": 1, "fecha_evento": 1,
                  "duracion_seg": 1, "ubicacion.localidad": 1}
    cursor = (db.avistamientos.find(filtro, proyeccion)
              .sort([("duracion_seg", -1), ("fecha_evento", 1)])
              .limit(int(limite)))
    return list(cursor)



def consulta_rango_fechas(desde, hasta, limite=50):
    if isinstance(desde, str):
        desde = parsear_fecha(desde)
    if isinstance(hasta, str):
        hasta = parsear_fecha(hasta)
    filtro = {"fecha_evento": {"$gte": desde, "$lte": hasta}}
    proyeccion = {"_id": 0, "codigo_reporte": 1, "fecha_evento": 1, "ubicacion.localidad": 1}
    return list(db.avistamientos.find(filtro, proyeccion).sort("fecha_evento", 1).limit(int(limite)))



def reporte_lookup(limite=20):
    pipeline = [
        {"$lookup": {"from": "categorias_fenomeno", "localField": "id_categoria",
                     "foreignField": "_id", "as": "categoria"}},
        {"$lookup": {"from": "observadores", "localField": "id_observador",
                     "foreignField": "_id", "as": "observador"}},
        {"$unwind": "$categoria"},
        {"$unwind": "$observador"},
        {"$project": {"_id": 0, "codigo_reporte": 1, "duracion_seg": 1,
                      "fenomeno": "$categoria.nombre",
                      "observador": "$observador.alias_o_estacion",
                      "localidad": "$ubicacion.localidad"}},
        {"$limit": int(limite)},
    ]
    return list(db.avistamientos.aggregate(pipeline))


def filtrar_largos(resultados, umbral=200):
    return [r for r in resultados if r.get("duracion_seg", 0) > umbral]

def filtrar_largos_lambda(resultados, umbral=200):
    return list(filter(lambda r: r.get("duracion_seg", 0) > umbral, resultados))


if __name__ == "__main__":
    print("\n=== 1) Puntarenas, orden por duración desc y fecha asc ===")
    for r in consulta_filtrada(provincia="Puntarenas", limite=5):
        print(r["codigo_reporte"], formatear_fecha(r["fecha_evento"]),
              r.get("duracion_seg", "s/d"), r["ubicacion"]["localidad"])

    print("\n=== 2) Rango de fechas ===")
    for r in consulta_rango_fechas("2025-02-01", "2025-02-28 23:59", limite=5):
        print(r["codigo_reporte"], formatear_fecha(r["fecha_evento"]), r["ubicacion"]["localidad"])

    print("\n=== 3) $lookup ===")
    reporte = reporte_lookup(limite=500)
    for r in reporte[:5]:
        print(f'{r["codigo_reporte"]} | {r["fenomeno"]} | {r["observador"]} | {r["localidad"]}')

    print("\n=== 4) Duración > 200 s ===")
    largos = filtrar_largos(reporte)
    print(f"{len(largos)} de {len(reporte)} reportes superan 200 s")

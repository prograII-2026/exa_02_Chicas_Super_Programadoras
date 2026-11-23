from flask import Flask, jsonify, request

import carga_datos
import consultas_fenomenos as cons
import crud
import generar_avistamientos as gen
from subrutinas import serializar

app = Flask(__name__)
app.json.ensure_ascii = False


def ok(data, code=200):
    return jsonify(serializar(data)), code

def error(msg, code=400):
    return jsonify({"error": str(msg)}), code


# ---------- carga ----------
@app.post("/carga/ubicaciones")
def carga_ubicaciones():
    ruta = (request.get_json(silent=True) or {}).get("ruta", "ubicaciones.csv")
    try:
        return ok({"insertadas": carga_datos.cargar_ubicaciones(ruta)}, 201)
    except (FileNotFoundError, ValueError) as e:
        return error(e)

@app.post("/carga/catalogos")
def carga_catalogos():
    return ok({"categorias_fenomeno": carga_datos.cargar_categorias(),
               "observadores": carga_datos.cargar_observadores()}, 201)


# ---------- CRUD categorias ----------
@app.get("/categorias")
def categorias_listar():
    return ok(crud.listar_categorias())

@app.get("/categorias/<int:_id>")
def categorias_obtener(_id):
    doc = crud.obtener_categoria(_id)
    return ok(doc) if doc else error("No existe", 404)

@app.post("/categorias")
def categorias_crear():
    try:
        return ok(crud.insertar_categoria(request.get_json(force=True)), 201)
    except ValueError as e:
        return error(e, 409)

@app.put("/categorias/<int:_id>")
def categorias_modificar(_id):
    try:
        return ok({"modificada": True}) if crud.modificar_categoria(_id, request.get_json(force=True)) \
            else error("No existe", 404)
    except ValueError as e:
        return error(e)

@app.delete("/categorias/<int:_id>")
def categorias_borrar(_id):
    try:
        return ok({"borrada": True}) if crud.borrar_categoria(_id) else error("No existe", 404)
    except ValueError as e:
        return error(e, 409)


# ---------- CRUD observadores ----------
@app.get("/observadores")
def observadores_listar():
    return ok(crud.listar_observadores())

@app.get("/observadores/<int:_id>")
def observadores_obtener(_id):
    doc = crud.obtener_observador(_id)
    return ok(doc) if doc else error("No existe", 404)

@app.post("/observadores")
def observadores_crear():
    try:
        return ok(crud.insertar_observador(request.get_json(force=True)), 201)
    except ValueError as e:
        return error(e, 409)

@app.put("/observadores/<int:_id>")
def observadores_modificar(_id):
    try:
        return ok({"modificado": True}) if crud.modificar_observador(_id, request.get_json(force=True)) \
            else error("No existe", 404)
    except ValueError as e:
        return error(e)

@app.delete("/observadores/<int:_id>")
def observadores_borrar(_id):
    try:
        return ok({"borrado": True}) if crud.borrar_observador(_id) else error("No existe", 404)
    except ValueError as e:
        return error(e, 409)


# ---------- avistamientos ----------
@app.post("/avistamientos/generar")
def avistamientos_generar():
    cantidad = request.args.get("cantidad", 10000, type=int)
    try:
        return ok({"generados": gen.generar_avistamientos(cantidad)}, 201)
    except RuntimeError as e:
        return error(e, 409)

@app.get("/avistamientos")
def avistamientos_filtrar():
    a = request.args
    return ok(cons.consulta_filtrada(a.get("provincia"), a.get("canton"),
                                     a.get("categoria", type=int), a.get("limite", 20, type=int)))

@app.get("/avistamientos/rango")
def avistamientos_rango():
    desde, hasta = request.args.get("desde"), request.args.get("hasta")
    if not (desde and hasta):
        return error("Indique ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD")
    try:
        return ok(cons.consulta_rango_fechas(desde, hasta, request.args.get("limite", 50, type=int)))
    except ValueError as e:
        return error(e)

@app.get("/avistamientos/reporte")
def avistamientos_reporte():
    return ok(cons.reporte_lookup(request.args.get("limite", 20, type=int)))

@app.get("/avistamientos/largos")
def avistamientos_largos():
    umbral = request.args.get("umbral", 200, type=int)
    return ok(cons.filtrar_largos(cons.reporte_lookup(limite=10000), umbral))


if __name__ == "__main__":
    app.run(debug=True)

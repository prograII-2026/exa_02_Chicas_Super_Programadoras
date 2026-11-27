
import unicodedata
from datetime import datetime

from bson import ObjectId


def _norm(texto) -> str:
    t = unicodedata.normalize("NFD", str(texto or ""))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


CANTONES_COSTEROS = {
    "Puntarenas", "Esparza", "Montes de Oro", "Osa", "Quepos", "Golfito", "Parrita",
    "Corredores", "Garabito", "Liberia", "Nicoya", "Santa Cruz", "Bagaces", "Carrillo",
    "Cañas", "Abangares", "Nandayure", "La Cruz", "Hojancha", "Limón", "Pococí",
    "Siquirres", "Talamanca", "Matina", "Guácimo",
}

CANTONES_MONTANOSOS = {
    "Tarrazú", "Aserrí", "Mora", "Acosta", "Turrubares", "Dota", "Pérez Zeledón",
    "León Cortés", "Puriscal", "San Ramón", "Zarcero", "Poás", "Valverde Vega",
    "Paraíso", "Jiménez", "Turrialba", "Alvarado", "Oreamuno", "El Guarco", "Barva",
    "Santa Bárbara", "San Rafael", "San Isidro", "Tilarán", "Buenos Aires", "Coto Brus",
}

POBLADOS_INSULARES = {
    "Isla del Coco", "Isla Chira", "Isla Venado", "Isla Caballo", "Isla San Lucas",
    "Isla Tortuga", "Isla Cedros", "Isla Jesucita", "Isla Berrugate",
}

_COSTEROS = {_norm(x) for x in CANTONES_COSTEROS}
_MONTANOSOS = {_norm(x) for x in CANTONES_MONTANOSOS}
_INSULARES = {_norm(x) for x in POBLADOS_INSULARES}


def clasificar_tipo_zona(provincia: str, canton: str, poblado: str) -> str:
    if _norm(poblado) in _INSULARES:
        return "Insular"
    if _norm(canton) in _COSTEROS:
        return "Costera"
    if _norm(canton) in _MONTANOSOS:
        return "Montañosa"
    return "Urbana"


MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def nombre_mes(numero: int) -> str:
    return MESES[numero - 1]


def formatear_fecha(fecha: datetime) -> str:
    if not isinstance(fecha, datetime):
        return str(fecha)
    return f"{fecha.day} de {nombre_mes(fecha.month)} de {fecha.year}, {fecha:%H:%M}"


def parsear_fecha(texto: str) -> datetime:
    texto = texto.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DD HH:MM")


def serializar(obj):
    if isinstance(obj, dict):
        return {k: serializar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serializar(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj
"""Funciones auxiliares compartidas"""
import unicodedata
from datetime import datetime

from bson import ObjectId


def _norm(texto) -> str:
    t = unicodedata.normalize("NFD", str(texto or ""))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


CANTONES_COSTEROS = {
    "Puntarenas", "Esparza", "Montes de Oro", "Osa", "Quepos", "Golfito", "Parrita",
    "Corredores", "Garabito", "Liberia", "Nicoya", "Santa Cruz", "Bagaces", "Carrillo",
    "Cañas", "Abangares", "Nandayure", "La Cruz", "Hojancha", "Limón", "Pococí",
    "Siquirres", "Talamanca", "Matina", "Guácimo",
}

CANTONES_MONTANOSOS = {
    "Tarrazú", "Aserrí", "Mora", "Acosta", "Turrubares", "Dota", "Pérez Zeledón",
    "León Cortés", "Puriscal", "San Ramón", "Zarcero", "Poás", "Valverde Vega",
    "Paraíso", "Jiménez", "Turrialba", "Alvarado", "Oreamuno", "El Guarco", "Barva",
    "Santa Bárbara", "San Rafael", "San Isidro", "Tilarán", "Buenos Aires", "Coto Brus",
}

POBLADOS_INSULARES = {
    "Isla del Coco", "Isla Chira", "Isla Venado", "Isla Caballo", "Isla San Lucas",
    "Isla Tortuga", "Isla Cedros", "Isla Jesucita", "Isla Berrugate",
}

_COSTEROS = {_norm(x) for x in CANTONES_COSTEROS}
_MONTANOSOS = {_norm(x) for x in CANTONES_MONTANOSOS}
_INSULARES = {_norm(x) for x in POBLADOS_INSULARES}


def clasificar_tipo_zona(provincia: str, canton: str, poblado: str) -> str:
    if _norm(poblado) in _INSULARES:
        return "Insular"
    if _norm(canton) in _COSTEROS:
        return "Costera"
    if _norm(canton) in _MONTANOSOS:
        return "Montañosa"
    return "Urbana"


MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def nombre_mes(numero: int) -> str:
    return MESES[numero - 1]


def formatear_fecha(fecha: datetime) -> str:
    if not isinstance(fecha, datetime):
        return str(fecha)
    return f"{fecha.day} de {nombre_mes(fecha.month)} de {fecha.year}, {fecha:%H:%M}"


def parsear_fecha(texto: str) -> datetime:
    texto = texto.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DD HH:MM")


def serializar(obj):
    if isinstance(obj, dict):
        return {k: serializar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serializar(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

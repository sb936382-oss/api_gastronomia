from datetime import date, datetime, time
from decimal import Decimal

from bson.codec_options import CodecOptions, TypeCodec, TypeEncoder, TypeRegistry
from bson.decimal128 import Decimal128
from pymongo import MongoClient, ReturnDocument
from pymongo.database import Database

from app.core.k_config import k_config


class KDecimalCodec(TypeCodec):
    """Guarda los Decimal de Python como Decimal128 (precios, cantidades) y los lee de nuevo como Decimal."""

    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, k_valor: Decimal) -> Decimal128:
        return Decimal128(k_valor)

    def transform_bson(self, k_valor: Decimal128) -> Decimal:
        return k_valor.to_decimal()


class KFechaEncoder(TypeEncoder):
    """MongoDB no tiene tipo fecha sin hora: un date se guarda como datetime a las 00:00."""

    python_type = date

    def transform_python(self, k_valor: date) -> datetime:
        return datetime.combine(k_valor, time.min)


k_opciones = CodecOptions(type_registry=TypeRegistry([KDecimalCodec(), KFechaEncoder()]))

# Usuario de la API con rol readWrite (database/01_mongo_estructura.js), nunca root
k_cliente_mongo = MongoClient(k_config.k_mongo_uri, serverSelectionTimeoutMS=5000)
k_db_mongo = k_cliente_mongo.get_database(k_config.k_mongo_db, codec_options=k_opciones)


def k_obtener_db() -> Database:
    """Base de datos MongoDB de la API (única base de datos del proyecto)."""
    return k_db_mongo


def k_siguiente_id(k_db: Database, k_nombre: str) -> int:
    """Id entero autoincremental: la colección contadores guarda el último id usado por cada colección."""
    k_contador = k_db["contadores"].find_one_and_update({"_id": k_nombre}, {"$inc": {"secuencia": 1}},
                                                       upsert=True, return_document=ReturnDocument.AFTER)
    return k_contador["secuencia"]

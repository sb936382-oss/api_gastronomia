import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()


class KConfig:
    """Configuración leída desde variables de entorno (.env)."""

    k_mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    k_mongo_db = os.getenv("MONGO_DB", "bd_gastronomia")
    k_jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    k_jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    k_jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


k_config = KConfig()

if not k_config.k_jwt_secret:
    raise RuntimeError("Falta JWT_SECRET_KEY en el archivo .env")

# Colombia no tiene horario de verano: America/Bogota = UTC-5 todo el año
K_ZONA_BOGOTA = timezone(timedelta(hours=-5), "America/Bogota")


def k_ahora() -> datetime:
    """Fecha y hora actual de Bogotá (sin tzinfo, así se guarda en MongoDB)."""
    return datetime.now(K_ZONA_BOGOTA).replace(tzinfo=None, microsecond=0)

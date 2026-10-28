from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, PlainSerializer

# Los Decimal (Decimal128 en MongoDB) se devuelven como número en el JSON (no como texto)
KDecimal = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class KError(BaseModel):
    detail: str


class KEliminacionSalida(BaseModel):
    mensaje: str
    borrado_logico: bool = False

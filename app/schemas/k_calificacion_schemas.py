from pydantic import BaseModel, Field


class KProductoCalificadoEntrada(BaseModel):
    id_producto: int = Field(gt=0, examples=[4])
    calificacion: int = Field(ge=1, le=5, examples=[5])


class KCalificacionCrear(BaseModel):
    id_pedido: int = Field(gt=0, examples=[1])
    id_cliente: int = Field(gt=0, examples=[1])
    calificacion_servicio: int = Field(ge=1, le=5, examples=[5])
    comentario: str | None = Field(None, max_length=500, examples=["Excelente atención y buen sabor"])
    productos: list[KProductoCalificadoEntrada] = Field(min_length=1)


class KCalificacionActualizar(BaseModel):
    calificacion_servicio: int | None = Field(None, ge=1, le=5)
    comentario: str | None = Field(None, max_length=500)
    productos: list[KProductoCalificadoEntrada] | None = Field(None, min_length=1)


class KProductoCalificadoSalida(BaseModel):
    id_producto: int
    nombre: str
    calificacion: int


class KCalificacionSalida(BaseModel):
    id: str
    id_pedido: int
    id_cliente: int
    fecha: str
    calificacion_servicio: int
    comentario: str | None = None
    productos: list[KProductoCalificadoSalida]


class KCalificacionDeProducto(BaseModel):
    id: str
    id_pedido: int
    id_cliente: int
    fecha: str
    calificacion: int
    comentario: str | None = None


class KCalificacionesProductoSalida(BaseModel):
    id_producto: int
    nombre: str
    promedio: float
    total_calificaciones: int
    calificaciones: list[KCalificacionDeProducto]

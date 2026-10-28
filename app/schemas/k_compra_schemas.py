from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.k_enums import KEstado
from app.schemas.k_comun_schemas import KDecimal


# ---------- Proveedores ----------
class KProveedorCrear(BaseModel):
    nit: str = Field(min_length=5, max_length=20, examples=["901555444-1"])
    razon_social: str = Field(min_length=1, max_length=120, examples=["Lácteos del Huila SAS"])
    telefono: str | None = Field(None, max_length=20, examples=["3201234567"])
    correo: EmailStr | None = Field(None, max_length=120, examples=["ventas@lacteoshuila.com"])
    direccion: str | None = Field(None, max_length=150, examples=["Calle 8 # 5-20, Neiva"])
    estado: KEstado = KEstado.ACTIVO


class KProveedorActualizar(BaseModel):
    nit: str | None = Field(None, min_length=5, max_length=20)
    razon_social: str | None = Field(None, min_length=1, max_length=120)
    telefono: str | None = Field(None, max_length=20)
    correo: EmailStr | None = Field(None, max_length=120)
    direccion: str | None = Field(None, max_length=150)
    estado: KEstado | None = None


class KProveedorSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_proveedor: int
    nit: str
    razon_social: str
    telefono: str | None
    correo: str | None
    direccion: str | None
    estado: KEstado


# ---------- Compras ----------
class KDetalleCompraEntrada(BaseModel):
    id_insumo: int = Field(gt=0, examples=[3])
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=[20])
    costo_unitario: Decimal = Field(ge=0, max_digits=10, decimal_places=2, examples=[850])


class KCompraCrear(BaseModel):
    numero_factura: str = Field(min_length=1, max_length=30, examples=["FV-2026-0101"])
    fecha_compra: datetime | None = Field(None, description="Si se omite se usa la fecha y hora actual")
    id_proveedor: int = Field(gt=0, examples=[1])
    detalle: list[KDetalleCompraEntrada] = Field(min_length=1)


class KCompraActualizar(BaseModel):
    numero_factura: str | None = Field(None, min_length=1, max_length=30)
    fecha_compra: datetime | None = None
    id_proveedor: int | None = Field(None, gt=0)
    detalle: list[KDetalleCompraEntrada] | None = Field(
        None, min_length=1, description="Si se envía, reemplaza el detalle y ajusta el inventario")


class KDetalleCompraSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle_compra: int
    id_insumo: int
    cantidad: KDecimal
    costo_unitario: KDecimal
    subtotal: KDecimal


class KCompraSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_compra: int
    numero_factura: str
    fecha_compra: datetime
    id_proveedor: int
    id_usuario: int
    total: KDecimal
    detalle: list[KDetalleCompraSalida]

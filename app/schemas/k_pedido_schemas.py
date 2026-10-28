from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.k_enums import KEstado, KEstadoPedido, KTipoCliente, KTipoPedido
from app.schemas.k_comun_schemas import KDecimal


# ---------- Clientes ----------
class KClienteCrear(BaseModel):
    identificacion: str = Field(min_length=5, max_length=20, examples=["1075222333"])
    nombres: str = Field(min_length=1, max_length=80, examples=["Valentina"])
    apellidos: str = Field(min_length=1, max_length=80, examples=["Cabrera Díaz"])
    telefono: str | None = Field(None, max_length=20, examples=["3115556677"])
    correo: EmailStr | None = Field(None, max_length=120, examples=["valentina.cabrera@email.com"])
    tipo_cliente: KTipoCliente
    estado: KEstado = KEstado.ACTIVO


class KClienteActualizar(BaseModel):
    identificacion: str | None = Field(None, min_length=5, max_length=20)
    nombres: str | None = Field(None, min_length=1, max_length=80)
    apellidos: str | None = Field(None, min_length=1, max_length=80)
    telefono: str | None = Field(None, max_length=20)
    correo: EmailStr | None = Field(None, max_length=120)
    tipo_cliente: KTipoCliente | None = None
    estado: KEstado | None = None


class KClienteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    identificacion: str
    nombres: str
    apellidos: str
    telefono: str | None
    correo: str | None
    tipo_cliente: KTipoCliente
    estado: KEstado


# ---------- Pedidos ----------
class KDetallePedidoEntrada(BaseModel):
    """RN01: el cliente solo envía producto y cantidad; precio y subtotal los calcula la API."""

    id_producto: int = Field(gt=0, examples=[13])
    cantidad: int = Field(gt=0, examples=[2])


class KPedidoCrear(BaseModel):
    id_cliente: int = Field(gt=0, examples=[1])
    tipo_pedido: KTipoPedido
    observaciones: str | None = Field(None, examples=["Mesa 4 - sin azúcar"])
    detalle: list[KDetallePedidoEntrada] = Field(min_length=1)


class KPedidoActualizar(BaseModel):
    id_cliente: int | None = Field(None, gt=0)
    tipo_pedido: KTipoPedido | None = None
    observaciones: str | None = None
    detalle: list[KDetallePedidoEntrada] | None = Field(None, min_length=1)


class KPedidoEstadoEntrada(BaseModel):
    estado: KEstadoPedido


class KDetallePedidoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle: int
    id_producto: int
    cantidad: int
    precio_unitario: KDecimal
    subtotal: KDecimal


class KPedidoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    fecha_pedido: datetime
    id_cliente: int
    id_usuario: int
    tipo_pedido: KTipoPedido
    estado: KEstadoPedido
    total: KDecimal
    observaciones: str | None
    detalle: list[KDetallePedidoSalida]


# ---------- Reportes ----------
class KReporteVentasSalida(BaseModel):
    desde: date
    hasta: date
    numero_pedidos: int
    total_vendido: KDecimal


class KProductoMasVendidoSalida(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    cantidad_vendida: int
    total_vendido: KDecimal

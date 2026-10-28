from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.k_enums import KEstado, KEstadoProducto, KUnidadMedida
from app.schemas.k_comun_schemas import KDecimal


# ---------- Categorías ----------
class KCategoriaCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=60, examples=["Panadería"])
    descripcion: str | None = Field(None, max_length=200, examples=["Pan artesanal horneado en la unidad"])
    estado: KEstado = KEstado.ACTIVO


class KCategoriaActualizar(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=60)
    descripcion: str | None = Field(None, max_length=200)
    estado: KEstado | None = None


class KCategoriaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria: int
    nombre: str
    descripcion: str | None
    estado: KEstado


# ---------- Productos ----------
class KProductoCrear(BaseModel):
    codigo: str = Field(min_length=1, max_length=20, examples=["PAN001"])
    nombre: str = Field(min_length=1, max_length=100, examples=["Pan de bono"])
    descripcion: str | None = Field(None, examples=["Pan de bono horneado con queso costeño"])
    precio_venta: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=[2500])
    unidad_venta: str = Field("porcion", min_length=1, max_length=20, examples=["unidad"])
    id_categoria: int = Field(gt=0, examples=[7])
    estado: KEstadoProducto = KEstadoProducto.DISPONIBLE


class KProductoActualizar(BaseModel):
    codigo: str | None = Field(None, min_length=1, max_length=20)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    descripcion: str | None = None
    precio_venta: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    unidad_venta: str | None = Field(None, min_length=1, max_length=20)
    id_categoria: int | None = Field(None, gt=0)
    estado: KEstadoProducto | None = None


class KProductoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    codigo: str
    nombre: str
    descripcion: str | None
    precio_venta: KDecimal
    unidad_venta: str
    id_categoria: int
    estado: KEstadoProducto


# ---------- Insumos ----------
class KInsumoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100, examples=["Queso costeño"])
    unidad_medida: KUnidadMedida = Field(examples=["kg"])
    stock_actual: Decimal = Field(0, ge=0, max_digits=10, decimal_places=2, examples=[10])
    stock_minimo: Decimal = Field(0, ge=0, max_digits=10, decimal_places=2, examples=[3])
    costo_unitario: Decimal = Field(0, ge=0, max_digits=10, decimal_places=2, examples=[18000])
    fecha_vencimiento: date | None = Field(None, examples=["2026-12-31"])
    estado: KEstado = KEstado.ACTIVO


class KInsumoActualizar(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)
    unidad_medida: KUnidadMedida | None = None
    stock_actual: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    stock_minimo: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    costo_unitario: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    fecha_vencimiento: date | None = None
    estado: KEstado | None = None


class KInsumoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_insumo: int
    nombre: str
    unidad_medida: KUnidadMedida
    stock_actual: KDecimal
    stock_minimo: KDecimal
    costo_unitario: KDecimal
    fecha_vencimiento: date | None
    estado: KEstado


class KInsumoPorVencerSalida(KInsumoSalida):
    dias_para_vencer: int


# ---------- Recetas (ficha técnica) ----------
class KRecetaCrear(BaseModel):
    id_producto: int = Field(gt=0, examples=[14])
    id_insumo: int = Field(gt=0, examples=[3])
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=3, examples=[0.05])


class KRecetaActualizar(BaseModel):
    id_insumo: int | None = Field(None, gt=0)
    cantidad: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=3)


class KRecetaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_receta: int
    id_producto: int
    id_insumo: int
    cantidad: KDecimal


class KRecetaDetalleSalida(BaseModel):
    id_receta: int
    id_insumo: int
    nombre_insumo: str
    unidad_medida: KUnidadMedida
    cantidad: KDecimal
    costo_unitario: KDecimal
    costo: KDecimal


class KRecetaProductoSalida(BaseModel):
    id_producto: int
    nombre: str
    insumos: list[KRecetaDetalleSalida]


class KCostoProductoSalida(BaseModel):
    id_producto: int
    nombre: str
    precio_venta: KDecimal
    costo_produccion: KDecimal
    margen: KDecimal
    margen_porcentaje: KDecimal
    insumos: list[KRecetaDetalleSalida]

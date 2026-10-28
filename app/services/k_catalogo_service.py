from decimal import Decimal

from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.k_config import k_ahora
from app.models.k_enums import KEstado, KEstadoProducto
from app.repositories.k_base_repository import KRepositorioBase
from app.repositories.k_insumo_repository import KInsumoRepository
from app.repositories.k_producto_repository import KProductoRepository
from app.schemas.k_catalogo_schemas import (
    KCategoriaActualizar, KCategoriaCrear, KCostoProductoSalida, KInsumoActualizar, KInsumoCrear,
    KInsumoPorVencerSalida, KInsumoSalida, KProductoActualizar, KProductoCrear, KRecetaActualizar,
    KRecetaCrear, KRecetaDetalleSalida, KRecetaProductoSalida,
)
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_validaciones import k_obtener_o_404, k_validar_unico

K_CENTAVOS = Decimal("0.01")


class KCategoriaService:
    def __init__(self, k_db: Database):
        self.k_repo = KRepositorioBase(k_db, "categorias", "id_categoria")

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Categoría")

    def k_crear(self, k_datos: KCategoriaCrear) -> dict:
        k_validar_unico(self.k_repo, "nombre", k_datos.nombre)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KCategoriaActualizar) -> dict:
        k_categoria = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "nombre", k_cambios.get("nombre"), k_id)
        return self.k_repo.k_actualizar(k_categoria, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        k_categoria = self.k_obtener(k_id)
        if self.k_repo.k_tiene_registros("productos", {"id_categoria": k_id}):
            self.k_repo.k_actualizar(k_categoria, {"estado": KEstado.INACTIVO})
            return KEliminacionSalida(mensaje="La categoría tiene productos asociados; "
                                              "se cambió su estado a INACTIVO", borrado_logico=True)
        self.k_repo.k_eliminar(k_categoria)
        return KEliminacionSalida(mensaje="Categoría eliminada")


class KProductoService:
    def __init__(self, k_db: Database):
        self.k_repo = KProductoRepository(k_db)
        self.k_repo_categoria = KRepositorioBase(k_db, "categorias", "id_categoria")

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_listar_por_categoria(self, k_id_categoria: int) -> list[dict]:
        k_obtener_o_404(self.k_repo_categoria, k_id_categoria, "Categoría")
        return self.k_repo.k_listar(id_categoria=k_id_categoria)

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Producto")

    def k_validar_categoria(self, k_id_categoria: int | None) -> None:
        if k_id_categoria is None:
            return
        k_categoria = k_obtener_o_404(self.k_repo_categoria, k_id_categoria, "Categoría")
        if k_categoria["estado"] != KEstado.ACTIVO:
            raise HTTPException(status.HTTP_409_CONFLICT, "La categoría está INACTIVA")

    def k_crear(self, k_datos: KProductoCrear) -> dict:
        k_validar_unico(self.k_repo, "codigo", k_datos.codigo)
        self.k_validar_categoria(k_datos.id_categoria)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KProductoActualizar) -> dict:
        k_producto = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "codigo", k_cambios.get("codigo"), k_id)
        self.k_validar_categoria(k_cambios.get("id_categoria"))
        return self.k_repo.k_actualizar(k_producto, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        """RN04: si el producto tiene pedidos asociados se inactiva en lugar de borrarse."""
        k_producto = self.k_obtener(k_id)
        if self.k_repo.k_tiene_registros("pedidos", {"detalle.id_producto": k_id}):
            self.k_repo.k_actualizar(k_producto, {"estado": KEstadoProducto.INACTIVO})
            return KEliminacionSalida(mensaje="El producto tiene pedidos asociados; "
                                              "se cambió su estado a INACTIVO (RN04)", borrado_logico=True)
        self.k_repo.k_eliminar(k_producto)
        # Sin pedidos, la receta del producto también se borra (antes lo hacía ON DELETE CASCADE)
        self.k_repo.k_db["recetas"].delete_many({"id_producto": k_id})
        return KEliminacionSalida(mensaje="Producto eliminado")

    def k_detalle_receta(self, k_id: int) -> list[KRecetaDetalleSalida]:
        return [
            KRecetaDetalleSalida(
                id_receta=k_rec["id_receta"], id_insumo=k_rec["id_insumo"], nombre_insumo=k_rec["insumo"]["nombre"],
                unidad_medida=k_rec["insumo"]["unidad_medida"], cantidad=k_rec["cantidad"],
                costo_unitario=k_rec["insumo"]["costo_unitario"],
                costo=(k_rec["cantidad"] * k_rec["insumo"]["costo_unitario"]).quantize(K_CENTAVOS),
            )
            for k_rec in self.k_repo.k_obtener_receta(k_id)
        ]

    def k_obtener_receta(self, k_id: int) -> KRecetaProductoSalida:
        k_producto = self.k_obtener(k_id)
        return KRecetaProductoSalida(id_producto=k_id, nombre=k_producto["nombre"],
                                     insumos=self.k_detalle_receta(k_id))

    def k_calcular_costo(self, k_id: int) -> KCostoProductoSalida:
        """RF06: costo = Σ (cantidad × costo_unitario) de la receta; margen frente al precio de venta."""
        k_producto = self.k_obtener(k_id)
        k_insumos = self.k_detalle_receta(k_id)
        k_costo = sum((k_item.costo for k_item in k_insumos), Decimal("0"))
        k_margen = k_producto["precio_venta"] - k_costo
        return KCostoProductoSalida(
            id_producto=k_id, nombre=k_producto["nombre"], precio_venta=k_producto["precio_venta"],
            costo_produccion=k_costo, margen=k_margen,
            margen_porcentaje=(k_margen / k_producto["precio_venta"] * 100).quantize(K_CENTAVOS),
            insumos=k_insumos,
        )


class KInsumoService:
    def __init__(self, k_db: Database):
        self.k_repo = KInsumoRepository(k_db)

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Insumo")

    def k_crear(self, k_datos: KInsumoCrear) -> dict:
        k_validar_unico(self.k_repo, "nombre", k_datos.nombre)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KInsumoActualizar) -> dict:
        k_insumo = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "nombre", k_cambios.get("nombre"), k_id)
        return self.k_repo.k_actualizar(k_insumo, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        """RN04: si el insumo tiene compras o recetas asociadas se inactiva en lugar de borrarse."""
        k_insumo = self.k_obtener(k_id)
        if (self.k_repo.k_tiene_registros("compras", {"detalle.id_insumo": k_id})
                or self.k_repo.k_tiene_registros("recetas", {"id_insumo": k_id})):
            self.k_repo.k_actualizar(k_insumo, {"estado": KEstado.INACTIVO})
            return KEliminacionSalida(mensaje="El insumo tiene compras o recetas asociadas; "
                                              "se cambió su estado a INACTIVO (RN04)", borrado_logico=True)
        self.k_repo.k_eliminar(k_insumo)
        return KEliminacionSalida(mensaje="Insumo eliminado")

    def k_stock_bajo(self) -> list[dict]:
        return self.k_repo.k_stock_bajo()

    def k_por_vencer(self, k_dias: int) -> list[KInsumoPorVencerSalida]:
        k_hoy = k_ahora().date()
        return [
            KInsumoPorVencerSalida(**KInsumoSalida.model_validate(k_insumo).model_dump(),
                                   dias_para_vencer=(k_insumo["fecha_vencimiento"] - k_hoy).days)
            for k_insumo in self.k_repo.k_por_vencer(k_hoy, k_dias)
        ]


class KRecetaService:
    def __init__(self, k_db: Database):
        self.k_repo = KRepositorioBase(k_db, "recetas", "id_receta")
        self.k_repo_producto = KRepositorioBase(k_db, "productos", "id_producto")
        self.k_repo_insumo = KRepositorioBase(k_db, "insumos", "id_insumo")

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Receta")

    def k_validar_insumo_unico(self, k_id_producto: int, k_id_insumo: int, k_id_actual: int | None = None) -> None:
        k_obtener_o_404(self.k_repo_insumo, k_id_insumo, "Insumo")
        k_existente = self.k_repo.k_buscar_por(id_producto=k_id_producto, id_insumo=k_id_insumo)
        if k_existente is not None and k_existente["id_receta"] != k_id_actual:
            raise HTTPException(status.HTTP_409_CONFLICT, "El insumo ya está en la receta de este producto")

    def k_crear(self, k_datos: KRecetaCrear) -> dict:
        k_obtener_o_404(self.k_repo_producto, k_datos.id_producto, "Producto")
        self.k_validar_insumo_unico(k_datos.id_producto, k_datos.id_insumo)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KRecetaActualizar) -> dict:
        k_receta = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        if "id_insumo" in k_cambios:
            self.k_validar_insumo_unico(k_receta["id_producto"], k_cambios["id_insumo"], k_id)
        return self.k_repo.k_actualizar(k_receta, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        self.k_repo.k_eliminar(self.k_obtener(k_id))
        return KEliminacionSalida(mensaje="Insumo retirado de la receta")

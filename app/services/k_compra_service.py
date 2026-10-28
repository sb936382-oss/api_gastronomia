from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.k_config import k_ahora
from app.database.k_conexion_mongo import k_siguiente_id
from app.models.k_enums import KEstado
from app.repositories.k_base_repository import KRepositorioBase
from app.repositories.k_insumo_repository import KInsumoRepository
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_compra_schemas import (
    KCompraActualizar, KCompraCrear, KDetalleCompraEntrada, KProveedorActualizar, KProveedorCrear,
)
from app.services.k_validaciones import k_obtener_o_404, k_validar_sin_repetidos, k_validar_unico


class KProveedorService:
    def __init__(self, k_db: Database):
        self.k_repo = KRepositorioBase(k_db, "proveedores", "id_proveedor")
        self.k_repo_compra = KRepositorioBase(k_db, "compras", "id_compra")

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Proveedor")

    def k_crear(self, k_datos: KProveedorCrear) -> dict:
        k_validar_unico(self.k_repo, "nit", k_datos.nit)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KProveedorActualizar) -> dict:
        k_proveedor = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "nit", k_cambios.get("nit"), k_id)
        return self.k_repo.k_actualizar(k_proveedor, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        """RN04: si el proveedor tiene compras se inactiva en lugar de borrarse."""
        k_proveedor = self.k_obtener(k_id)
        if self.k_repo.k_tiene_registros("compras", {"id_proveedor": k_id}):
            self.k_repo.k_actualizar(k_proveedor, {"estado": KEstado.INACTIVO})
            return KEliminacionSalida(mensaje="El proveedor tiene compras registradas; "
                                              "se cambió su estado a INACTIVO (RN04)", borrado_logico=True)
        self.k_repo.k_eliminar(k_proveedor)
        return KEliminacionSalida(mensaje="Proveedor eliminado")

    def k_listar_compras(self, k_id: int) -> list[dict]:
        self.k_obtener(k_id)
        return self.k_repo_compra.k_listar(id_proveedor=k_id)


class KCompraService:
    def __init__(self, k_db: Database):
        self.k_db = k_db
        self.k_repo = KRepositorioBase(k_db, "compras", "id_compra")
        self.k_repo_proveedor = KRepositorioBase(k_db, "proveedores", "id_proveedor")
        self.k_repo_insumo = KInsumoRepository(k_db)

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Compra")

    def k_validar_proveedor(self, k_id_proveedor: int) -> None:
        k_proveedor = k_obtener_o_404(self.k_repo_proveedor, k_id_proveedor, "Proveedor")
        if k_proveedor["estado"] != KEstado.ACTIVO:
            raise HTTPException(status.HTTP_409_CONFLICT, "El proveedor está INACTIVO")

    def k_validar_factura(self, k_id_proveedor: int, k_numero_factura: str, k_id_actual: int | None = None) -> None:
        k_existente = self.k_repo.k_buscar_por(id_proveedor=k_id_proveedor, numero_factura=k_numero_factura)
        if k_existente is not None and k_existente["id_compra"] != k_id_actual:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                f"La factura {k_numero_factura} ya está registrada para este proveedor")

    def k_armar_detalle(self, k_items: list[KDetalleCompraEntrada]) -> tuple[list[dict], Decimal]:
        """El detalle se guarda dentro del documento de la compra (documento embebido)."""
        k_validar_sin_repetidos([k_item.id_insumo for k_item in k_items], "insumos")
        k_detalle, k_total = [], Decimal("0")
        for k_item in k_items:
            k_insumo = k_obtener_o_404(self.k_repo_insumo, k_item.id_insumo, "Insumo")
            if k_insumo["estado"] != KEstado.ACTIVO:
                raise HTTPException(status.HTTP_409_CONFLICT, f"El insumo '{k_insumo['nombre']}' está INACTIVO")
            k_subtotal = k_item.cantidad * k_item.costo_unitario
            k_total += k_subtotal
            k_detalle.append({"id_detalle_compra": k_siguiente_id(self.k_db, "detalle_compra"),
                              "id_insumo": k_item.id_insumo, "cantidad": k_item.cantidad,
                              "costo_unitario": k_item.costo_unitario, "subtotal": k_subtotal})
        return k_detalle, k_total

    def k_mover_inventario(self, k_detalle_anterior: list[dict], k_detalle_nuevo: list[dict]) -> None:
        """RN02: lo comprado suma al stock y actualiza el costo; lo que se quita de una compra resta del stock.
        Primero se valida que ningún insumo quede negativo y solo después se modifica el inventario."""
        k_movimientos: dict[int, Decimal] = defaultdict(Decimal)
        for k_det in k_detalle_anterior:
            k_movimientos[k_det["id_insumo"]] -= k_det["cantidad"]
        for k_det in k_detalle_nuevo:
            k_movimientos[k_det["id_insumo"]] += k_det["cantidad"]
        k_costos = {k_det["id_insumo"]: k_det["costo_unitario"] for k_det in k_detalle_nuevo}

        k_insumos = self.k_repo_insumo.k_obtener_varios(list(k_movimientos))
        for k_id, k_cantidad in k_movimientos.items():
            if k_insumos[k_id]["stock_actual"] + k_cantidad < 0:
                raise HTTPException(status.HTTP_409_CONFLICT,
                                    f"No se puede revertir la compra: el insumo '{k_insumos[k_id]['nombre']}' "
                                    f"quedaría con stock negativo (stock actual {k_insumos[k_id]['stock_actual']})")
        for k_id, k_cantidad in k_movimientos.items():
            self.k_repo_insumo.k_mover_stock(k_id, k_cantidad, k_costos.get(k_id))

    def k_crear(self, k_datos: KCompraCrear, k_usuario: dict) -> dict:
        self.k_validar_proveedor(k_datos.id_proveedor)
        self.k_validar_factura(k_datos.id_proveedor, k_datos.numero_factura)
        k_detalle, k_total = self.k_armar_detalle(k_datos.detalle)
        k_compra = {"numero_factura": k_datos.numero_factura, "fecha_compra": k_datos.fecha_compra or k_ahora(),
                    "id_proveedor": k_datos.id_proveedor, "id_usuario": k_usuario["id_usuario"],
                    "total": k_total, "detalle": k_detalle}
        self.k_mover_inventario([], k_detalle)
        return self.k_repo.k_crear(k_compra)

    def k_actualizar(self, k_id: int, k_datos: KCompraActualizar) -> dict:
        k_compra = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True, exclude={"detalle"})
        if "id_proveedor" in k_cambios:
            self.k_validar_proveedor(k_cambios["id_proveedor"])
        self.k_validar_factura(k_cambios.get("id_proveedor", k_compra["id_proveedor"]),
                               k_cambios.get("numero_factura", k_compra["numero_factura"]), k_id)
        if k_datos.detalle is not None:
            k_cambios["detalle"], k_cambios["total"] = self.k_armar_detalle(k_datos.detalle)
            self.k_mover_inventario(k_compra["detalle"], k_cambios["detalle"])
        return self.k_repo.k_actualizar(k_compra, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        k_compra = self.k_obtener(k_id)
        self.k_mover_inventario(k_compra["detalle"], [])
        self.k_repo.k_eliminar(k_compra)
        return KEliminacionSalida(mensaje="Compra eliminada; se descontó del inventario lo que había ingresado")

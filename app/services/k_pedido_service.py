from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.k_config import k_ahora
from app.database.k_conexion_mongo import k_siguiente_id
from app.models.k_enums import KEstado, KEstadoPedido, KEstadoProducto
from app.repositories.k_base_repository import KRepositorioBase
from app.repositories.k_insumo_repository import KInsumoRepository
from app.repositories.k_pedido_repository import KPedidoRepository
from app.repositories.k_producto_repository import KProductoRepository
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_pedido_schemas import (
    KClienteActualizar, KClienteCrear, KDetallePedidoEntrada, KPedidoActualizar, KPedidoCrear,
    KProductoMasVendidoSalida, KReporteVentasSalida,
)
from app.services.k_validaciones import k_obtener_o_404, k_validar_sin_repetidos, k_validar_unico

K_ESTADOS_FINALES = (KEstadoPedido.ENTREGADO, KEstadoPedido.ANULADO)


class KClienteService:
    def __init__(self, k_db: Database):
        self.k_repo = KRepositorioBase(k_db, "clientes", "id_cliente")
        self.k_repo_pedido = KPedidoRepository(k_db)

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Cliente")

    def k_crear(self, k_datos: KClienteCrear) -> dict:
        k_validar_unico(self.k_repo, "identificacion", k_datos.identificacion)
        return self.k_repo.k_crear(k_datos.model_dump())

    def k_actualizar(self, k_id: int, k_datos: KClienteActualizar) -> dict:
        k_cliente = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "identificacion", k_cambios.get("identificacion"), k_id)
        return self.k_repo.k_actualizar(k_cliente, k_cambios)

    def k_eliminar(self, k_id: int) -> KEliminacionSalida:
        """RN04: si el cliente tiene pedidos se inactiva en lugar de borrarse."""
        k_cliente = self.k_obtener(k_id)
        if self.k_repo.k_tiene_registros("pedidos", {"id_cliente": k_id}):
            self.k_repo.k_actualizar(k_cliente, {"estado": KEstado.INACTIVO})
            return KEliminacionSalida(mensaje="El cliente tiene pedidos registrados; "
                                              "se cambió su estado a INACTIVO (RN04)", borrado_logico=True)
        self.k_repo.k_eliminar(k_cliente)
        return KEliminacionSalida(mensaje="Cliente eliminado")

    def k_listar_pedidos(self, k_id: int) -> list[dict]:
        self.k_obtener(k_id)
        return self.k_repo_pedido.k_listar(id_cliente=k_id)


class KPedidoService:
    def __init__(self, k_db: Database):
        self.k_db = k_db
        self.k_repo = KPedidoRepository(k_db)
        self.k_repo_cliente = KRepositorioBase(k_db, "clientes", "id_cliente")
        self.k_repo_producto = KProductoRepository(k_db)
        self.k_repo_insumo = KInsumoRepository(k_db)

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_listar_por_estado(self, k_estado: KEstadoPedido) -> list[dict]:
        return self.k_repo.k_listar(estado=k_estado)

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Pedido")

    def k_validar_cliente(self, k_id_cliente: int) -> None:
        k_cliente = k_obtener_o_404(self.k_repo_cliente, k_id_cliente, "Cliente")
        if k_cliente["estado"] != KEstado.ACTIVO:
            raise HTTPException(status.HTTP_409_CONFLICT, "El cliente está INACTIVO")

    def k_validar_modificable(self, k_pedido: dict) -> None:
        """RN05: un pedido ENTREGADO o ANULADO no puede modificarse."""
        if k_pedido["estado"] in K_ESTADOS_FINALES:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                f"El pedido está {k_pedido['estado']} y no puede modificarse (RN05)")

    def k_armar_detalle(self, k_items: list[KDetallePedidoEntrada]) -> tuple[list[dict], Decimal]:
        """RN01: subtotal = cantidad × precio_unitario (precio actual del producto); total = Σ subtotales."""
        k_validar_sin_repetidos([k_item.id_producto for k_item in k_items], "productos")
        k_detalle, k_total = [], Decimal("0")
        for k_item in k_items:
            k_producto = k_obtener_o_404(self.k_repo_producto, k_item.id_producto, "Producto")
            if k_producto["estado"] != KEstadoProducto.DISPONIBLE:
                raise HTTPException(status.HTTP_409_CONFLICT,
                                    f"El producto '{k_producto['nombre']}' está {k_producto['estado']}")
            k_subtotal = k_producto["precio_venta"] * k_item.cantidad
            k_total += k_subtotal
            k_detalle.append({"id_detalle": k_siguiente_id(self.k_db, "detalle_pedido"),
                              "id_producto": k_producto["id_producto"], "cantidad": k_item.cantidad,
                              "precio_unitario": k_producto["precio_venta"], "subtotal": k_subtotal})
        return k_detalle, k_total

    def k_crear(self, k_datos: KPedidoCrear, k_usuario: dict) -> dict:
        self.k_validar_cliente(k_datos.id_cliente)
        k_detalle, k_total = self.k_armar_detalle(k_datos.detalle)
        k_pedido = {"fecha_pedido": k_ahora(), "id_cliente": k_datos.id_cliente,
                    "id_usuario": k_usuario["id_usuario"], "tipo_pedido": k_datos.tipo_pedido,
                    "estado": KEstadoPedido.PENDIENTE, "total": k_total,
                    "observaciones": k_datos.observaciones, "detalle": k_detalle}
        return self.k_repo.k_crear(k_pedido)

    def k_actualizar(self, k_id: int, k_datos: KPedidoActualizar) -> dict:
        k_pedido = self.k_obtener(k_id)
        self.k_validar_modificable(k_pedido)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True, exclude={"detalle"})
        if "id_cliente" in k_cambios:
            self.k_validar_cliente(k_cambios["id_cliente"])
        if k_datos.detalle is not None:
            k_cambios["detalle"], k_cambios["total"] = self.k_armar_detalle(k_datos.detalle)
        return self.k_repo.k_actualizar(k_pedido, k_cambios)

    def k_cambiar_estado(self, k_id: int, k_estado: KEstadoPedido) -> dict:
        k_pedido = self.k_obtener(k_id)
        self.k_validar_modificable(k_pedido)
        if k_pedido["estado"] == k_estado:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"El pedido ya está en estado {k_estado.value}")
        if k_estado == KEstadoPedido.ENTREGADO:
            self.k_descontar_inventario(k_pedido)
        return self.k_repo.k_actualizar(k_pedido, {"estado": k_estado})

    def k_descontar_inventario(self, k_pedido: dict) -> None:
        """RN03: al entregar se descuentan los insumos según la receta; 409 si no hay existencias."""
        k_cantidades = {k_det["id_producto"]: k_det["cantidad"] for k_det in k_pedido["detalle"]}
        k_requerido: dict[int, Decimal] = defaultdict(Decimal)
        for k_receta in self.k_repo_producto.k_obtener_recetas_de(list(k_cantidades)):
            k_requerido[k_receta["id_insumo"]] += k_receta["cantidad"] * k_cantidades[k_receta["id_producto"]]
        k_insumos = self.k_repo_insumo.k_obtener_varios(list(k_requerido))
        k_faltantes = [
            f"{k_insumos[k_id]['nombre']} (requiere {k_cant:.3f} {k_insumos[k_id]['unidad_medida']}, "
            f"hay {k_insumos[k_id]['stock_actual']})"
            for k_id, k_cant in k_requerido.items() if k_insumos[k_id]["stock_actual"] < k_cant
        ]
        if k_faltantes:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                "Inventario insuficiente para entregar el pedido: " + "; ".join(k_faltantes))
        for k_id, k_cant in k_requerido.items():
            self.k_repo_insumo.k_mover_stock(k_id, -k_cant)

    def k_anular(self, k_id: int) -> KEliminacionSalida:
        """DELETE de un pedido: se anula (borrado lógico) para conservar el historial de ventas."""
        k_pedido = self.k_obtener(k_id)
        self.k_validar_modificable(k_pedido)
        self.k_repo.k_actualizar(k_pedido, {"estado": KEstadoPedido.ANULADO})
        return KEliminacionSalida(mensaje="Pedido ANULADO", borrado_logico=True)


class KReporteService:
    def __init__(self, k_db: Database):
        self.k_repo = KPedidoRepository(k_db)

    def k_ventas(self, k_desde: date, k_hasta: date) -> KReporteVentasSalida:
        if k_desde > k_hasta:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "La fecha 'desde' no puede ser mayor que 'hasta'")
        k_inicio = datetime.combine(k_desde, time.min)
        k_fin = datetime.combine(k_hasta + timedelta(days=1), time.min)
        k_numero, k_total = self.k_repo.k_resumen_ventas(k_inicio, k_fin)
        return KReporteVentasSalida(desde=k_desde, hasta=k_hasta, numero_pedidos=k_numero, total_vendido=k_total)

    def k_productos_mas_vendidos(self, k_limite: int) -> list[KProductoMasVendidoSalida]:
        return [KProductoMasVendidoSalida(**k_fila) for k_fila in self.k_repo.k_productos_mas_vendidos(k_limite)]

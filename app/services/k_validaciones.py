from typing import Any

from fastapi import HTTPException, status

from app.repositories.k_base_repository import KRepositorioBase


def k_obtener_o_404(k_repo: KRepositorioBase, k_id: int, k_nombre: str):
    k_objeto = k_repo.k_obtener(k_id)
    if k_objeto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{k_nombre} con id {k_id} no encontrado")
    return k_objeto


def k_validar_unico(k_repo: KRepositorioBase, k_campo: str, k_valor: Any, k_id_actual: int | None = None) -> None:
    """409 si ya existe otro registro con el mismo valor en un campo UNIQUE."""
    if k_valor is None:
        return
    k_existente = k_repo.k_buscar_por(**{k_campo: k_valor})
    if k_existente is not None and k_repo.k_id_de(k_existente) != k_id_actual:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ya existe un registro con {k_campo} = '{k_valor}'")


def k_validar_sin_repetidos(k_ids: list[int], k_campo: str) -> None:
    if len(k_ids) != len(set(k_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"El detalle tiene {k_campo} repetidos")

from app.schemas.k_comun_schemas import KError

K_DESCRIPCIONES = {
    400: "Solicitud inválida (no cumple una regla de negocio)",
    401: "Token ausente, inválido o expirado",
    403: "El rol del usuario no tiene permiso para este recurso",
    404: "Recurso no encontrado",
    409: "Conflicto con los datos existentes (duplicado, estado o inventario)",
}


def k_respuestas(*k_codigos: int) -> dict:
    """Documenta en Swagger los códigos de error que puede devolver un endpoint."""
    return {k_codigo: {"model": KError, "description": K_DESCRIPCIONES[k_codigo]} for k_codigo in k_codigos}

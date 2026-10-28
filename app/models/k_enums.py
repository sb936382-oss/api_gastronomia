import enum


class KRol(str, enum.Enum):
    ADMIN = "ADMIN"
    CAJERO = "CAJERO"
    COCINERO = "COCINERO"


class KEstado(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class KEstadoProducto(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"
    AGOTADO = "AGOTADO"
    INACTIVO = "INACTIVO"


class KUnidadMedida(str, enum.Enum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"  # noqa: E741
    lb = "lb"
    unidad = "unidad"


class KTipoCliente(str, enum.Enum):
    APRENDIZ = "APRENDIZ"
    INSTRUCTOR = "INSTRUCTOR"
    FUNCIONARIO = "FUNCIONARIO"
    EXTERNO = "EXTERNO"


class KTipoPedido(str, enum.Enum):
    MESA = "MESA"
    PARA_LLEVAR = "PARA_LLEVAR"
    EVENTO = "EVENTO"


class KEstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    ENTREGADO = "ENTREGADO"
    ANULADO = "ANULADO"


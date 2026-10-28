from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.k_config import k_config
from app.core.k_security import k_cifrar_password, k_crear_token, k_verificar_password
from app.models.k_enums import KEstado
from app.repositories.k_base_repository import KRepositorioBase
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_usuario_schemas import KLoginEntrada, KTokenSalida, KUsuarioActualizar, KUsuarioCrear
from app.services.k_validaciones import k_obtener_o_404, k_validar_unico


class KUsuarioService:
    def __init__(self, k_db: Database):
        self.k_repo = KRepositorioBase(k_db, "usuarios", "id_usuario")

    def k_login(self, k_datos: KLoginEntrada) -> KTokenSalida:
        k_usuario = self.k_repo.k_buscar_por(correo=k_datos.correo)
        if k_usuario is None or not k_verificar_password(k_datos.password, k_usuario["password"]):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")
        if k_usuario["estado"] != KEstado.ACTIVO:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "El usuario está INACTIVO")
        return KTokenSalida(access_token=k_crear_token(k_usuario),
                            expira_en_minutos=k_config.k_jwt_expire_minutes, usuario=k_usuario)

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: int) -> dict:
        return k_obtener_o_404(self.k_repo, k_id, "Usuario")

    def k_crear(self, k_datos: KUsuarioCrear) -> dict:
        k_validar_unico(self.k_repo, "identificacion", k_datos.identificacion)
        k_validar_unico(self.k_repo, "correo", k_datos.correo)
        k_usuario = {**k_datos.model_dump(exclude={"password"}), "password": k_cifrar_password(k_datos.password)}
        return self.k_repo.k_crear(k_usuario)

    def k_actualizar(self, k_id: int, k_datos: KUsuarioActualizar) -> dict:
        k_usuario = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude_none=True)
        k_validar_unico(self.k_repo, "identificacion", k_cambios.get("identificacion"), k_id)
        k_validar_unico(self.k_repo, "correo", k_cambios.get("correo"), k_id)
        if "password" in k_cambios:
            k_cambios["password"] = k_cifrar_password(k_cambios["password"])
        return self.k_repo.k_actualizar(k_usuario, k_cambios)

    def k_eliminar(self, k_id: int, k_usuario_sesion: dict) -> KEliminacionSalida:
        k_usuario = self.k_obtener(k_id)
        if k_usuario["id_usuario"] == k_usuario_sesion["id_usuario"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "No puede eliminar su propio usuario")
        if (self.k_repo.k_tiene_registros("pedidos", {"id_usuario": k_id})
                or self.k_repo.k_tiene_registros("compras", {"id_usuario": k_id})):
            self.k_repo.k_actualizar(k_usuario, {"estado": KEstado.INACTIVO})
            return KEliminacionSalida(mensaje="El usuario tiene pedidos o compras registrados; "
                                              "se cambió su estado a INACTIVO", borrado_logico=True)
        self.k_repo.k_eliminar(k_usuario)
        return KEliminacionSalida(mensaje="Usuario eliminado")

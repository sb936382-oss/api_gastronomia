from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.k_enums import KEstado, KRol


class KLoginEntrada(BaseModel):
    correo: EmailStr = Field(examples=["admin@gastronomia.com"])
    password: str = Field(min_length=1, max_length=72, examples=["Admin123*"])


class KUsuarioCrear(BaseModel):
    identificacion: str = Field(min_length=5, max_length=20, examples=["1075000111"])
    nombres: str = Field(min_length=1, max_length=80, examples=["Ana María"])
    apellidos: str = Field(min_length=1, max_length=80, examples=["Pérez Rojas"])
    correo: EmailStr = Field(max_length=120, examples=["ana.perez@gastronomia.com"])
    password: str = Field(min_length=8, max_length=72, examples=["Clave123*"])
    rol: KRol
    estado: KEstado = KEstado.ACTIVO


class KUsuarioActualizar(BaseModel):
    identificacion: str | None = Field(None, min_length=5, max_length=20)
    nombres: str | None = Field(None, min_length=1, max_length=80)
    apellidos: str | None = Field(None, min_length=1, max_length=80)
    correo: EmailStr | None = Field(None, max_length=120)
    password: str | None = Field(None, min_length=8, max_length=72)
    rol: KRol | None = None
    estado: KEstado | None = None


class KUsuarioSalida(BaseModel):
    """RN06: la contraseña nunca se incluye en las respuestas."""

    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    identificacion: str
    nombres: str
    apellidos: str
    correo: str
    rol: KRol
    estado: KEstado


class KTokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en_minutos: int
    usuario: KUsuarioSalida

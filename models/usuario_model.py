
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum
)

from models.base import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id_usuario = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre = Column(
        String(160),
        nullable=False
    )

    nombre_usuario = Column(
        String(60),
        nullable=False,
        unique=True
    )

    contrasena_hash = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        Enum(
            "Administrador",
            "Tecnico",
            name="rol_usuario"
        ),
        nullable=False
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True
    )

    def __repr__(self):
        return (
            f"<Usuario("
            f"id={self.id_usuario}, "
            f"usuario='{self.nombre_usuario}', "
            f"rol='{self.rol}'"
            f")>"
        )

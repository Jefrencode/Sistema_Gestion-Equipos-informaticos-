# MODELO ORM: ESTADOS

from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Estado(Base):

    __tablename__ = "estados"

    # Identificador del estado
    id_estado: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Nombre del estado
    nombre: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    # Descripción opcional
    descripcion: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Tipo de registro al que pertenece
    tipo_registro: Mapped[str] = mapped_column(
        Enum(
            "Reparacion",
            "Mantenimiento",
            name="tipo_registro"
        ),
        nullable=False
    )

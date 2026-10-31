
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ReparacionComponente(Base):
    __tablename__ = "reparacion_componentes"

    # Clave primaria compuesta
    id_reparacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "reparaciones.id_reparacion",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        primary_key=True
    )

    id_componente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "componentes.id_componente",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        primary_key=True
    )

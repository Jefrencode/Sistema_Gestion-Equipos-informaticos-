
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Text,
    Date,
    Numeric,
    ForeignKey,
    Enum,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Mantenimiento(Base):

    __tablename__ = "mantenimientos"

    id_mantenimiento: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_equipo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "equipos.id_equipo",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    id_estado: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "estados.id_estado",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    tipo_mantenimiento: Mapped[str] = mapped_column(
        Enum(
            "Preventivo",
            "Correctivo",
            name="tipo_mantenimiento"
        ),
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    responsable: Mapped[str] = mapped_column(
        String(160),
        nullable=False
    )

    costo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    __table_args__ = (
        CheckConstraint(
            "costo >= 0",
            name="chk_mantenimiento_costo"
        ),
    )

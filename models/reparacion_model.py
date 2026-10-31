
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Integer,
    Date,
    Text,
    Numeric,
    ForeignKey,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Reparacion(Base):

    __tablename__ = "reparaciones"

    # Identificador de la reparación
    id_reparacion: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Equipo al que pertenece la reparación
    id_equipo: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "equipos.id_equipo",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # Diagnóstico asociado (opcional)
    id_diagnostico: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "diagnosticos.id_diagnostico",
            ondelete="SET NULL",
            onupdate="CASCADE"
        ),
        nullable=True
    )

    # Estado de la reparación
    id_estado: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "estados.id_estado",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # Fecha de reparación
    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    # Descripción del trabajo realizado
    trabajo_realizado: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Costo de la reparación
    costo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    # Restricción: el costo no puede ser negativo
    __table_args__ = (
        CheckConstraint(
            "costo >= 0",
            name="chk_reparacion_costo"
        ),
    )

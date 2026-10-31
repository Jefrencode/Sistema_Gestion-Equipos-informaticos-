
from decimal import Decimal

from sqlalchemy import Integer, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Componente(Base):
    __tablename__ = "componentes"

    id_componente: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nombre: Mapped[str] = mapped_column(
        String(120), nullable=False
    )

    categoria: Mapped[str | None] = mapped_column(
        String(80), nullable=True
    )

    marca: Mapped[str | None] = mapped_column(
        String(80), nullable=True
    )

    modelo: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    cantidad: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    costo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

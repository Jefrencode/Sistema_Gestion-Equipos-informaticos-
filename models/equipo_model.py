
from datetime import date

from sqlalchemy import (
    Integer,
    String,
    Text,
    Date,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Equipo(Base):

    # ==========================================
    # 1. NOMBRE DE LA TABLA
    # ==========================================

    __tablename__ = "equipos"

    # ==========================================
    # 2. CLAVE PRIMARIA
    # ==========================================

    id_equipo: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ==========================================
    # 3. CLAVE FORÁNEA
    # ==========================================

    id_cliente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "clientes.id_cliente",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # ==========================================
    # 4. INFORMACIÓN DEL EQUIPO
    # ==========================================

    tipo: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )

    marca: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    modelo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    numero_serie: Mapped[str | None] = mapped_column(
        String(120),
        unique=True,
        nullable=True
    )

    # ==========================================
    # 5. INFORMACIÓN DE RECEPCIÓN
    # ==========================================

    fecha_registro: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    estado_recepcion: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descripcion_problema: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

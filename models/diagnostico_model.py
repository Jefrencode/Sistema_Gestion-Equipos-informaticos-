
from datetime import date

from sqlalchemy import (Integer, Date,Text,ForeignKey)

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Diagnostico(Base):

    # 1. NOMBRE DE LA TABLA

    __tablename__ = "diagnosticos"

    # 2. CLAVE PRIMARIA

    id_diagnostico: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)

    # 3. CLAVE FORÁNEA: EQUIPO

    id_equipo: Mapped[int] = mapped_column(Integer,ForeignKey("equipos.id_equipo",ondelete="RESTRICT",onupdate="CASCADE"),nullable=False)

    # 4. FECHA DEL DIAGNÓSTICO

    fecha: Mapped[date] = mapped_column(Date,nullable=False)

    # 5. INFORMACIÓN DEL DIAGNÓSTICO

    sintoma: Mapped[str] = mapped_column(Text,nullable=False)

    evaluacion: Mapped[str] = mapped_column(Text,nullable=False)

    resultado: Mapped[str] = mapped_column(Text,nullable=False)

    observacion: Mapped[str | None] = mapped_column(Text,nullable=True)

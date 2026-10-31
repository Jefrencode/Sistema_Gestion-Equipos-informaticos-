
from sqlalchemy import Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    cedula: Mapped[str|None] = mapped_column(String(20), unique=True, nullable=True)

    nombre: Mapped[str] = mapped_column(String(80), nullable=False)

    apellido: Mapped[str] = mapped_column(String(80), nullable=False)

    telefono: Mapped[str|None] = mapped_column(String(25))

    correo: Mapped[str|None] = mapped_column(String(120))

    direccion: Mapped[str| None] = mapped_column(String(255))

    tipo_cliente: Mapped[str] = mapped_column(Enum("Particular", "Empresarial"), nullable=False,default="Particular")
    
    observaciones: Mapped[str|None] = mapped_column(Text)


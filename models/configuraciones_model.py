from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base


class ConfiguracionSistema(Base):
    __tablename__ = "configuraciones_sistema"

    # CLAVE PRIMARIA
    id_configuracion = Column(
        Integer,
        primary_key=True,
        autoincrement=False
    )

    # INFORMACIÓN DEL TALLER
    nombre_taller = Column(
        String(160),
        nullable=False
    )

    telefono = Column(
        String(30),
        nullable=True
    )

    correo = Column(
        String(160),
        nullable=True
    )

    direccion = Column(
        String(255),
        nullable=True
    )

    # PREFERENCIAS DEL SISTEMA
    formato_fecha = Column(
        String(20),
        nullable=False,
        default="dd/MM/yyyy"
    )

    confirmar_acciones = Column(
        Boolean,
        nullable=False,
        default=True
    )

    def __repr__(self):
        return (
            f"<ConfiguracionSistema("
            f"id={self.id_configuracion}, "
            f"nombre_taller='{self.nombre_taller}', "
            f"formato_fecha='{self.formato_fecha}'"
            f")>"
        )

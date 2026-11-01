
from sqlalchemy import select, func

from database.connection import SessionLocal

from models.equipo_model import Equipo
from models.diagnostico_model import Diagnostico
from models.reparacion_model import Reparacion
from models.mantenimiento_model import Mantenimiento
from models.estado_model import Estado


class DashboardController:

    # ESTADÍSTICAS GENERALES
    def obtener_estadisticas(self):

        with SessionLocal() as sesion:

            # Total de equipos registrados
            total_equipos = sesion.scalar(
                select(func.count(Equipo.id_equipo))
            ) or 0

            # Total de diagnósticos registrados
            total_diagnosticos = sesion.scalar(
                select(func.count(Diagnostico.id_diagnostico))
            ) or 0

            # Reparaciones en proceso
            reparaciones_proceso = sesion.scalar(
                select(func.count(Reparacion.id_reparacion))
                .join(
                    Estado,
                    Reparacion.id_estado == Estado.id_estado
                )
                .where(
                    Estado.nombre == "En proceso",
                    Estado.tipo_registro == "Reparacion"
                )
            ) or 0

            # Mantenimientos pendientes
            mantenimientos_pendientes = sesion.scalar(
                select(func.count(Mantenimiento.id_mantenimiento))
                .join(
                    Estado,
                    Mantenimiento.id_estado == Estado.id_estado
                )
                .where(
                    Estado.nombre == "Pendiente",
                    Estado.tipo_registro == "Mantenimiento"
                )
            ) or 0

            return {
                "total_equipos": total_equipos,
                "total_diagnosticos": total_diagnosticos,
                "reparaciones_proceso": reparaciones_proceso,
                "mantenimientos_pendientes": mantenimientos_pendientes
            }

    # ÚLTIMOS EQUIPOS REGISTRADOS
    def obtener_equipos_recientes(self, limite=5):

        with SessionLocal() as sesion:

            consulta = (
                select(Equipo)
                .order_by(
                    Equipo.fecha_registro.desc(),
                    Equipo.id_equipo.desc()
                )
                .limit(limite)
            )

            equipos = sesion.scalars(consulta).all()

            return [
                {
                    "codigo": f"EQ-{equipo.id_equipo:03d}",
                    "estado": equipo.estado_recepcion,
                    "tipo": equipo.tipo,
                    "marca": equipo.marca,
                    "modelo": equipo.modelo or ""
                }
                for equipo in equipos
            ]

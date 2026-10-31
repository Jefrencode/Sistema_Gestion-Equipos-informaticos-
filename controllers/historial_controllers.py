
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal

from models.cliente_model import Cliente
from models.equipo_model import Equipo
from models.diagnostico_model import Diagnostico
from models.reparacion_model import Reparacion
from models.mantenimiento_model import Mantenimiento
from models.estado_model import Estado


class HistorialController:

    # ==============================================
    # OBTENER HISTORIAL COMPLETO
    # ==============================================

    def listar_historial(self):

        try:
            with SessionLocal() as sesion:

                historial = []

                # ----------------------------------
                # 1. CLIENTES
                # ----------------------------------

                clientes = sesion.scalars(
                    select(Cliente).order_by(
                        Cliente.id_cliente
                    )
                ).all()

                for cliente in clientes:

                    nombre_cliente = (
                        f"{cliente.nombre} "
                        f"{cliente.apellido}"
                    ).strip()

                    historial.append({
                        "id": cliente.id_cliente,
                        "fecha": None,
                        "tipo": "Clientes",
                        "referencia": (
                            f"Cliente #{cliente.id_cliente}"
                        ),
                        "descripcion": (
                            f"Cliente registrado: "
                            f"{nombre_cliente}"
                        ),
                        "estado": "—"
                    })

                # ----------------------------------
                # 2. EQUIPOS
                # ----------------------------------

                consulta_equipos = (
                    select(Equipo, Cliente)
                    .join(
                        Cliente,
                        Equipo.id_cliente
                        == Cliente.id_cliente
                    )
                )

                equipos = sesion.execute(
                    consulta_equipos
                ).all()

                for equipo, cliente in equipos:

                    nombre_equipo = (
                        f"{equipo.tipo} "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''}"
                    ).strip()

                    propietario = (
                        f"{cliente.nombre} "
                        f"{cliente.apellido}"
                    ).strip()

                    descripcion = (
                        f"Equipo de {propietario}. "
                        f"Problema reportado: "
                        f"{equipo.descripcion_problema or 'No especificado'}"
                    )

                    historial.append({
                        "id": equipo.id_equipo,
                        "fecha": equipo.fecha_registro,
                        "tipo": "Equipos",
                        "referencia": (
                            f"Equipo #{equipo.id_equipo} - "
                            f"{nombre_equipo}"
                        ),
                        "descripcion": descripcion,
                        "estado": (
                            equipo.estado_recepcion or "—"
                        )
                    })

                # ----------------------------------
                # 3. DIAGNÓSTICOS
                # ----------------------------------

                consulta_diagnosticos = (
                    select(Diagnostico, Equipo)
                    .join(
                        Equipo,
                        Diagnostico.id_equipo
                        == Equipo.id_equipo
                    )
                )

                diagnosticos = sesion.execute(
                    consulta_diagnosticos
                ).all()

                for diagnostico, equipo in diagnosticos:

                    nombre_equipo = (
                        f"{equipo.tipo} "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''}"
                    ).strip()

                    descripcion = (
                        f"Síntoma: {diagnostico.sintoma}. "
                        f"Evaluación: {diagnostico.evaluacion}. "
                        f"Resultado: {diagnostico.resultado}."
                    )

                    if diagnostico.observacion:
                        descripcion += (
                            f" Observación: "
                            f"{diagnostico.observacion}"
                        )

                    historial.append({
                        "id": diagnostico.id_diagnostico,
                        "fecha": diagnostico.fecha,
                        "tipo": "Diagnósticos",
                        "referencia": (
                            f"Equipo #{equipo.id_equipo} - "
                            f"{nombre_equipo}"
                        ),
                        "descripcion": descripcion,
                        "estado": "—"
                    })

                # ----------------------------------
                # 4. REPARACIONES
                # ----------------------------------

                consulta_reparaciones = (
                    select(Reparacion, Equipo, Estado)
                    .join(
                        Equipo,
                        Reparacion.id_equipo
                        == Equipo.id_equipo
                    )
                    .join(
                        Estado,
                        Reparacion.id_estado
                        == Estado.id_estado
                    )
                )

                reparaciones = sesion.execute(
                    consulta_reparaciones
                ).all()

                for reparacion, equipo, estado in reparaciones:

                    nombre_equipo = (
                        f"{equipo.tipo} "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''}"
                    ).strip()

                    descripcion = (
                        f"Reparación #{reparacion.id_reparacion}. "
                        f"Trabajo realizado: "
                        f"{reparacion.trabajo_realizado}. "
                        f"Costo: C$ {reparacion.costo:.2f}"
                    )

                    historial.append({
                        "id": reparacion.id_reparacion,
                        "fecha": reparacion.fecha,
                        "tipo": "Reparaciones",
                        "referencia": (
                            f"Equipo #{equipo.id_equipo} - "
                            f"{nombre_equipo}"
                        ),
                        "descripcion": descripcion,
                        "estado": estado.nombre
                    })

                # ----------------------------------
                # 5. MANTENIMIENTOS
                # ----------------------------------

                consulta_mantenimientos = (
                    select(Mantenimiento, Equipo, Estado)
                    .join(
                        Equipo,
                        Mantenimiento.id_equipo
                        == Equipo.id_equipo
                    )
                    .join(
                        Estado,
                        Mantenimiento.id_estado
                        == Estado.id_estado
                    )
                )

                mantenimientos = sesion.execute(
                    consulta_mantenimientos
                ).all()

                for mantenimiento, equipo, estado in mantenimientos:

                    nombre_equipo = (
                        f"{equipo.tipo} "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''}"
                    ).strip()

                    descripcion = (
                        f"Mantenimiento "
                        f"{mantenimiento.tipo_mantenimiento}. "
                        f"{mantenimiento.descripcion}. "
                        f"Responsable: "
                        f"{mantenimiento.responsable}. "
                        f"Costo: C$ {mantenimiento.costo:.2f}"
                    )

                    historial.append({
                        "id": mantenimiento.id_mantenimiento,
                        "fecha": mantenimiento.fecha,
                        "tipo": "Mantenimientos",
                        "referencia": (
                            f"Equipo #{equipo.id_equipo} - "
                            f"{nombre_equipo}"
                        ),
                        "descripcion": descripcion,
                        "estado": estado.nombre
                    })

                # ----------------------------------
                # 6. ORDENAR POR FECHA
                # ----------------------------------

                historial.sort(
                    key=lambda registro: (
                        registro["fecha"] is not None,
                        registro["fecha"] or date.min,
                        registro["id"]
                    ),
                    reverse=True
                )

                return historial

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudo consultar el historial "
                "del sistema."
            ) from error


from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal

from models.diagnostico_model import Diagnostico
from models.equipo_model import Equipo
from models.cliente_model import Cliente


class DiagnosticosController:
    # 1. VALIDAR DATOS DEL DIAGNÓSTICO
    def validar_diagnostico(self, datos):

        # Validar identificador del equipo
        try:
            id_equipo = int(datos.get("id_equipo"))
        except (TypeError, ValueError):
            raise ValueError(
                "Debe seleccionar un equipo válido."
            )

        if id_equipo <= 0:
            raise ValueError(
                "Debe seleccionar un equipo válido."
            )

        # Obtener información del formulario
        fecha = datos.get("fecha")

        sintoma = str(
            datos.get("sintoma") or ""
        ).strip()

        evaluacion = str(
            datos.get("evaluacion") or ""
        ).strip()

        resultado = str(
            datos.get("resultado") or ""
        ).strip()

        observacion = str(
            datos.get("observacion") or ""
        ).strip()

        # Validar fecha
        if (
            not isinstance(fecha, date)
            or isinstance(fecha, datetime)
        ):
            raise ValueError(
                "Debe proporcionar una fecha válida."
            )

        # Validar campos obligatorios
        if not sintoma:
            raise ValueError(
                "Debe ingresar el síntoma del equipo."
            )

        if not evaluacion:
            raise ValueError(
                "Debe ingresar la evaluación realizada."
            )

        if not resultado:
            raise ValueError(
                "Debe ingresar el resultado del diagnóstico."
            )

        # Devolver datos normalizados
        return {
            "id_equipo": id_equipo,
            "fecha": fecha,
            "sintoma": sintoma,
            "evaluacion": evaluacion,
            "resultado": resultado,
            "observacion": observacion or None
        }

    # 2. LISTAR EQUIPOS REGISTRADOS


    def listar_equipos(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Equipo, Cliente)
                    .join(
                        Cliente,
                        Equipo.id_cliente == Cliente.id_cliente
                    )
                    .order_by(Equipo.id_equipo)
                )

                resultados = sesion.execute(
                    consulta
                ).all()

                return [
                    {
                        "id_equipo": equipo.id_equipo,
                        "descripcion": (
                            f"#{equipo.id_equipo} - "
                            f"{equipo.marca} "
                            f"{equipo.modelo or ''} - "
                            f"{cliente.nombre} "
                            f"{cliente.apellido}"
                        )
                    }
                    for equipo, cliente in resultados
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los equipos."
            ) from error


    # 3. REGISTRAR DIAGNÓSTICO


    def registrar_diagnostico(self, datos):

        datos_validados = self.validar_diagnostico(datos)

        try:
            with SessionLocal() as sesion:

                # Verificar existencia del equipo
                equipo = sesion.get(
                    Equipo,
                    datos_validados["id_equipo"]
                )

                if equipo is None:
                    raise ValueError(
                        "El equipo seleccionado no existe."
                    )

                diagnostico = Diagnostico(**datos_validados)

                sesion.add(diagnostico)
                sesion.commit()
                sesion.refresh(diagnostico)

                return diagnostico.id_diagnostico

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el diagnóstico. "
                "Verificá los datos asociados al equipo."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al registrar el diagnóstico."
            ) from error


    # 4. LISTAR DIAGNÓSTICOS

    def listar_diagnosticos(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Diagnostico, Equipo, Cliente)
                    .join(
                        Equipo,
                        Diagnostico.id_equipo == Equipo.id_equipo
                    )
                    .join(
                        Cliente,
                        Equipo.id_cliente == Cliente.id_cliente
                    )
                    .order_by(Diagnostico.id_diagnostico)
                )

                resultados = sesion.execute(
                    consulta
                ).all()

                return [
                    {
                        "id_diagnostico": (
                            diagnostico.id_diagnostico
                        ),
                        "id_equipo": diagnostico.id_equipo,
                        "nombre_equipo": (
                            f"#{equipo.id_equipo} - "
                            f"{equipo.marca} "
                            f"{equipo.modelo or ''}"
                        ),
                        "nombre_cliente": (
                            f"{cliente.nombre} "
                            f"{cliente.apellido}"
                        ),
                        "fecha": diagnostico.fecha,
                        "sintoma": diagnostico.sintoma,
                        "evaluacion": diagnostico.evaluacion,
                        "resultado": diagnostico.resultado,
                        "observacion": diagnostico.observacion
                    }
                    for diagnostico, equipo, cliente in resultados
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los diagnósticos."
            ) from error

    # 5. ACTUALIZAR DIAGNÓSTICO


    def actualizar_diagnostico(
        self,
        id_diagnostico,
        datos
    ):

        datos_validados = self.validar_diagnostico(datos)

        try:
            with SessionLocal() as sesion:

                diagnostico = sesion.get(
                    Diagnostico,
                    id_diagnostico
                )

                if diagnostico is None:
                    raise ValueError(
                        "El diagnóstico seleccionado no existe."
                    )

                equipo = sesion.get(
                    Equipo,
                    datos_validados["id_equipo"]
                )

                if equipo is None:
                    raise ValueError(
                        "El equipo seleccionado no existe."
                    )

                # Actualizar los atributos del objeto ORM
                for campo, valor in datos_validados.items():
                    setattr(diagnostico, campo, valor)

                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar el diagnóstico."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al actualizar el diagnóstico."
            ) from error


    # 6. ELIMINAR DIAGNÓSTICO

    def eliminar_diagnostico(self, id_diagnostico):

        try:
            with SessionLocal() as sesion:

                diagnostico = sesion.get(
                    Diagnostico,
                    id_diagnostico
                )

                if diagnostico is None:
                    raise ValueError(
                        "El diagnóstico seleccionado no existe."
                    )

                sesion.delete(diagnostico)
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar este diagnóstico "
                "porque tiene registros relacionados."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al eliminar el diagnóstico."
            ) from error

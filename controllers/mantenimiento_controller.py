
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal

from models.mantenimiento_model import Mantenimiento
from models.equipo_model import Equipo
from models.cliente_model import Cliente
from models.estado_model import Estado


class MantenimientosController:

    # ==============================================
    # VALIDACIÓN
    # ==============================================

    def validar_mantenimiento(self, datos):

        try:
            id_equipo = int(datos.get("id_equipo"))
            id_estado = int(datos.get("id_estado"))
        except (TypeError, ValueError):
            raise ValueError(
                "Debe seleccionar un equipo y un estado válidos."
            )

        if id_equipo <= 0 or id_estado <= 0:
            raise ValueError(
                "Debe seleccionar un equipo y un estado válidos."
            )

        tipo = str(
            datos.get("tipo_mantenimiento") or ""
        ).strip()

        if tipo not in ("Preventivo", "Correctivo"):
            raise ValueError(
                "El tipo de mantenimiento debe ser "
                "Preventivo o Correctivo."
            )

        fecha = datos.get("fecha")

        if not isinstance(fecha, date):
            raise ValueError(
                "La fecha del mantenimiento no es válida."
            )

        descripcion = str(
            datos.get("descripcion") or ""
        ).strip()

        if not descripcion:
            raise ValueError(
                "Debe ingresar la descripción del mantenimiento."
            )

        responsable = str(
            datos.get("responsable") or ""
        ).strip()

        if not responsable:
            raise ValueError(
                "Debe ingresar el responsable del mantenimiento."
            )

        if len(responsable) > 160:
            raise ValueError(
                "El responsable no puede superar 160 caracteres."
            )

        costo_texto = str(
            datos.get("costo") or ""
        ).strip().replace(",", ".")

        if not costo_texto:
            raise ValueError(
                "Debe ingresar el costo del mantenimiento."
            )

        try:
            costo = Decimal(costo_texto)
        except (InvalidOperation, ValueError):
            raise ValueError(
                "El costo debe ser un número válido."
            )

        if not costo.is_finite() or costo < 0:
            raise ValueError(
                "El costo debe ser un número no negativo."
            )

        if costo > Decimal("99999999.99"):
            raise ValueError(
                "El costo supera el máximo permitido."
            )

        if costo.as_tuple().exponent < -2:
            raise ValueError(
                "El costo admite como máximo dos decimales."
            )

        return {
            "id_equipo": id_equipo,
            "id_estado": id_estado,
            "tipo_mantenimiento": tipo,
            "fecha": fecha,
            "descripcion": descripcion,
            "responsable": responsable,
            "costo": costo
        }

    # ==============================================
    # VERIFICAR RELACIONES
    # ==============================================

    def verificar_relaciones(self, sesion, datos):

        equipo = sesion.get(
            Equipo, datos["id_equipo"]
        )

        if equipo is None:
            raise ValueError(
                "El equipo seleccionado no existe."
            )

        estado = sesion.get(
            Estado, datos["id_estado"]
        )

        if estado is None:
            raise ValueError(
                "El estado seleccionado no existe."
            )

        if estado.tipo_registro != "Mantenimiento":
            raise ValueError(
                "El estado seleccionado no pertenece "
                "al módulo de Mantenimientos."
            )

    # ==============================================
    # LISTAR EQUIPOS
    # ==============================================

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

                equipos = []

                for equipo, cliente in resultados:

                    descripcion = (
                        f"#{equipo.id_equipo} - "
                        f"{equipo.tipo} - "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''} - "
                        f"{cliente.nombre} {cliente.apellido}"
                    )

                    equipos.append({
                        "id_equipo": equipo.id_equipo,
                        "descripcion": descripcion.strip()
                    })

                return equipos

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron cargar los equipos."
            ) from error

    # ==============================================
    # LISTAR ESTADOS DE MANTENIMIENTO
    # ==============================================

    def listar_estados(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Estado)
                    .where(
                        Estado.tipo_registro == "Mantenimiento"
                    )
                    .order_by(Estado.nombre)
                )

                estados = sesion.scalars(
                    consulta
                ).all()

                return [
                    {
                        "id_estado": estado.id_estado,
                        "nombre": estado.nombre
                    }
                    for estado in estados
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron cargar los estados."
            ) from error

    # ==============================================
    # REGISTRAR MANTENIMIENTO
    # ==============================================

    def registrar_mantenimiento(self, datos):

        datos_validados = self.validar_mantenimiento(
            datos
        )

        try:
            with SessionLocal() as sesion:

                self.verificar_relaciones(
                    sesion, datos_validados
                )

                mantenimiento = Mantenimiento(
                    **datos_validados
                )

                sesion.add(mantenimiento)
                sesion.flush()

                id_mantenimiento = (
                    mantenimiento.id_mantenimiento
                )

                sesion.commit()

                return id_mantenimiento

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el mantenimiento. "
                "Verifique los datos relacionados."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al registrar "
                "el mantenimiento."
            ) from error

    # ==============================================
    # LISTAR MANTENIMIENTOS
    # ==============================================

    def listar_mantenimientos(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(
                        Mantenimiento,
                        Equipo,
                        Estado
                    )
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
                    .order_by(
                        Mantenimiento.id_mantenimiento.desc()
                    )
                )

                resultados = sesion.execute(
                    consulta
                ).all()

                mantenimientos = []

                for mantenimiento, equipo, estado in resultados:

                    nombre_equipo = (
                        f"#{equipo.id_equipo} - "
                        f"{equipo.tipo} - "
                        f"{equipo.marca} "
                        f"{equipo.modelo or ''}"
                    )

                    mantenimientos.append({
                        "id_mantenimiento":
                            mantenimiento.id_mantenimiento,

                        "id_equipo":
                            mantenimiento.id_equipo,

                        "id_estado":
                            mantenimiento.id_estado,

                        "nombre_equipo":
                            nombre_equipo.strip(),

                        "tipo_mantenimiento":
                            mantenimiento.tipo_mantenimiento,

                        "fecha":
                            mantenimiento.fecha,

                        "descripcion":
                            mantenimiento.descripcion,

                        "responsable":
                            mantenimiento.responsable,

                        "costo":
                            mantenimiento.costo,

                        "nombre_estado":
                            estado.nombre
                    })

                return mantenimientos

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los mantenimientos."
            ) from error

    # ==============================================
    # OBTENER MANTENIMIENTO
    # ==============================================

    def obtener_mantenimiento(self, id_mantenimiento):

        for mantenimiento in self.listar_mantenimientos():
            if (
                mantenimiento["id_mantenimiento"]
                == id_mantenimiento
            ):
                return mantenimiento

        return None

    # ==============================================
    # ACTUALIZAR MANTENIMIENTO
    # ==============================================

    def actualizar_mantenimiento(
        self, id_mantenimiento, datos
    ):

        datos_validados = self.validar_mantenimiento(
            datos
        )

        try:
            with SessionLocal() as sesion:

                mantenimiento = sesion.get(
                    Mantenimiento,
                    id_mantenimiento
                )

                if mantenimiento is None:
                    raise ValueError(
                        "El mantenimiento seleccionado "
                        "no existe."
                    )

                self.verificar_relaciones(
                    sesion, datos_validados
                )

                for campo, valor in datos_validados.items():
                    setattr(
                        mantenimiento,
                        campo,
                        valor
                    )

                sesion.commit()
                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar el mantenimiento."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al actualizar "
                "el mantenimiento."
            ) from error

    # ==============================================
    # ELIMINAR MANTENIMIENTO
    # ==============================================

    def eliminar_mantenimiento(self, id_mantenimiento):

        try:
            with SessionLocal() as sesion:

                mantenimiento = sesion.get(
                    Mantenimiento,
                    id_mantenimiento
                )

                if mantenimiento is None:
                    raise ValueError(
                        "El mantenimiento seleccionado "
                        "no existe."
                    )

                sesion.delete(mantenimiento)
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar el mantenimiento "
                "porque tiene registros relacionados."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al eliminar "
                "el mantenimiento."
            ) from error

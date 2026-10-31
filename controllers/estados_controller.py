
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from models.estado_model import Estado


class EstadosController:

    # ===========================================
    # VALIDAR DATOS
    # ===========================================

    def validar_estado(self, datos):

        nombre = str(
            datos.get("nombre") or ""
        ).strip()

        descripcion = str(
            datos.get("descripcion") or ""
        ).strip()

        tipo_registro = str(
            datos.get("tipo_registro") or ""
        ).strip()

        if not nombre:
            raise ValueError(
                "Debe ingresar el nombre del estado."
            )

        if len(nombre) > 40:
            raise ValueError(
                "El nombre no puede superar 40 caracteres."
            )

        if len(descripcion) > 255:
            raise ValueError(
                "La descripción no puede superar 255 caracteres."
            )

        if tipo_registro not in (
            "Reparacion",
            "Mantenimiento"
        ):
            raise ValueError(
                "Seleccione un tipo de registro válido."
            )

        return {
            "nombre": nombre,
            "descripcion": descripcion or None,
            "tipo_registro": tipo_registro
        }

    # ===========================================
    # EVITAR DUPLICADOS
    # ===========================================

    def verificar_duplicado(
        self, sesion, nombre, tipo_registro,
        id_excluir=None
    ):

        consulta = select(Estado.id_estado).where(
            func.lower(Estado.nombre) == nombre.lower(),
            Estado.tipo_registro == tipo_registro
        )

        if id_excluir is not None:
            consulta = consulta.where(
                Estado.id_estado != id_excluir
            )

        existente = sesion.scalar(consulta)

        if existente is not None:
            raise ValueError(
                "Ya existe un estado con ese nombre "
                "para el tipo de registro seleccionado."
            )

    # ===========================================
    # REGISTRAR ESTADO
    # ===========================================

    def registrar_estado(self, datos):

        datos_validados = self.validar_estado(datos)

        try:
            with SessionLocal() as sesion:

                self.verificar_duplicado(
                    sesion,
                    datos_validados["nombre"],
                    datos_validados["tipo_registro"]
                )

                estado = Estado(**datos_validados)

                sesion.add(estado)
                sesion.flush()

                id_estado = estado.id_estado

                sesion.commit()

                return id_estado

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el estado. "
                "Compruebe si ya existe."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al registrar el estado."
            ) from error

    # ===========================================
    # LISTAR ESTADOS
    # ===========================================

    def listar_estados(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Estado)
                    .order_by(Estado.id_estado.desc())
                )

                estados = sesion.scalars(consulta).all()

                return [
                    {
                        "id_estado": e.id_estado,
                        "nombre": e.nombre,
                        "descripcion": e.descripcion,
                        "tipo_registro": e.tipo_registro
                    }
                    for e in estados
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los estados."
            ) from error

    # ===========================================
    # OBTENER ESTADO
    # ===========================================

    def obtener_estado(self, id_estado):

        try:
            with SessionLocal() as sesion:

                estado = sesion.get(
                    Estado, id_estado
                )

                if estado is None:
                    return None

                return {
                    "id_estado": estado.id_estado,
                    "nombre": estado.nombre,
                    "descripcion": estado.descripcion,
                    "tipo_registro": estado.tipo_registro
                }

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudo consultar el estado."
            ) from error

    # ===========================================
    # ACTUALIZAR ESTADO
    # ===========================================

    def actualizar_estado(self, id_estado, datos):

        datos_validados = self.validar_estado(datos)

        try:
            with SessionLocal() as sesion:

                estado = sesion.get(
                    Estado, id_estado
                )

                if estado is None:
                    raise ValueError(
                        "El estado seleccionado no existe."
                    )

                # El tipo de registro no se modifica:
                # podría afectar reparaciones o
                # mantenimientos ya relacionados.
                if (
                    estado.tipo_registro
                    != datos_validados["tipo_registro"]
                ):
                    raise ValueError(
                        "No se permite cambiar el tipo "
                        "de un estado existente."
                    )

                self.verificar_duplicado(
                    sesion,
                    datos_validados["nombre"],
                    estado.tipo_registro,
                    id_estado
                )

                estado.nombre = datos_validados["nombre"]
                estado.descripcion = datos_validados["descripcion"]

                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar el estado. "
                "Compruebe si ya existe ese nombre."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al actualizar el estado."
            ) from error

    # ===========================================
    # ELIMINAR ESTADO
    # ===========================================

    def eliminar_estado(self, id_estado):

        try:
            with SessionLocal() as sesion:

                estado = sesion.get(
                    Estado, id_estado
                )

                if estado is None:
                    raise ValueError(
                        "El estado seleccionado no existe."
                    )

                sesion.delete(estado)
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar este estado "
                "porque está siendo utilizado en "
                "reparaciones o mantenimientos."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al eliminar el estado."
            ) from error

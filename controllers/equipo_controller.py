# CONTROLADOR: GESTIÓN DE EQUIPOS
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal

from models.equipo_model import Equipo
from models.cliente_model import Cliente


class EquiposController:

    # ==========================================
    # 1. VALIDAR DATOS DEL EQUIPO
    # ==========================================

    def validar_equipo(self, datos):

        # Validar cliente asociado
        try:
            id_cliente = int(datos.get("id_cliente"))
        except (TypeError, ValueError):
            raise ValueError(
                "Debe seleccionar un cliente válido."
            )

        if id_cliente <= 0:
            raise ValueError(
                "Debe seleccionar un cliente válido."
            )

        # Obtener datos de texto
        tipo = str(datos.get("tipo") or "").strip()
        marca = str(datos.get("marca") or "").strip()
        modelo = str(datos.get("modelo") or "").strip()
        numero_serie = str(
            datos.get("numero_serie") or ""
        ).strip()

        estado_recepcion = str(
            datos.get("estado_recepcion") or ""
        ).strip()

        descripcion_problema = str(
            datos.get("descripcion_problema") or ""
        ).strip()

        fecha_registro = datos.get("fecha_registro")

        # Validar campos obligatorios
        if not tipo:
            raise ValueError(
                "Debe seleccionar el tipo de equipo."
            )

        if not marca:
            raise ValueError(
                "Debe ingresar la marca del equipo."
            )

        if not estado_recepcion:
            raise ValueError(
                "Debe indicar el estado de recepción."
            )

        # Validar longitud según MySQL
        if len(tipo) > 60:
            raise ValueError(
                "El tipo de equipo no puede superar 60 caracteres."
            )

        if len(marca) > 80:
            raise ValueError(
                "La marca no puede superar 80 caracteres."
            )

        if len(modelo) > 100:
            raise ValueError(
                "El modelo no puede superar 100 caracteres."
            )

        if len(numero_serie) > 120:
            raise ValueError(
                "El número de serie no puede superar 120 caracteres."
            )

        if len(estado_recepcion) > 150:
            raise ValueError(
                "El estado de recepción no puede superar 150 caracteres."
            )

        # Validar fecha
        if not isinstance(fecha_registro, date) or isinstance(fecha_registro, datetime):
            raise ValueError("Debe proporcionar una fecha válida.")

        # Devolver datos normalizados
        return {
            "id_cliente": id_cliente,
            "tipo": tipo,
            "marca": marca,
            "modelo": modelo or None,
            "numero_serie": numero_serie or None,
            "fecha_registro": fecha_registro,
            "estado_recepcion": estado_recepcion,
            "descripcion_problema": (
                descripcion_problema or None
            )
        }

    # ==========================================
    # 2. LISTAR CLIENTES
    # ==========================================

    def listar_clientes(self):

        try:
            with SessionLocal() as sesion:

                consulta = select(Cliente).order_by(
                    Cliente.nombre,
                    Cliente.apellido
                )

                clientes = sesion.scalars(
                    consulta
                ).all()

                return [
                    {
                        "id_cliente": cliente.id_cliente,
                        "nombre_completo": (
                            f"{cliente.nombre} "
                            f"{cliente.apellido}"
                        )
                    }
                    for cliente in clientes
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los clientes."
            ) from error

    # ==========================================
    # 3. REGISTRAR EQUIPO
    # ==========================================

    def registrar_equipo(self, datos):

        datos_validados = self.validar_equipo(datos)

        try:
            with SessionLocal() as sesion:

                # Verificar que el cliente exista
                cliente = sesion.get(
                    Cliente,
                    datos_validados["id_cliente"]
                )

                if cliente is None:
                    raise ValueError(
                        "El cliente seleccionado no existe."
                    )

                # Crear objeto ORM
                equipo = Equipo(**datos_validados)

                sesion.add(equipo)
                sesion.commit()
                sesion.refresh(equipo)

                return equipo.id_equipo

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el equipo. "
                "Verificá que el número de serie no esté repetido."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al registrar el equipo."
            ) from error

    # ==========================================
    # 4. LISTAR EQUIPOS
    # ==========================================

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
                        "id_cliente": equipo.id_cliente,
                        "nombre_cliente": (
                            f"{cliente.nombre} "
                            f"{cliente.apellido}"
                        ),
                        "tipo": equipo.tipo,
                        "marca": equipo.marca,
                        "modelo": equipo.modelo,
                        "numero_serie": equipo.numero_serie,
                        "fecha_registro": equipo.fecha_registro,
                        "estado_recepcion": equipo.estado_recepcion,
                        "descripcion_problema": (
                            equipo.descripcion_problema
                        )
                    }
                    for equipo, cliente in resultados
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los equipos."
            ) from error

    # ==========================================
    # 5. ACTUALIZAR EQUIPO
    # ==========================================

    def actualizar_equipo(self, id_equipo, datos):

        datos_validados = self.validar_equipo(datos)

        try:
            with SessionLocal() as sesion:

                equipo = sesion.get(
                    Equipo,
                    id_equipo
                )

                if equipo is None:
                    raise ValueError(
                        "El equipo seleccionado no existe."
                    )

                # Verificar cliente asociado
                cliente = sesion.get(
                    Cliente,
                    datos_validados["id_cliente"]
                )

                if cliente is None:
                    raise ValueError(
                        "El cliente seleccionado no existe."
                    )

                # Actualizar atributos del equipo
                for campo, valor in datos_validados.items():
                    setattr(equipo, campo, valor)

                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar el equipo. "
                "Verificá que el número de serie no esté repetido."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al actualizar el equipo."
            ) from error

    # ==========================================
    # 6. ELIMINAR EQUIPO
    # ==========================================

    def eliminar_equipo(self, id_equipo):

        try:
            with SessionLocal() as sesion:

                equipo = sesion.get(
                    Equipo,
                    id_equipo
                )

                if equipo is None:
                    raise ValueError(
                        "El equipo seleccionado no existe."
                    )

                sesion.delete(equipo)
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar este equipo porque "
                "tiene registros relacionados, como "
                "diagnósticos, reparaciones o mantenimientos."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al eliminar el equipo."
            ) from error

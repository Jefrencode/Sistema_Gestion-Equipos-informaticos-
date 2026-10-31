
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal

from models.cliente_model import Cliente
from models.equipo_model import Equipo
from models.diagnostico_model import Diagnostico
from models.estado_model import Estado
from models.reparacion_model import Reparacion
from models.componente_model import Componente
from models.reparacion_componentes_model import ReparacionComponente


class ReparacionesController:

    # ========================================================
    # 1. VALIDAR DATOS DE REPARACIÓN
    # ========================================================

    def validar_reparacion(self, datos):

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

        # El diagnóstico es opcional.
        id_diagnostico = datos.get("id_diagnostico")

        if id_diagnostico in (None, ""):
            id_diagnostico = None

        else:
            try:
                id_diagnostico = int(id_diagnostico)

            except (TypeError, ValueError):
                raise ValueError(
                    "El diagnóstico seleccionado no es válido."
                )

            if id_diagnostico <= 0:
                raise ValueError(
                    "El diagnóstico seleccionado no es válido."
                )

        # Validar fecha.
        fecha = datos.get("fecha")

        if (
            not isinstance(fecha, date)
            or isinstance(fecha, datetime)
        ):
            raise ValueError(
                "Debe proporcionar una fecha válida."
            )

        # Validar trabajo realizado.
        trabajo = str(
            datos.get("trabajo_realizado") or ""
        ).strip()

        if not trabajo:
            raise ValueError(
                "Debe describir el trabajo realizado."
            )

        # Validar costo con Decimal para evitar
        # problemas de precisión de los números float.
        costo_texto = str(
            datos.get("costo", "")
        ).strip().replace(",", ".")

        if not costo_texto:
            raise ValueError(
                "Debe introducir el costo de la reparación."
            )

        try:
            costo = Decimal(costo_texto)

        except (InvalidOperation, ValueError):
            raise ValueError(
                "El costo debe ser un número válido."
            )

        if not costo.is_finite():
            raise ValueError(
                "El costo debe ser un número finito."
            )

        if costo < 0:
            raise ValueError(
                "El costo no puede ser negativo."
            )

        if costo != costo.quantize(Decimal("0.01")):
            raise ValueError(
                "El costo admite como máximo dos decimales."
            )

        if costo > Decimal("99999999.99"):
            raise ValueError(
                "El costo supera el máximo permitido."
            )

        return {
            "id_equipo": id_equipo,
            "id_diagnostico": id_diagnostico,
            "id_estado": id_estado,
            "fecha": fecha,
            "trabajo_realizado": trabajo,
            "costo": costo
        }

    # ========================================================
    # 2. VALIDAR COMPONENTES
    # ========================================================

    def validar_componentes(
        self, sesion, ids_componentes
    ):

        if ids_componentes is None:
            ids_componentes = []

        if not isinstance(
            ids_componentes, (list, tuple)
        ):
            raise ValueError(
                "La selección de componentes no es válida."
            )

        ids = []

        for valor in ids_componentes:

            # Evitar identificadores booleanos o fraccionarios.
            if isinstance(valor, bool):
                raise ValueError(
                    "Se encontró un componente inválido."
                )

            try:
                id_componente = int(valor)

            except (TypeError, ValueError, OverflowError):
                raise ValueError(
                    "Se encontró un componente inválido."
                )

            if str(valor).strip() != str(id_componente):
                raise ValueError(
                    "Se encontró un componente inválido."
                )

            if id_componente <= 0:
                raise ValueError(
                    "Se encontró un componente inválido."
                )

            ids.append(id_componente)

        # No permitir componentes repetidos.
        if len(ids) != len(set(ids)):
            raise ValueError(
                "No puede agregar dos veces el mismo componente."
            )

        # Comprobar que todos existan.
        for id_componente in ids:

            componente = sesion.get(
                Componente,
                id_componente
            )

            if componente is None:
                raise ValueError(
                    f"El componente #{id_componente} no existe."
                )

        return ids

    # ========================================================
    # 3. VERIFICAR RELACIONES DE LA REPARACIÓN
    # ========================================================

    def verificar_relaciones(self, sesion, datos):

        # Comprobar equipo.
        equipo = sesion.get(
            Equipo,
            datos["id_equipo"]
        )

        if equipo is None:
            raise ValueError(
                "El equipo seleccionado no existe."
            )

        # Comprobar estado.
        estado = sesion.get(
            Estado,
            datos["id_estado"]
        )

        if (
            estado is None
            or estado.tipo_registro != "Reparacion"
        ):
            raise ValueError(
                "Debe seleccionar un estado de reparación válido."
            )

        # Comprobar diagnóstico, si fue seleccionado.
        if datos["id_diagnostico"] is not None:

            diagnostico = sesion.get(
                Diagnostico,
                datos["id_diagnostico"]
            )

            if diagnostico is None:
                raise ValueError(
                    "El diagnóstico seleccionado no existe."
                )

            # El diagnóstico debe pertenecer al equipo.
            if diagnostico.id_equipo != datos["id_equipo"]:
                raise ValueError(
                    "El diagnóstico no pertenece al equipo seleccionado."
                )

    # ========================================================
    # 4. LISTAR EQUIPOS
    # ========================================================

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

    # ========================================================
    # 5. LISTAR DIAGNÓSTICOS POR EQUIPO
    # ========================================================

    def listar_diagnosticos(self, id_equipo):

        if id_equipo is None:
            return []

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Diagnostico)
                    .where(
                        Diagnostico.id_equipo == id_equipo
                    )
                    .order_by(
                        Diagnostico.id_diagnostico.desc()
                    )
                )

                diagnosticos = sesion.scalars(
                    consulta
                ).all()

                return [
                    {
                        "id_diagnostico": d.id_diagnostico,
                        "descripcion": (
                            f"#{d.id_diagnostico} - "
                            f"{d.sintoma[:60]}"
                        )
                    }
                    for d in diagnosticos
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los diagnósticos."
            ) from error

    # ========================================================
    # 6. LISTAR ESTADOS DE REPARACIÓN
    # ========================================================

    def listar_estados(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Estado)
                    .where(
                        Estado.tipo_registro == "Reparacion"
                    )
                    .order_by(Estado.id_estado)
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
                "No se pudieron consultar los estados."
            ) from error

    # ========================================================
    # 7. LISTAR COMPONENTES DEL CATÁLOGO
    # ========================================================

    def listar_componentes(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Componente)
                    .order_by(Componente.nombre)
                )

                componentes = sesion.scalars(
                    consulta
                ).all()

                return [
                    {
                        "id_componente": c.id_componente,
                        "nombre": c.nombre,
                        "categoria": c.categoria,
                        "marca": c.marca,
                        "modelo": c.modelo,
                        "descripcion": c.descripcion,
                        "cantidad": c.cantidad,
                        "costo": c.costo
                    }
                    for c in componentes
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los componentes."
            ) from error

    # ========================================================
    # 8. LISTAR COMPONENTES DE UNA REPARACIÓN
    # ========================================================

    def listar_componentes_reparacion(
        self, id_reparacion
    ):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Componente)
                    .join(
                        ReparacionComponente,
                        Componente.id_componente ==
                        ReparacionComponente.id_componente
                    )
                    .where(
                        ReparacionComponente.id_reparacion ==
                        id_reparacion
                    )
                    .order_by(Componente.nombre)
                )

                componentes = sesion.scalars(
                    consulta
                ).all()

                return [
                    {
                        "id_componente": c.id_componente,
                        "nombre": c.nombre,
                        "marca": c.marca,
                        "modelo": c.modelo
                    }
                    for c in componentes
                ]

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar los componentes "
                "de la reparación."
            ) from error

    # ========================================================
    # 9. GUARDAR ASOCIACIONES DE COMPONENTES
    # ========================================================

    def guardar_asociaciones(
        self, sesion, id_reparacion, ids_componentes
    ):

        ids = self.validar_componentes(
            sesion,
            ids_componentes
        )

        for id_componente in ids:

            relacion = ReparacionComponente(
                id_reparacion=id_reparacion,
                id_componente=id_componente
            )

            sesion.add(relacion)

    # ========================================================
    # 10. REGISTRAR REPARACIÓN
    # ========================================================

    def registrar_reparacion(
        self, datos, ids_componentes=None
    ):

        datos_validados = self.validar_reparacion(datos)

        try:
            with SessionLocal() as sesion:

                # Verificar claves foráneas.
                self.verificar_relaciones(
                    sesion,
                    datos_validados
                )

                # Validar componentes antes de insertar.
                ids = self.validar_componentes(
                    sesion,
                    ids_componentes
                )

                # Crear reparación.
                reparacion = Reparacion(
                    **datos_validados
                )

                sesion.add(reparacion)

                # Obtener ID sin confirmar todavía.
                sesion.flush()

                # Asociar componentes seleccionados.
                self.guardar_asociaciones(
                    sesion,
                    reparacion.id_reparacion,
                    ids
                )

                id_reparacion = reparacion.id_reparacion

                # Una sola transacción.
                sesion.commit()

                return id_reparacion

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar la reparación. "
                "Verifique los datos relacionados."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al registrar la reparación."
            ) from error

    # ========================================================
    # 11. LISTAR TODAS LAS REPARACIONES
    # ========================================================

    def listar_reparaciones(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(
                        Reparacion,
                        Equipo,
                        Estado,
                        Diagnostico
                    )
                    .join(
                        Equipo,
                        Reparacion.id_equipo ==
                        Equipo.id_equipo
                    )
                    .join(
                        Estado,
                        Reparacion.id_estado ==
                        Estado.id_estado
                    )
                    .outerjoin(
                        Diagnostico,
                        Reparacion.id_diagnostico ==
                        Diagnostico.id_diagnostico
                    )
                    .order_by(
                        Reparacion.id_reparacion.desc()
                    )
                )

                resultados = sesion.execute(
                    consulta
                ).all()

                reparaciones = []

                for reparacion, equipo, estado, diagnostico in resultados:

                    nombre_diagnostico = "Sin diagnóstico"

                    if diagnostico is not None:
                        nombre_diagnostico = (
                            f"#{diagnostico.id_diagnostico} - "
                            f"{diagnostico.sintoma[:60]}"
                        )

                    # Consultar componentes asociados.
                    consulta_componentes = (
                        select(Componente)
                        .join(
                            ReparacionComponente,
                            Componente.id_componente ==
                            ReparacionComponente.id_componente
                        )
                        .where(
                            ReparacionComponente.id_reparacion ==
                            reparacion.id_reparacion
                        )
                        .order_by(Componente.nombre)
                    )

                    componentes = sesion.scalars(
                        consulta_componentes
                    ).all()

                    nombres_componentes = [
                        c.nombre for c in componentes
                    ]

                    reparaciones.append({
                        "id_reparacion": reparacion.id_reparacion,
                        "id_equipo": reparacion.id_equipo,
                        "id_diagnostico": reparacion.id_diagnostico,
                        "id_estado": reparacion.id_estado,

                        "nombre_equipo": (
                            f"#{equipo.id_equipo} - "
                            f"{equipo.marca} "
                            f"{equipo.modelo or ''}"
                        ),

                        "nombre_diagnostico": nombre_diagnostico,

                        "nombre_estado": estado.nombre,

                        "fecha": reparacion.fecha,

                        "trabajo_realizado": (
                            reparacion.trabajo_realizado
                        ),

                        "costo": reparacion.costo,

                        "componentes": ", ".join(
                            nombres_componentes
                        ),

                        "ids_componentes": [
                            c.id_componente
                            for c in componentes
                        ]
                    })

                return reparaciones

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudieron consultar las reparaciones."
            ) from error

    # ========================================================
    # 12. OBTENER UNA REPARACIÓN POR ID
    # ========================================================

    def obtener_reparacion(self, id_reparacion):

        reparaciones = self.listar_reparaciones()

        for reparacion in reparaciones:

            if reparacion["id_reparacion"] == id_reparacion:
                return reparacion

        return None

    # ========================================================
    # 13. ACTUALIZAR REPARACIÓN
    # ========================================================

    def actualizar_reparacion(
        self,
        id_reparacion,
        datos,
        ids_componentes=None
    ):

        datos_validados = self.validar_reparacion(datos)

        try:
            with SessionLocal() as sesion:

                reparacion = sesion.get(
                    Reparacion,
                    id_reparacion
                )

                if reparacion is None:
                    raise ValueError(
                        "La reparación seleccionada no existe."
                    )

                # Validar las relaciones.
                self.verificar_relaciones(
                    sesion,
                    datos_validados
                )

                # Validar componentes seleccionados.
                ids = self.validar_componentes(
                    sesion,
                    ids_componentes
                )

                # Actualizar campos.
                for campo, valor in datos_validados.items():
                    setattr(reparacion, campo, valor)

                # Eliminar asociaciones anteriores.
                sesion.execute(
                    delete(ReparacionComponente).where(
                        ReparacionComponente.id_reparacion ==
                        id_reparacion
                    )
                )

                # Insertar asociaciones actuales.
                self.guardar_asociaciones(
                    sesion,
                    id_reparacion,
                    ids
                )

                # Confirmar todos los cambios juntos.
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar la reparación "
                "con sus componentes."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al actualizar la reparación."
            ) from error

    # ========================================================
    # 14. ELIMINAR REPARACIÓN
    # ========================================================

    def eliminar_reparacion(self, id_reparacion):

        try:
            with SessionLocal() as sesion:

                reparacion = sesion.get(
                    Reparacion,
                    id_reparacion
                )

                if reparacion is None:
                    raise ValueError(
                        "La reparación seleccionada no existe."
                    )

                # MySQL eliminará las asociaciones de
                # reparacion_componentes automáticamente
                # por la regla ON DELETE CASCADE.
                sesion.delete(reparacion)

                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar la reparación "
                "porque tiene registros relacionados."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al eliminar la reparación."
            ) from error

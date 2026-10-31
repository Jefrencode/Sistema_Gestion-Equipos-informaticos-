
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from models.componente_model import Componente


class ComponentesController:

    # ==================================================
    # 1. VALIDAR DATOS DEL COMPONENTE
    # ==================================================

    def validar_componente(self, datos):

        nombre = str(datos.get("nombre") or "").strip()
        categoria = str(datos.get("categoria") or "").strip()
        marca = str(datos.get("marca") or "").strip()
        modelo = str(datos.get("modelo") or "").strip()
        descripcion = str(
            datos.get("descripcion") or ""
        ).strip()

        if not nombre:
            raise ValueError(
                "Debe ingresar el nombre del componente."
            )

        if len(nombre) > 120:
            raise ValueError(
                "El nombre no puede superar 120 caracteres."
            )

        if len(categoria) > 80:
            raise ValueError(
                "La categoría no puede superar 80 caracteres."
            )

        if len(marca) > 80:
            raise ValueError(
                "La marca no puede superar 80 caracteres."
            )

        if len(modelo) > 100:
            raise ValueError(
                "El modelo no puede superar 100 caracteres."
            )

        # Cantidad: número entero no negativo.
        cantidad_texto = str(
            datos.get("cantidad", "")
        ).strip()

        if not cantidad_texto.isdecimal():
            raise ValueError(
                "La cantidad debe ser un número entero "
                "igual o mayor que cero."
            )

        cantidad = int(cantidad_texto)

        if cantidad > 2147483647:
            raise ValueError(
                "La cantidad supera el máximo permitido."
            )

        # Costo: Decimal para valores monetarios.
        costo_texto = str(
            datos.get("costo", "")
        ).strip().replace(",", ".")

        if not costo_texto:
            raise ValueError(
                "Debe ingresar el costo del componente."
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

        if costo != costo.quantize(Decimal("0.01")):
            raise ValueError(
                "El costo admite como máximo dos decimales."
            )

        return {
            "nombre": nombre,
            "categoria": categoria or None,
            "marca": marca or None,
            "modelo": modelo or None,
            "descripcion": descripcion or None,
            "cantidad": cantidad,
            "costo": costo
        }

    # ==================================================
    # 2. REGISTRAR COMPONENTE
    # ==================================================

    def registrar_componente(self, datos):

        datos_validados = self.validar_componente(datos)

        try:
            with SessionLocal() as sesion:

                componente = Componente(**datos_validados)

                sesion.add(componente)
                sesion.commit()
                sesion.refresh(componente)

                return componente.id_componente

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el componente."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al registrar "
                "el componente."
            ) from error

    # ==================================================
    # 3. LISTAR COMPONENTES
    # ==================================================

    def listar_componentes(self):

        try:
            with SessionLocal() as sesion:

                consulta = (
                    select(Componente)
                    .order_by(
                        Componente.id_componente.desc()
                    )
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

    # ==================================================
    # 4. OBTENER COMPONENTE POR ID
    # ==================================================

    def obtener_componente(self, id_componente):

        try:
            with SessionLocal() as sesion:

                componente = sesion.get(
                    Componente, id_componente
                )

                if componente is None:
                    return None

                return {
                    "id_componente": componente.id_componente,
                    "nombre": componente.nombre,
                    "categoria": componente.categoria,
                    "marca": componente.marca,
                    "modelo": componente.modelo,
                    "descripcion": componente.descripcion,
                    "cantidad": componente.cantidad,
                    "costo": componente.costo
                }

        except SQLAlchemyError as error:
            raise RuntimeError(
                "No se pudo consultar el componente."
            ) from error

    # ==================================================
    # 5. ACTUALIZAR COMPONENTE
    # ==================================================

    def actualizar_componente(
        self, id_componente, datos
    ):

        datos_validados = self.validar_componente(datos)

        try:
            with SessionLocal() as sesion:

                componente = sesion.get(
                    Componente, id_componente
                )

                if componente is None:
                    raise ValueError(
                        "El componente seleccionado no existe."
                    )

                for campo, valor in datos_validados.items():
                    setattr(componente, campo, valor)

                sesion.commit()
                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar el componente."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al actualizar "
                "el componente."
            ) from error

    # ==================================================
    # 6. ELIMINAR COMPONENTE
    # ==================================================

    def eliminar_componente(self, id_componente):

        try:
            with SessionLocal() as sesion:

                componente = sesion.get(
                    Componente, id_componente
                )

                if componente is None:
                    raise ValueError(
                        "El componente seleccionado no existe."
                    )

                sesion.delete(componente)
                sesion.commit()

                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar este componente "
                "porque está asociado a una reparación."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Error de base de datos al eliminar "
                "el componente."
            ) from error

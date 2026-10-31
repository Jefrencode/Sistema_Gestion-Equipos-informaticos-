
import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from models.cliente_model import Cliente


class ClientesController:

    # 1. VALIDACIONES DEL CLIENTE


    def validar_cliente(self, datos):
        nombre = (datos.get("nombre") or "").strip()
        apellido = (datos.get("apellido") or "").strip()
        cedula = (datos.get("cedula") or "").strip().upper()
        telefono = (datos.get("telefono") or "").strip()
        correo = (datos.get("correo") or "").strip().lower()
        direccion = (datos.get("direccion") or "").strip()
        observaciones = (datos.get("observaciones") or "").strip()
        tipo_cliente = datos.get("tipo_cliente")

        # Validación de nombres y apellidos
        patron_nombre = r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*"

        for campo, valor in [("nombre", nombre),("apellido", apellido)]:
            if not valor:
                raise ValueError(f"El {campo} es obligatorio.")

            if len(valor) > 80:
                raise ValueError(f"El {campo} no puede superar 80 caracteres.")

            if not re.fullmatch(patron_nombre, valor):
                raise ValueError(f"El {campo} contiene caracteres no válidos.")

        # Validación de cédula
        if cedula:
            patron_cedula = r"\d{3}-\d{6}-\d{4}[A-Z]"

            if not re.fullmatch(patron_cedula, cedula):
                raise ValueError("Formato de cédula incorrecto. ""Ejemplo: 001-010101-0001A")

            fecha_texto = cedula[4:10]

            try:
                datetime.strptime(fecha_texto, "%d%m%y")
            except ValueError as error:
                raise ValueError("La fecha contenida en la cédula no es válida.") from error

        # Validación de teléfono
        if telefono:
            if not re.fullmatch(r"[578]\d{7}", telefono):
                raise ValueError("El teléfono debe tener 8 dígitos " "y comenzar con 5, 7 u 8.")

        # Validación de correo electrónico
        if correo:
            patron_correo = r"[^@\s]+@[^@\s]+\.[^@\s]+"

            if (len(correo) > 120 or not re.fullmatch(patron_correo, correo)):
                raise ValueError("Ingrese un correo electrónico válido.")

        # Validación del tipo de cliente
        if tipo_cliente not in ("Particular", "Empresarial"):
            raise ValueError("Seleccione un tipo de cliente válido.")

        # Validación de dirección
        if len(direccion) > 255:
            raise ValueError("La dirección no puede superar 255 caracteres.")

        # Normalización de datos
        datos_limpios = {
            "nombre": nombre,
            "apellido": apellido,
            "cedula": cedula or None,
            "telefono": telefono or None,
            "correo": correo or None,
            "direccion": direccion or None,
            "tipo_cliente": tipo_cliente,
            "observaciones": observaciones or None
        }

        return datos_limpios


    # 2. REGISTRAR CLIENTE

    def registrar_cliente(self, datos):

        # Validar antes de guardar
        datos_validados = self.validar_cliente(datos)

        try:
            with SessionLocal() as sesion:

                # Crear objeto ORM
                cliente = Cliente(**datos_validados)

                # Preparar registro
                sesion.add(cliente)

                # Confirmar cambios en MySQL
                sesion.commit()

                # Actualizar el objeto con datos de MySQL
                sesion.refresh(cliente)

                return cliente.id_cliente

        except IntegrityError as error:
            raise ValueError(
                "No se pudo registrar el cliente. "
                "Verificá si la cédula ya está registrada."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError("Ocurrió un error al guardar el cliente.") from error

    # 3. LISTAR CLIENTES
    
    def listar_clientes(self):
        try:
            with SessionLocal() as sesion:

                consulta = select(Cliente).order_by(Cliente.id_cliente)

                clientes = sesion.scalars(consulta).all()

                return [
                    {
                        "id_cliente": cliente.id_cliente,
                        "cedula": cliente.cedula,
                        "nombre": cliente.nombre,
                        "apellido": cliente.apellido,
                        "telefono": cliente.telefono,
                        "correo": cliente.correo,
                        "direccion": cliente.direccion,
                        "tipo_cliente": cliente.tipo_cliente,
                        "observaciones": cliente.observaciones
                    }
                    for cliente in clientes
                ]

        except SQLAlchemyError as error:
            raise RuntimeError("No se pudieron consultar los clientes.") from error
    
    # ==========================================
    # 4. ACTUALIZAR CLIENTE
    # ==========================================

    def actualizar_cliente(self, id_cliente, datos):
        datos_validados = self.validar_cliente(datos)

        try:
            with SessionLocal() as sesion:
                cliente = sesion.get(Cliente, id_cliente)

                if cliente is None:
                    raise ValueError("El cliente no existe.")

                for campo, valor in datos_validados.items():
                    setattr(cliente, campo, valor)

                sesion.commit()
                return True

        except IntegrityError as error:
            raise ValueError(
                "No se pudo actualizar. "
                "Verificá que la cédula no esté repetida."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al actualizar el cliente."
            ) from error

    # ==========================================
    # 5. ELIMINAR CLIENTE
    # ==========================================

    def eliminar_cliente(self, id_cliente):
        try:
            with SessionLocal() as sesion:
                cliente = sesion.get(Cliente, id_cliente)

                if cliente is None:
                    raise ValueError("El cliente no existe.")

                sesion.delete(cliente)
                sesion.commit()
                return True

        except IntegrityError as error:
            raise ValueError(
                "No se puede eliminar este cliente porque "
                "tiene registros relacionados, como equipos."
            ) from error

        except SQLAlchemyError as error:
            raise RuntimeError(
                "Ocurrió un error al eliminar el cliente."
            ) from error





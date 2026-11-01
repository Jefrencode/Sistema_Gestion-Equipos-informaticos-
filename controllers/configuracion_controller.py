
from sqlalchemy import select, text
from database.connection import SessionLocal
from models.configuraciones_model import ConfiguracionSistema
from models.usuario_model import Usuario


class ConfiguracionController:

    def __init__(self, id_administrador):
        self.id_administrador = id_administrador

    # VERIFICAR PERMISOS DEL ADMINISTRADOR
    def verificar_administrador(self, sesion):
        usuario = sesion.get(Usuario, self.id_administrador)

        if usuario is None:
            raise PermissionError(
                "El usuario autenticado no existe."
            )

        if not usuario.activo:
            raise PermissionError(
                "El usuario se encuentra inactivo."
            )

        if usuario.rol != "Administrador":
            raise PermissionError(
                "No tienes permisos para modificar la configuración."
            )

    # CONSULTAR CONFIGURACIÓN
    def obtener_configuracion(self):
        with SessionLocal() as sesion:
            configuracion = sesion.get(
                ConfiguracionSistema, 1
            )

            if configuracion is None:
                return None

            return {
                "id_configuracion": configuracion.id_configuracion,
                "nombre_taller": configuracion.nombre_taller,
                "telefono": configuracion.telefono or "",
                "correo": configuracion.correo or "",
                "direccion": configuracion.direccion or "",
                "formato_fecha": configuracion.formato_fecha,
                "confirmar_acciones": bool(
                    configuracion.confirmar_acciones
                )
            }

    # GUARDAR O ACTUALIZAR CONFIGURACIÓN
    def guardar_configuracion(self, datos):
        nombre = datos["nombre_taller"].strip()

        if not nombre:
            raise ValueError(
                "El nombre del taller es obligatorio."
            )

        if datos["formato_fecha"] not in (
            "dd/MM/yyyy", "yyyy-MM-dd"
        ):
            raise ValueError(
                "El formato de fecha no es válido."
            )

        if not isinstance(datos["confirmar_acciones"], bool):
            raise ValueError(
                "La preferencia de confirmación no es válida."
            )

        with SessionLocal.begin() as sesion:

            # Comprobar permisos antes de modificar datos
            self.verificar_administrador(sesion)

            configuracion = sesion.get(
                ConfiguracionSistema, 1
            )

            if configuracion is None:
                # Primera configuración del sistema
                configuracion = ConfiguracionSistema(
                    id_configuracion=1,
                    nombre_taller=nombre,
                    telefono=datos["telefono"].strip(),
                    correo=datos["correo"].strip(),
                    direccion=datos["direccion"].strip(),
                    formato_fecha=datos["formato_fecha"],
                    confirmar_acciones=datos["confirmar_acciones"]
                )

                sesion.add(configuracion)

            else:
                # Actualizar configuración existente
                configuracion.nombre_taller = nombre
                configuracion.telefono = datos["telefono"].strip()
                configuracion.correo = datos["correo"].strip()
                configuracion.direccion = datos["direccion"].strip()
                configuracion.formato_fecha = datos["formato_fecha"]
                configuracion.confirmar_acciones = (
                    datos["confirmar_acciones"]
                )

        return True

    # COMPROBAR CONEXIÓN A MYSQL
    def verificar_conexion(self):
        try:
            with SessionLocal() as sesion:
                sesion.execute(text("SELECT 1"))
            return True

        except Exception:
            return False

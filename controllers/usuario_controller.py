
import bcrypt

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from models.usuario_model import Usuario


class UsuarioController:

    ROLES = {
        "Técnico": "Tecnico",
        "Administrador": "Administrador"
    }

    def __init__(self, id_administrador):
        if id_administrador is None:
            raise ValueError(
                "Se requiere una sesión administrativa."
            )

        self.id_administrador = int(id_administrador)

    # ==========================================
    # AUTORIZACIÓN
    # ==========================================

    def verificar_administrador(self, sesion):

        administrador = sesion.get(
            Usuario, self.id_administrador
        )

        if (
            administrador is None
            or not administrador.activo
            or administrador.rol != "Administrador"
        ):
            raise PermissionError(
                "No tienes permisos de administrador "
                "para realizar esta operación."
            )

        return administrador

    # ==========================================
    # CONTRASEÑAS
    # ==========================================

    @staticmethod
    def generar_hash(contrasena):

        if len(contrasena) < 8:
            raise ValueError(
                "La contraseña debe tener al menos "
                "8 caracteres."
            )

        datos = contrasena.encode("utf-8")

        if len(datos) > 72:
            raise ValueError(
                "La contraseña no puede superar "
                "72 bytes en UTF-8."
            )

        return bcrypt.hashpw(
            datos,
            bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def verificar_contrasena(contrasena, hash_guardado):

        try:
            return bcrypt.checkpw(
                contrasena.encode("utf-8"),
                hash_guardado.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False

    # ==========================================
    # VALIDACIONES
    # ==========================================

    def validar_datos(self, nombre, usuario, rol):

        nombre = nombre.strip()
        usuario = usuario.strip()

        if not nombre or not usuario:
            raise ValueError(
                "El nombre y el nombre de usuario "
                "son obligatorios."
            )

        if len(nombre) > 160:
            raise ValueError(
                "El nombre no puede superar "
                "160 caracteres."
            )

        if len(usuario) > 60:
            raise ValueError(
                "El usuario no puede superar "
                "60 caracteres."
            )

        if rol not in self.ROLES:
            raise ValueError(
                "El rol seleccionado no es válido."
            )

        return nombre, usuario, self.ROLES[rol]

    @staticmethod
    def usuario_duplicado(
        sesion, nombre_usuario, excluir_id=None
    ):

        consulta = select(Usuario).where(
            func.lower(Usuario.nombre_usuario)
            == nombre_usuario.casefold()
        )

        if excluir_id is not None:
            consulta = consulta.where(
                Usuario.id_usuario != excluir_id
            )

        return sesion.scalar(consulta) is not None

    @staticmethod
    def contar_administradores_activos(sesion):

        return sesion.scalar(
            select(func.count(Usuario.id_usuario))
            .where(
                Usuario.rol == "Administrador",
                Usuario.activo.is_(True)
            )
        )

    @staticmethod
    def convertir_diccionario(usuario):

        return {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "nombre_usuario": usuario.nombre_usuario,
            "rol": (
                "Técnico"
                if usuario.rol == "Tecnico"
                else "Administrador"
            ),
            "activo": bool(usuario.activo)
        }

    # ==========================================
    # LISTAR USUARIOS
    # ==========================================

    def listar_usuarios(self):

        with SessionLocal() as sesion:

            self.verificar_administrador(sesion)

            usuarios = sesion.scalars(
                select(Usuario).order_by(
                    Usuario.id_usuario.desc()
                )
            ).all()

            return [
                self.convertir_diccionario(usuario)
                for usuario in usuarios
            ]

    # ==========================================
    # REGISTRAR USUARIO
    # ==========================================

    def registrar_usuario(
        self, nombre, nombre_usuario, contrasena, rol
    ):

        nombre, nombre_usuario, rol_bd = (
            self.validar_datos(
                nombre, nombre_usuario, rol
            )
        )

        hash_contrasena = self.generar_hash(
            contrasena
        )

        with SessionLocal() as sesion:

            self.verificar_administrador(sesion)

            if self.usuario_duplicado(
                sesion, nombre_usuario
            ):
                raise ValueError(
                    "Ese nombre de usuario ya existe."
                )

            nuevo_usuario = Usuario(
                nombre=nombre,
                nombre_usuario=nombre_usuario,
                contrasena_hash=hash_contrasena,
                rol=rol_bd,
                activo=True
            )

            sesion.add(nuevo_usuario)

            try:
                sesion.commit()
                sesion.refresh(nuevo_usuario)
            except IntegrityError as error:
                sesion.rollback()
                raise ValueError(
                    "No se pudo registrar: "
                    "el usuario ya existe."
                ) from error

            return nuevo_usuario.id_usuario

    # ==========================================
    # ACTUALIZAR USUARIO
    # ==========================================

    def actualizar_usuario(
        self,
        id_usuario,
        nombre,
        nombre_usuario,
        rol,
        nueva_contrasena=""
    ):

        nombre, nombre_usuario, rol_bd = (
            self.validar_datos(
                nombre, nombre_usuario, rol
            )
        )

        nuevo_hash = None

        if nueva_contrasena:
            nuevo_hash = self.generar_hash(
                nueva_contrasena
            )

        with SessionLocal() as sesion:

            self.verificar_administrador(sesion)

            usuario = sesion.get(
                Usuario, int(id_usuario)
            )

            if usuario is None:
                raise ValueError(
                    "El usuario no existe."
                )

            if self.usuario_duplicado(
                sesion,
                nombre_usuario,
                usuario.id_usuario
            ):
                raise ValueError(
                    "Ese nombre de usuario "
                    "ya pertenece a otra cuenta."
                )

            if (
                usuario.id_usuario
                == self.id_administrador
                and rol_bd != "Administrador"
            ):
                raise ValueError(
                    "No puedes quitarte tu propio "
                    "rol de administrador."
                )

            if (
                usuario.rol == "Administrador"
                and usuario.activo
                and rol_bd != "Administrador"
                and self.contar_administradores_activos(
                    sesion
                ) <= 1
            ):
                raise ValueError(
                    "Debe existir al menos un "
                    "administrador activo."
                )

            usuario.nombre = nombre
            usuario.nombre_usuario = nombre_usuario
            usuario.rol = rol_bd

            if nuevo_hash is not None:
                usuario.contrasena_hash = nuevo_hash

            try:
                sesion.commit()
            except IntegrityError as error:
                sesion.rollback()
                raise ValueError(
                    "No se pudieron guardar los cambios. "
                    "Verifica el nombre de usuario."
                ) from error

    # ==========================================
    # ACTIVAR / DESACTIVAR
    # ==========================================

    def cambiar_estado(self, id_usuario):

        with SessionLocal() as sesion:

            self.verificar_administrador(sesion)

            usuario = sesion.get(
                Usuario, int(id_usuario)
            )

            if usuario is None:
                raise ValueError(
                    "El usuario no existe."
                )

            if (
                usuario.id_usuario
                == self.id_administrador
                and usuario.activo
            ):
                raise ValueError(
                    "No puedes desactivar tu propia cuenta."
                )

            if (
                usuario.rol == "Administrador"
                and usuario.activo
                and self.contar_administradores_activos(
                    sesion
                ) <= 1
            ):
                raise ValueError(
                    "No puedes desactivar al último "
                    "administrador activo."
                )

            usuario.activo = not usuario.activo
            nuevo_estado = bool(usuario.activo)

            sesion.commit()

            return nuevo_estado

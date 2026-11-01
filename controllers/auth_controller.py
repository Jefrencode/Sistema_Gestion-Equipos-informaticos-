import bcrypt

from sqlalchemy import select

from database.connection import SessionLocal
from models.usuario_model import Usuario


class AuthController:

    def iniciar_sesion(self, nombre_usuario, contrasena):

        nombre_usuario = nombre_usuario.strip()

        if not nombre_usuario or not contrasena:
            raise ValueError(
                "Ingresa el usuario y la contraseña."
            )

        with SessionLocal() as sesion:

            usuario = sesion.scalar(
                select(Usuario).where(
                    Usuario.nombre_usuario == nombre_usuario
                )
            )

            if usuario is None:
                return None

            if not usuario.activo:
                return None

            try:
                contrasena_valida = bcrypt.checkpw(
                    contrasena.encode("utf-8"),
                    usuario.contrasena_hash.encode("utf-8")
                )
            except (ValueError, TypeError):
                return None

            if not contrasena_valida:
                return None

            # Devolvemos únicamente los datos
            # necesarios para la sesión.
            # Nunca devolvemos el hash.

            return {
                "id_usuario": usuario.id_usuario,
                "nombre": usuario.nombre,
                "nombre_usuario": usuario.nombre_usuario,
                "rol": usuario.rol
            }

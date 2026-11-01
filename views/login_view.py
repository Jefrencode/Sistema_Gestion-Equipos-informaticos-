from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QMessageBox
)

from controllers.auth_controller import AuthController


class ImagenLogin(QLabel):
    """Imagen adaptable al tamaño de su contenedor."""

    def __init__(self, ruta_imagen):
        super().__init__()

        self.setObjectName("loginImagen")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(300)

        self.imagen_original = QPixmap(str(ruta_imagen))

        if self.imagen_original.isNull():
            self.setText("GESTIÓN DE EQUIPOS\nINFORMÁTICOS")
        else:
            self.actualizar_imagen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.actualizar_imagen()

    def actualizar_imagen(self):
        if self.imagen_original.isNull():
            return

        if self.width() <= 0 or self.height() <= 0:
            return

        imagen = self.imagen_original.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(imagen)


class LoginView(QWidget):

    login_exitoso = Signal(dict)

    def __init__(self):
        super().__init__()

        self.auth_controller = AuthController()

        self.crear_interfaz()
        self.conectar_eventos()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        self.setObjectName("loginWindow")
        self.setWindowTitle("Sistema de Gestión de Equipos")
        self.setMinimumSize(900, 600)

        # Layout principal
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ======================================
        # PANEL IZQUIERDO
        # ======================================

        self.panel_izquierdo = QFrame()
        self.panel_izquierdo.setObjectName("loginPanelIzquierdo")

        layout_izquierdo = QVBoxLayout(self.panel_izquierdo)
        layout_izquierdo.setContentsMargins(35, 35, 35, 35)
        layout_izquierdo.setSpacing(18)

        self.lbl_marca = QLabel("GESTIÓN DE EQUIPOS")
        self.lbl_marca.setObjectName("loginMarca")

        self.lbl_frase = QLabel(
            "Tecnología, diagnóstico y mantenimiento"
        )
        self.lbl_frase.setObjectName("loginFrase")
        self.lbl_frase.setWordWrap(True)

        # Ruta de imagen independiente del directorio
        # desde donde se ejecute main.py.
        ruta_proyecto = Path(__file__).resolve().parent.parent

        ruta_imagen = (
            ruta_proyecto
            / "resourse"
            / "images"
            / "login_background.png"
        )

        self.imagen = ImagenLogin(ruta_imagen)
        self.imagen.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.lbl_descripcion_imagen = QLabel(
            "Una solución integral para administrar "
            "los equipos de tu taller."
        )
        self.lbl_descripcion_imagen.setObjectName(
            "loginDescripcionImagen"
        )
        self.lbl_descripcion_imagen.setWordWrap(True)

        layout_izquierdo.addWidget(self.lbl_marca)
        layout_izquierdo.addWidget(self.lbl_frase)
        layout_izquierdo.addWidget(self.imagen, 1)
        layout_izquierdo.addWidget(self.lbl_descripcion_imagen)

        # ======================================
        # PANEL DERECHO
        # ======================================

        self.panel_derecho = QFrame()
        self.panel_derecho.setObjectName("loginPanelDerecho")

        layout_derecho = QVBoxLayout(self.panel_derecho)
        layout_derecho.setContentsMargins(35, 35, 35, 35)
        layout_derecho.setSpacing(15)

        layout_derecho.addStretch()

        self.frame_login = QFrame()
        self.frame_login.setObjectName("loginCard")
        self.frame_login.setMaximumWidth(480)

        layout_frame = QVBoxLayout(self.frame_login)
        layout_frame.setContentsMargins(38, 40, 38, 40)
        layout_frame.setSpacing(14)

        # Icono superior
        self.lbl_icono = QLabel("")
        self.lbl_icono.setObjectName("loginIcono")
        self.lbl_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Encabezado
        self.lbl_titulo = QLabel("Bienvenido")
        self.lbl_titulo.setObjectName("titulo")
        self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_descripcion = QLabel(
            "Sistema de Gestión de Equipos"
        )
        self.lbl_descripcion.setObjectName("descripcion")
        self.lbl_descripcion.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.lbl_descripcion.setWordWrap(True)

        self.lbl_subtitulo = QLabel("Iniciar sesión")
        self.lbl_subtitulo.setObjectName("subtitulo")

        self.lbl_mensaje = QLabel(
            "Ingresa tus credenciales para continuar"
        )
        self.lbl_mensaje.setObjectName("mensaje")
        self.lbl_mensaje.setWordWrap(True)

        layout_frame.addWidget(self.lbl_icono)
        layout_frame.addWidget(self.lbl_titulo)
        layout_frame.addWidget(self.lbl_descripcion)
        layout_frame.addSpacing(22)
        layout_frame.addWidget(self.lbl_subtitulo)
        layout_frame.addWidget(self.lbl_mensaje)
        layout_frame.addSpacing(12)

        # ======================================
        # USUARIO
        # ======================================

        self.lbl_usuario = QLabel("Usuario")
        self.lbl_usuario.setObjectName("loginLabel")

        self.usuario = QLineEdit()
        self.usuario.setObjectName("campoUsuario")
        self.usuario.setPlaceholderText("Ingresa tu usuario")
        self.usuario.setMaxLength(60)
        self.usuario.setClearButtonEnabled(True)
        self.usuario.setMinimumHeight(48)

        layout_frame.addWidget(self.lbl_usuario)
        layout_frame.addWidget(self.usuario)

        layout_frame.addSpacing(6)

        # ======================================
        # CONTRASEÑA
        # ======================================

        self.lbl_contrasena = QLabel("Contraseña")
        self.lbl_contrasena.setObjectName("loginLabel")

        self.contrasena = QLineEdit()
        self.contrasena.setObjectName("campoContrasena")
        self.contrasena.setPlaceholderText(
            "Ingresa tu contraseña"
        )
        self.contrasena.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.contrasena.setMinimumHeight(48)

        self.btn_mostrar = QPushButton("Mostrar")
        self.btn_mostrar.setObjectName("btnMostrarPassword")
        self.btn_mostrar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout_password = QHBoxLayout()
        layout_password.setSpacing(8)
        layout_password.addWidget(self.contrasena, 1)
        layout_password.addWidget(self.btn_mostrar)

        layout_frame.addWidget(self.lbl_contrasena)
        layout_frame.addLayout(layout_password)

        layout_frame.addSpacing(18)

        # ======================================
        # BOTÓN DE LOGIN
        # ======================================

        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setObjectName("btnLogin")
        self.btn_login.setMinimumHeight(50)
        self.btn_login.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout_frame.addWidget(self.btn_login)

        layout_frame.addSpacing(12)

        # Pie
        self.lbl_footer = QLabel(
            "Acceso exclusivo para personal autorizado"
        )
        self.lbl_footer.setObjectName("footer")
        self.lbl_footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.lbl_footer.setWordWrap(True)

        layout_frame.addWidget(self.lbl_footer)

        # Centrar tarjeta horizontalmente
        layout_tarjeta = QHBoxLayout()
        layout_tarjeta.addStretch()
        layout_tarjeta.addWidget(self.frame_login, 1)
        layout_tarjeta.addStretch()

        layout_derecho.addLayout(layout_tarjeta)

        layout_derecho.addStretch()

        # ======================================
        # DISTRIBUCIÓN GENERAL
        # ======================================

        layout_principal.addWidget(
            self.panel_izquierdo, 1
        )
        layout_principal.addWidget(
            self.panel_derecho, 1
        )

        self.usuario.setFocus()

    # ==========================================
    # EVENTOS
    # ==========================================

    def conectar_eventos(self):

        self.btn_login.clicked.connect(
            self.iniciar_sesion
        )

        self.contrasena.returnPressed.connect(
            self.iniciar_sesion
        )

        self.btn_mostrar.clicked.connect(
            self.alternar_contrasena
        )

    # ==========================================
    # MOSTRAR / OCULTAR CONTRASEÑA
    # ==========================================

    def alternar_contrasena(self):

        if self.contrasena.echoMode() == (
            QLineEdit.EchoMode.Password
        ):
            self.contrasena.setEchoMode(
                QLineEdit.EchoMode.Normal
            )
            self.btn_mostrar.setText("Ocultar")

        else:
            self.contrasena.setEchoMode(
                QLineEdit.EchoMode.Password
            )
            self.btn_mostrar.setText("Mostrar")

    # ==========================================
    # AUTENTICACIÓN
    # ==========================================

    def iniciar_sesion(self):

        if not self.btn_login.isEnabled():
            return

        usuario = self.usuario.text().strip()
        contrasena = self.contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(
                self,
                "Campos obligatorios",
                "Ingresa tu nombre de usuario y contraseña."
            )
            return

        self.btn_login.setEnabled(False)

        try:
            usuario_autenticado = (
                self.auth_controller.iniciar_sesion(
                    usuario,
                    contrasena
                )
            )

            if usuario_autenticado is None:
                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "El usuario o la contraseña son "
                    "incorrectos, o la cuenta está desactivada."
                )

                self.contrasena.clear()
                self.contrasena.setFocus()
                return

            self.contrasena.clear()
            self.usuario.clear()

            self.login_exitoso.emit(
                usuario_autenticado
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error de autenticación",
                "No fue posible verificar las credenciales.\n"
                "Comprueba la conexión con MySQL."
            )

            print(f"Error al iniciar sesión: {error}")

        finally:
            self.btn_login.setEnabled(True)

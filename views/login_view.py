from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QFrame,
    QHBoxLayout,
    QMessageBox
)



class LoginView(QWidget):

    def __init__(self,dashboard):
        super().__init__()

        self.dashboard = dashboard
        self.crear_interfaz()
        self.btn_login.clicked.connect(self.iniciar_sesion)

    def iniciar_sesion(self):

        usuario = self.usuario.text()
        contrasena = self.contrasena.text()

        if usuario == "admin" and contrasena == "1234":

            self.hide()
            self.dashboard.show()

        else:
            QMessageBox.warning(self,"Error"," El usuario y la contraseña es incorrecta.")

    def crear_interfaz(self):

        # Configuración de la ventana
        self.setObjectName("loginWindow")
        self.setWindowTitle("Sistema de Gestión de Equipos")
        self.setMinimumSize(900, 600)

        # CONTENEDOR PRINCIPAL
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)

        # Espaciado superior
        layout_principal.addStretch()


        # TÍTULO
        self.lbl_titulo = QLabel("Sistema de Gestión de Equipos")
        self.lbl_titulo.setObjectName("titulo")
        layout_titulo = QHBoxLayout()
        layout_titulo.addStretch()
        layout_titulo.addWidget(self.lbl_titulo)
        layout_titulo.addStretch()

        layout_principal.addLayout(layout_titulo)

        # DESCRIPCIÓN

        self.lbl_descripcion = QLabel("Diagnóstico, reparación y mantenimiento")

        self.lbl_descripcion.setObjectName("descripcion")

        layout_descripcion = QHBoxLayout()
        layout_descripcion.addStretch()
        layout_descripcion.addWidget(self.lbl_descripcion)
        layout_descripcion.addStretch()

        layout_principal.addLayout(layout_descripcion)

        # Espacio
        layout_principal.addSpacing(25)

        # FRAME DEL LOGIN
        self.frame_login = QFrame()
        self.frame_login.setObjectName("loginCard")

        layout_frame = QVBoxLayout()

        layout_frame.setContentsMargins(35, 30, 35, 35)

        # SUBTÍTULO
        self.lbl_subtitulo = QLabel("Iniciar sesión")

        self.lbl_subtitulo.setObjectName("subtitulo")

        layout_frame.addWidget(self.lbl_subtitulo)

        self.lbl_mensaje = QLabel("Ingrese sus credenciales para continuar")

        self.lbl_mensaje.setObjectName("mensaje")

        layout_frame.addWidget(self.lbl_mensaje)

        layout_frame.addSpacing(20)


        # CAMPOS


        self.usuario = QLineEdit()

        self.usuario.setObjectName("campoUsuario")

        self.usuario.setPlaceholderText("Ingrese su usuario")

        self.contrasena = QLineEdit()

        self.contrasena.setObjectName("campoContrasena")

        self.contrasena.setPlaceholderText("Ingrese su contraseña")

        self.contrasena.setEchoMode(QLineEdit.Password)

        # FORMULARIO
        formulario = QFormLayout()

        formulario.setVerticalSpacing(15)

        formulario.addRow("Usuario",self.usuario)

        formulario.addRow("Contraseña",self.contrasena)

        layout_frame.addLayout(formulario)

        layout_frame.addSpacing(20)


        # BOTÓN

        self.btn_login = QPushButton("Iniciar sesión")

        self.btn_login.setObjectName("btnLogin")

        self.btn_login.setCursor(Qt.PointingHandCursor)

        layout_frame.addWidget(self.btn_login)

        # TEXTO INFERIOR
        self.lbl_footer = QLabel("Acceso exclusivo para personal autorizado" )

        self.lbl_footer.setObjectName("footer")

        layout_footer = QHBoxLayout()
        layout_footer.addStretch()
        layout_footer.addWidget(self.lbl_footer)
        layout_footer.addStretch()

        layout_frame.addSpacing(15)
        layout_frame.addLayout(layout_footer)

        self.frame_login.setLayout(layout_frame)

        # CENTRAR TARJETA

        layout_card = QHBoxLayout()

        layout_card.addStretch()
        layout_card.addWidget(self.frame_login)
        layout_card.addStretch()

        layout_principal.addLayout(layout_card)

        # Espacio inferior
        layout_principal.addStretch()

        self.setLayout(layout_principal)


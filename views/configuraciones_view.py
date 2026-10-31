from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QPushButton,QMessageBox,QGroupBox,QComboBox,QLabel)


class Configuraciones_sistema (QWidget):

    def __init__(self):
        super().__init__()
        self.crear_interfaz()
        self.conexiones_botones()

    def crear_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 20, 25, 20)
        layout_principal.setSpacing(20)

        # ENCABEZADO

        titulo = QLabel("Configuración del sistema")

        descripcion = QLabel("Administra la información del taller " "y las preferencias de la aplicación.")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # INFORMACIÓN DEL TALLER

        grupo_taller = QGroupBox("Información del taller")
        formulario_taller = QFormLayout(grupo_taller)
        formulario_taller.setSpacing(15)

        self.txt_nombre_taller = QLineEdit()
        self.txt_nombre_taller.setPlaceholderText("Nombre del taller")

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Número de teléfono")

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("Correo electrónico")

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección del taller")

        formulario_taller.addRow("Nombre:", self.txt_nombre_taller)

        formulario_taller.addRow("Teléfono:", self.txt_telefono)

        formulario_taller.addRow("Correo:", self.txt_correo)

        formulario_taller.addRow("Dirección:", self.txt_direccion)

        layout_principal.addWidget(grupo_taller)

        # PREFERENCIAS DEL SISTEMA

        grupo_preferencias = QGroupBox("Preferencias del sistema")
        formulario_preferencias = QFormLayout(grupo_preferencias)
        formulario_preferencias.setSpacing(15)

        self.cbx_formato_fecha = QComboBox()
        self.cbx_formato_fecha.addItems(["dd/MM/yyyy","yyyy-MM-dd"])

        formulario_preferencias.addRow("Formato de fecha:",self.cbx_formato_fecha
        )

        self.cbx_confirmacion = QComboBox()
        self.cbx_confirmacion.addItems(["Sí","No"
        ])

        formulario_preferencias.addRow("Confirmar acciones:",self.cbx_confirmacion)

        layout_principal.addWidget(grupo_preferencias)

        # INFORMACIÓN DE LA BASE DE DATOS


        grupo_datos = QGroupBox("Estado de la conexión")
        layout_datos = QVBoxLayout(grupo_datos)

        self.lbl_estado_conexion = QLabel("Base de datos: pendiente de configuración")

        self.lbl_estado_conexion.setWordWrap(True)

        layout_datos.addWidget(self.lbl_estado_conexion)
        layout_principal.addWidget(grupo_datos)


        # BOTONES


        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar configuración" )

        self.btn_limpiar = QPushButton("Restablecer formulario")

        layout_botones.addStretch()
        layout_botones.addWidget(self.btn_limpiar)
        layout_botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(layout_botones)
        layout_principal.addStretch()

    def conexiones_botones(self):
        self.btn_guardar.clicked.connect(self.guardar_configuracion)

        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

    def guardar_configuracion(self):
        nombre = self.txt_nombre_taller.text().strip()
        correo = self.txt_correo.text().strip()

        if not nombre:
            QMessageBox.warning(self,"Campo obligatorio","Introduce el nombre del taller.")
            self.txt_nombre_taller.setFocus()
            return

        if correo and (
            "@" not in correo or "." not in correo.split("@")[-1]
        ):
            QMessageBox.warning(self,"Correo inválido","Introduce un correo electrónico válido."
            )
            self.txt_correo.setFocus()
            return

        # Por ahora solo validamos el formulario.
        # La persistencia se implementará con el backend.

        QMessageBox.information( self,"Configuración validada","Los datos son válidos. ""La configuración se guardará cuando " "conectemos el backend."
        )

    def limpiar_formulario(self):
        self.txt_nombre_taller.clear()
        self.txt_telefono.clear()
        self.txt_correo.clear()
        self.txt_direccion.clear()

        self.cbx_formato_fecha.setCurrentIndex(0)
        self.cbx_confirmacion.setCurrentIndex(0)

        self.txt_nombre_taller.setFocus()

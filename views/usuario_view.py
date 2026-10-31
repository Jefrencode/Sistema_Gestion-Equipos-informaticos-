
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtCore import Qt


class Usuarios(QWidget):

    def __init__(self):
        super().__init__()

        self.modo_edicion = False
        self.id_usuario_seleccionado = None

        self.crear_interfaz()
        self.conexiones_botones()

    def crear_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        # Título
        titulo = QLabel("Gestión de usuarios")
        
        layout_principal.addWidget(titulo)

        descripcion = QLabel("Administra las cuentas de los trabajadores del taller.")
        layout_principal.addWidget(descripcion)

        # Formulario
        grupo_formulario = QGroupBox("Datos del usuario")
        formulario = QFormLayout(grupo_formulario)
        formulario.setSpacing(12)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Nombre de usuario")

        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText("Contraseña inicial o nueva contraseña")
        self.txt_contrasena.setEchoMode(QLineEdit.EchoMode.Password)

        self.cbx_rol = QComboBox()
        self.cbx_rol.addItems(["Técnico", "Administrador"])

        formulario.addRow("Nombre completo:", self.txt_nombre)
        formulario.addRow("Nombre de usuario:", self.txt_usuario)
        formulario.addRow("Contraseña:", self.txt_contrasena)
        formulario.addRow("Rol:", self.cbx_rol)

        layout_principal.addWidget(grupo_formulario)

        # Botones
        layout_botones = QHBoxLayout()

        self.btn_nuevo = QPushButton("Nuevo usuario")
        self.btn_guardar = QPushButton("Guardar usuario")
        self.btn_editar = QPushButton("Guardar cambios")
        self.btn_estado = QPushButton("Activar / Desactivar")
        self.btn_limpiar = QPushButton("Limpiar")

        layout_botones.addWidget(self.btn_nuevo)
        layout_botones.addWidget(self.btn_guardar)
        layout_botones.addWidget(self.btn_editar)
        layout_botones.addWidget(self.btn_estado)
        layout_botones.addWidget(self.btn_limpiar)

        layout_principal.addLayout(layout_botones)

        # Tabla
        grupo_tabla = QGroupBox("Usuarios registrados")
        layout_tabla = QVBoxLayout(grupo_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre o nombre de usuario...")
        layout_tabla.addWidget(self.txt_buscar)

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(5)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID","Nombre completo","Usuario","Rol","Estado",])

        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_usuarios.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_usuarios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_usuarios.setAlternatingRowColors(True)

        encabezado = self.tabla_usuarios.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout_tabla.addWidget(self.tabla_usuarios)
        layout_principal.addWidget(grupo_tabla)

        # Estado inicial de los botones
        self.btn_editar.setEnabled(False)
        self.btn_estado.setEnabled(False)

    def conexiones_botones(self):
        self.btn_guardar.clicked.connect(self.guardar_usuario)
        self.btn_editar.clicked.connect(self.guardar_cambios)
        self.btn_nuevo.clicked.connect(self.nuevo_usuario)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_estado.clicked.connect(self.cambiar_estado)
        self.tabla_usuarios.itemSelectionChanged.connect(self.seleccionar_usuario)
        self.txt_buscar.textChanged.connect(self.filtrar_usuarios)

    def guardar_usuario(self):
        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contrasena.text()
        rol = self.cbx_rol.currentText()

        if not nombre or not usuario or not contrasena:
            QMessageBox.warning(self,"Campos obligatorios","Completa el nombre, el usuario y la contraseña.")
            return

        if len(contrasena) < 8:
            QMessageBox.warning(self,"Contraseña no válida","La contraseña debe tener al menos 8 caracteres.")
            return

        # Evitar nombres de usuario duplicados.
        for fila in range(self.tabla_usuarios.rowCount()):
            usuario_existente = self.tabla_usuarios.item(fila, 2)

            if (usuario_existente and usuario_existente.text().casefold() == usuario.casefold()):
                QMessageBox.warning(self, "Usuario duplicado", "Ese nombre de usuario ya está registrado.")
                return

        # ID temporal: MySQL generará los IDs definitivos.
        id_temporal = 1

        for fila in range(self.tabla_usuarios.rowCount()):
            item_id = self.tabla_usuarios.item(fila, 0)
            if item_id:
                id_temporal = max(
                    id_temporal, int(item_id.text()) + 1
                )

        fila = self.tabla_usuarios.rowCount()
        self.tabla_usuarios.insertRow(fila)

        datos = [
            str(id_temporal),
            nombre,
            usuario,
            rol,
            "Activo",
        ]

        for columna, dato in enumerate(datos):
            self.tabla_usuarios.setItem(fila, columna, QTableWidgetItem(dato))

        # La contraseña no se muestra ni se guarda en la tabla.
        # En la versión con MySQL se almacenará como hash seguro.
        self.limpiar_formulario()

        QMessageBox.information(
            self,"Usuario agregado","El usuario se agregó a la tabla temporal.")

    def seleccionar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        seleccionado = fila >= 0

        self.btn_editar.setEnabled(seleccionado)
        self.btn_estado.setEnabled(seleccionado)

        if not seleccionado:
            return

        self.id_usuario_seleccionado = ( self.tabla_usuarios.item(fila, 0).text())
        self.txt_nombre.setText(self.tabla_usuarios.item(fila, 1).text())
        self.txt_usuario.setText( self.tabla_usuarios.item(fila, 2).text())
        self.cbx_rol.setCurrentText(self.tabla_usuarios.item(fila, 3).text())

        # La contraseña nunca se recupera desde la tabla.
        self.txt_contrasena.clear()

        self.modo_edicion = True
        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)

    def guardar_cambios(self):
        if self.id_usuario_seleccionado is None:
            return

        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contrasena.text()
        rol = self.cbx_rol.currentText()

        if not nombre or not usuario:
            QMessageBox.warning(
                self,"Campos obligatorios","El nombre y el nombre de usuario son obligatorios."
            )
            return

        if contrasena and len(contrasena) < 8:
            QMessageBox.warning(
                self,"Contraseña no válida","La nueva contraseña debe tener al menos 8 caracteres."
            )
            return

        fila_seleccionada = self.tabla_usuarios.currentRow()

        if fila_seleccionada < 0:
            return

        for fila in range(self.tabla_usuarios.rowCount()):
            if fila == fila_seleccionada:
                continue

            item_usuario = self.tabla_usuarios.item(fila, 2)

            if (item_usuario and item_usuario.text().casefold() == usuario.casefold()):
                QMessageBox.warning(
                    self,"Usuario duplicado","Ese nombre de usuario ya pertenece a otra cuenta."
                )
                return

        self.tabla_usuarios.item(fila_seleccionada, 1).setText(nombre)
        self.tabla_usuarios.item(fila_seleccionada, 2).setText(usuario)
        self.tabla_usuarios.item(fila_seleccionada, 3).setText(rol)

        self.limpiar_formulario()

        QMessageBox.information(
            self,"Cambios realizados","Los datos se actualizaron en la tabla temporal."+ (
                "\nLa nueva contraseña se guardará al conectar "
                "el sistema con el backend." if contrasena else "" ))

    def cambiar_estado(self):
        fila = self.tabla_usuarios.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self,"Selecciona un usuario","Selecciona una fila de la tabla."
            )
            return

        item_estado = self.tabla_usuarios.item(fila, 4)
        nuevo_estado = ("Inactivo"if item_estado.text() == "Activo"else "Activo"
        )

        respuesta = QMessageBox.question(
            self,"Confirmar cambio",f"¿Deseas cambiar el estado de esta cuenta a "f"{nuevo_estado}?")

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        item_estado.setText(nuevo_estado)
        self.limpiar_formulario()

    def filtrar_usuarios(self, texto):
        texto = texto.strip().casefold()

        for fila in range(self.tabla_usuarios.rowCount()):
            item_nombre = self.tabla_usuarios.item(fila, 1)
            item_usuario = self.tabla_usuarios.item(fila, 2)

            coincide = (texto in item_nombre.text().casefold()or texto in item_usuario.text().casefold())

            self.tabla_usuarios.setRowHidden(fila, not coincide)

    def nuevo_usuario(self):
        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    def limpiar_formulario(self):
        self.txt_nombre.clear()
        self.txt_usuario.clear()
        self.txt_contrasena.clear()
        self.cbx_rol.setCurrentIndex(0)

        self.tabla_usuarios.clearSelection()
        self.id_usuario_seleccionado = None
        self.modo_edicion = False

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_estado.setEnabled(False)

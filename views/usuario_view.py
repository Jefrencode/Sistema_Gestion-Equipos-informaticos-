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
    QHeaderView
)

from PySide6.QtCore import Qt

from controllers.usuario_controller import (
    UsuarioController
)


class Usuarios(QWidget):

    def __init__(self, id_administrador):
        super().__init__()

        self.controller = UsuarioController(
            id_administrador
        )

        self.modo_edicion = False
        self.id_usuario_seleccionado = None

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_usuarios()

    # ==========================================
    # CREAR INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(
            20, 20, 20, 20
        )
        layout_principal.setSpacing(15)

        titulo = QLabel("Gestión de usuarios")

        descripcion = QLabel(
            "Administra las cuentas de los "
            "trabajadores del taller."
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # FORMULARIO

        grupo_formulario = QGroupBox(
            "Datos del usuario"
        )

        formulario = QFormLayout(
            grupo_formulario
        )
        formulario.setSpacing(12)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText(
            "Nombre completo"
        )
        self.txt_nombre.setMaxLength(160)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText(
            "Nombre de usuario"
        )
        self.txt_usuario.setMaxLength(60)

        self.txt_contrasena = QLineEdit()
        self.txt_contrasena.setPlaceholderText(
            "Contraseña inicial o nueva contraseña"
        )
        self.txt_contrasena.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.cbx_rol = QComboBox()
        self.cbx_rol.addItems([
            "Técnico",
            "Administrador"
        ])

        formulario.addRow(
            "Nombre completo:",
            self.txt_nombre
        )
        formulario.addRow(
            "Nombre de usuario:",
            self.txt_usuario
        )
        formulario.addRow(
            "Contraseña:",
            self.txt_contrasena
        )
        formulario.addRow(
            "Rol:",
            self.cbx_rol
        )

        layout_principal.addWidget(
            grupo_formulario
        )

        # BOTONES

        layout_botones = QHBoxLayout()

        self.btn_nuevo = QPushButton(
            "Nuevo usuario"
        )

        self.btn_guardar = QPushButton(
            "Guardar usuario"
        )

        self.btn_editar = QPushButton(
            "Guardar cambios"
        )

        self.btn_estado = QPushButton(
            "Activar / Desactivar"
        )

        self.btn_limpiar = QPushButton(
            "Limpiar"
        )

        layout_botones.addWidget(
            self.btn_nuevo
        )
        layout_botones.addWidget(
            self.btn_guardar
        )
        layout_botones.addWidget(
            self.btn_editar
        )
        layout_botones.addWidget(
            self.btn_estado
        )
        layout_botones.addWidget(
            self.btn_limpiar
        )

        layout_principal.addLayout(
            layout_botones
        )

        # TABLA

        grupo_tabla = QGroupBox(
            "Usuarios registrados"
        )

        layout_tabla = QVBoxLayout(
            grupo_tabla
        )

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por nombre o usuario..."
        )

        layout_tabla.addWidget(
            self.txt_buscar
        )

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(5)

        self.tabla_usuarios.setHorizontalHeaderLabels([
            "ID",
            "Nombre completo",
            "Usuario",
            "Rol",
            "Estado"
        ])

        self.tabla_usuarios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabla_usuarios.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabla_usuarios.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla_usuarios.setAlternatingRowColors(
            True
        )

        encabezado = (
            self.tabla_usuarios.horizontalHeader()
        )

        encabezado.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout_tabla.addWidget(
            self.tabla_usuarios
        )

        layout_principal.addWidget(
            grupo_tabla
        )

        self.btn_editar.setEnabled(False)
        self.btn_estado.setEnabled(False)

    # ==========================================
    # CONECTAR EVENTOS
    # ==========================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_usuario
        )

        self.btn_editar.clicked.connect(
            self.guardar_cambios
        )

        self.btn_nuevo.clicked.connect(
            self.nuevo_usuario
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.btn_estado.clicked.connect(
            self.cambiar_estado
        )

        self.tabla_usuarios.itemSelectionChanged.connect(
            self.seleccionar_usuario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_usuarios
        )

    # ==========================================
    # CARGAR USUARIOS DESDE MYSQL
    # ==========================================

    def cargar_usuarios(self):

        try:
            usuarios = (
                self.controller.listar_usuarios()
            )

            self.tabla_usuarios.setRowCount(0)

            for usuario in usuarios:

                fila = (
                    self.tabla_usuarios.rowCount()
                )

                self.tabla_usuarios.insertRow(fila)

                datos = [
                    str(usuario["id_usuario"]),
                    usuario["nombre"],
                    usuario["nombre_usuario"],
                    usuario["rol"],
                    (
                        "Activo"
                        if usuario["activo"]
                        else "Inactivo"
                    )
                ]

                for columna, valor in enumerate(datos):

                    item = QTableWidgetItem(
                        str(valor)
                    )

                    self.tabla_usuarios.setItem(
                        fila,
                        columna,
                        item
                    )

            self.filtrar_usuarios(
                self.txt_buscar.text()
            )

        except PermissionError as error:

            self.setEnabled(False)

            QMessageBox.critical(
                self,
                "Acceso denegado",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al cargar usuarios",
                str(error)
            )

    # ==========================================
    # GUARDAR USUARIO
    # ==========================================

    def guardar_usuario(self):

        nombre = self.txt_nombre.text().strip()
        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contrasena.text()
        rol = self.cbx_rol.currentText()

        try:

            self.controller.registrar_usuario(
                nombre,
                usuario,
                contrasena,
                rol
            )

            QMessageBox.information(
                self,
                "Usuario registrado",
                "El usuario se guardó correctamente "
                "en MySQL."
            )

            self.limpiar_formulario()
            self.cargar_usuarios()

        except (
            ValueError,
            PermissionError,
            Exception
        ) as error:

            QMessageBox.warning(
                self,
                "No se pudo registrar",
                str(error)
            )

    # ==========================================
    # SELECCIONAR USUARIO
    # ==========================================

    def seleccionar_usuario(self):

        fila = self.tabla_usuarios.currentRow()

        if fila < 0:
            self.id_usuario_seleccionado = None
            self.modo_edicion = False

            self.btn_editar.setEnabled(False)
            self.btn_estado.setEnabled(False)
            return

        self.id_usuario_seleccionado = int(
            self.tabla_usuarios.item(
                fila, 0
            ).text()
        )

        self.txt_nombre.setText(
            self.tabla_usuarios.item(
                fila, 1
            ).text()
        )

        self.txt_usuario.setText(
            self.tabla_usuarios.item(
                fila, 2
            ).text()
        )

        self.cbx_rol.setCurrentText(
            self.tabla_usuarios.item(
                fila, 3
            ).text()
        )

        # Nunca recuperar contraseñas.
        # Dejar vacío para conservar la actual.
        self.txt_contrasena.clear()

        self.modo_edicion = True

        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_estado.setEnabled(True)

    # ==========================================
    # GUARDAR CAMBIOS
    # ==========================================

    def guardar_cambios(self):

        if self.id_usuario_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selecciona un usuario",
                "Debes seleccionar una cuenta."
            )
            return

        try:

            self.controller.actualizar_usuario(
                id_usuario=self.id_usuario_seleccionado,
                nombre=self.txt_nombre.text(),
                nombre_usuario=self.txt_usuario.text(),
                rol=self.cbx_rol.currentText(),
                nueva_contrasena=(
                    self.txt_contrasena.text()
                )
            )

            QMessageBox.information(
                self,
                "Cambios guardados",
                "El usuario se actualizó "
                "correctamente."
            )

            self.limpiar_formulario()
            self.cargar_usuarios()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error al actualizar",
                str(error)
            )

    # ==========================================
    # ACTIVAR / DESACTIVAR
    # ==========================================

    def cambiar_estado(self):

        if self.id_usuario_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selecciona un usuario",
                "Debes seleccionar una cuenta."
            )
            return

        fila = self.tabla_usuarios.currentRow()

        estado_actual = (
            self.tabla_usuarios.item(
                fila, 4
            ).text()
        )

        nuevo_estado = (
            "Inactivo"
            if estado_actual == "Activo"
            else "Activo"
        )

        respuesta = QMessageBox.question(
            self,
            "Confirmar cambio",
            "¿Deseas cambiar el estado "
            f"de esta cuenta a {nuevo_estado}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:

            self.controller.cambiar_estado(
                self.id_usuario_seleccionado
            )

            QMessageBox.information(
                self,
                "Estado actualizado",
                "El estado del usuario se "
                "actualizó correctamente."
            )

            self.limpiar_formulario()
            self.cargar_usuarios()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error al cambiar estado",
                str(error)
            )

    # ==========================================
    # FILTRAR USUARIOS
    # ==========================================

    def filtrar_usuarios(self, texto):

        texto = texto.strip().casefold()

        for fila in range(
            self.tabla_usuarios.rowCount()
        ):

            item_nombre = (
                self.tabla_usuarios.item(fila, 1)
            )

            item_usuario = (
                self.tabla_usuarios.item(fila, 2)
            )

            if not item_nombre or not item_usuario:
                continue

            coincide = (
                texto in item_nombre.text().casefold()
                or texto in item_usuario.text().casefold()
            )

            self.tabla_usuarios.setRowHidden(
                fila,
                not coincide
            )

    # ==========================================
    # NUEVO USUARIO
    # ==========================================

    def nuevo_usuario(self):

        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    # ==========================================
    # LIMPIAR FORMULARIO
    # ==========================================

    def limpiar_formulario(self):

        self.tabla_usuarios.clearSelection()

        self.txt_nombre.clear()
        self.txt_usuario.clear()
        self.txt_contrasena.clear()

        self.cbx_rol.setCurrentIndex(0)

        self.id_usuario_seleccionado = None
        self.modo_edicion = False

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_estado.setEnabled(False)

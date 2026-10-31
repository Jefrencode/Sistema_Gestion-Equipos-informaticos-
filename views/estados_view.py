
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QHeaderView, QTableWidget,
    QTableWidgetItem, QGroupBox, QTextEdit,
    QLabel, QComboBox
)

from PySide6.QtCore import Qt

from controllers.estados_controller import EstadosController


class Estados_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = EstadosController()

        self.modo_edicion = False
        self.id_estado_seleccionado = None
        self.estados = []

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_estados()

    # ===========================================
    # CREAR INTERFAZ
    # ===========================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # FORMULARIO
        grupo_formulario = QGroupBox(
            "Datos del estado"
        )

        layout_formulario = QVBoxLayout(
            grupo_formulario
        )

        formulario = QFormLayout()
        formulario.setSpacing(15)

        self.lbl_modo = QLabel("Nuevo estado")

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(40)
        self.txt_nombre.setPlaceholderText(
            "Nombre del estado"
        )

        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setPlaceholderText(
            "Describe el estado..."
        )
        self.txt_descripcion.setMaximumHeight(100)

        self.cbx_tipo_registro = QComboBox()
        self.cbx_tipo_registro.addItem(
            "Seleccione un tipo", None
        )
        self.cbx_tipo_registro.addItem(
            "Reparación", "Reparacion"
        )
        self.cbx_tipo_registro.addItem(
            "Mantenimiento", "Mantenimiento"
        )

        formulario.addRow(
            "Acción:", self.lbl_modo
        )
        formulario.addRow(
            "Nombre:", self.txt_nombre
        )
        formulario.addRow(
            "Descripción:", self.txt_descripcion
        )
        formulario.addRow(
            "Tipo de registro:", self.cbx_tipo_registro
        )

        layout_formulario.addLayout(formulario)

        # BOTONES
        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_guardar = QPushButton(
            "Guardar estado"
        )
        self.btn_editar = QPushButton(
            "Guardar cambios"
        )
        self.btn_eliminar = QPushButton(
            "Eliminar estado"
        )
        self.btn_limpiar = QPushButton("Limpiar")

        layout_formulario.addWidget(self.btn_nuevo)
        layout_formulario.addWidget(self.btn_guardar)
        layout_formulario.addWidget(self.btn_editar)
        layout_formulario.addWidget(self.btn_eliminar)
        layout_formulario.addWidget(self.btn_limpiar)

        # TABLA DE ESTADOS
        grupo_tabla = QGroupBox(
            "Estados registrados"
        )

        layout_tabla = QVBoxLayout(
            grupo_tabla
        )

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por ID, nombre, descripción o tipo..."
        )

        layout_tabla.addWidget(self.txt_buscar)

        self.tabla_estados = QTableWidget()
        self.tabla_estados.setColumnCount(4)

        self.tabla_estados.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Descripción",
            "Tipo de registro"
        ])

        self.tabla_estados.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_estados.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabla_estados.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabla_estados.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla_estados.setAlternatingRowColors(
            True
        )

        layout_tabla.addWidget(self.tabla_estados)

        layout_principal.addWidget(
            grupo_formulario, 1
        )
        layout_principal.addWidget(
            grupo_tabla, 2
        )

        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

    # ===========================================
    # CONEXIONES
    # ===========================================

    def conexiones_botones(self):

        self.btn_nuevo.clicked.connect(
            self.nuevo_estado
        )

        self.btn_guardar.clicked.connect(
            self.guardar_estado
        )

        self.btn_editar.clicked.connect(
            self.guardar_cambios
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_estado
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.tabla_estados.itemSelectionChanged.connect(
            self.seleccionar_estado
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_estados
        )

    # ===========================================
    # OBTENER DATOS
    # ===========================================

    def obtener_datos_formulario(self):

        return {
            "nombre": self.txt_nombre.text().strip(),
            "descripcion": (
                self.txt_descripcion
                .toPlainText()
                .strip()
            ),
            "tipo_registro": (
                self.cbx_tipo_registro.currentData()
            )
        }

    # ===========================================
    # GUARDAR
    # ===========================================

    def guardar_estado(self):

        datos = self.obtener_datos_formulario()

        try:
            id_estado = self.controller.registrar_estado(
                datos
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"Estado #{id_estado} registrado "
                "correctamente."
            )

            self.limpiar_formulario()
            self.cargar_estados()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error)
            )

    # ===========================================
    # CARGAR DESDE MYSQL
    # ===========================================

    def cargar_estados(self):

        try:
            self.estados = (
                self.controller.listar_estados()
            )

            self.filtrar_estados(
                self.txt_buscar.text()
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error de consulta",
                str(error)
            )

    # ===========================================
    # MOSTRAR EN LA TABLA
    # ===========================================

    def mostrar_estados(self, estados):

        self.tabla_estados.blockSignals(True)

        try:
            self.tabla_estados.setRowCount(0)

            for estado in estados:

                fila = self.tabla_estados.rowCount()
                self.tabla_estados.insertRow(fila)

                datos = [
                    str(estado["id_estado"]),
                    estado["nombre"],
                    estado["descripcion"] or "",
                    estado["tipo_registro"]
                ]

                for columna, dato in enumerate(datos):

                    item = QTableWidgetItem(
                        str(dato)
                    )

                    if columna == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            estado["id_estado"]
                        )

                    self.tabla_estados.setItem(
                        fila,
                        columna,
                        item
                    )

        finally:
            self.tabla_estados.blockSignals(False)

    # ===========================================
    # SELECCIONAR ESTADO
    # ===========================================

    def seleccionar_estado(self):

        fila = self.tabla_estados.currentRow()

        if fila < 0:
            return

        item_id = self.tabla_estados.item(fila, 0)

        if item_id is None:
            return

        id_estado = item_id.data(
            Qt.ItemDataRole.UserRole
        )

        estado = next(
            (
                e for e in self.estados
                if e["id_estado"] == id_estado
            ),
            None
        )

        if estado is None:
            return

        self.id_estado_seleccionado = id_estado
        self.modo_edicion = True

        self.txt_nombre.setText(
            estado["nombre"]
        )

        self.txt_descripcion.setPlainText(
            estado["descripcion"] or ""
        )

        indice = self.cbx_tipo_registro.findData(
            estado["tipo_registro"]
        )

        if indice >= 0:
            self.cbx_tipo_registro.setCurrentIndex(
                indice
            )

        # Proteger el tipo de registro al editar
        self.cbx_tipo_registro.setEnabled(False)

        self.lbl_modo.setText(
            f"Editando estado ID: {id_estado}"
        )

        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    # ===========================================
    # GUARDAR CAMBIOS
    # ===========================================

    def guardar_cambios(self):

        if self.id_estado_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un estado para editar."
            )
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_estado(
                self.id_estado_seleccionado,
                datos
            )

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "El estado fue actualizado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_estados()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

    # ===========================================
    # ELIMINAR
    # ===========================================

    def eliminar_estado(self):

        if self.id_estado_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un estado para eliminar."
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar este estado?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.controller.eliminar_estado(
                self.id_estado_seleccionado
            )

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "El estado fue eliminado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_estados()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                str(error)
            )

    # ===========================================
    # NUEVO ESTADO
    # ===========================================

    def nuevo_estado(self):

        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    # ===========================================
    # LIMPIAR FORMULARIO
    # ===========================================

    def limpiar_formulario(self):

        self.id_estado_seleccionado = None
        self.modo_edicion = False

        self.txt_nombre.clear()
        self.txt_descripcion.clear()

        self.cbx_tipo_registro.setEnabled(True)
        self.cbx_tipo_registro.setCurrentIndex(0)

        self.lbl_modo.setText("Nuevo estado")

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.tabla_estados.clearSelection()

        self.txt_nombre.setFocus()

    # ===========================================
    # FILTRAR
    # ===========================================

    def filtrar_estados(self, texto=None):

        if texto is None:
            texto = self.txt_buscar.text()

        texto = texto.strip().casefold()

        # Restablecer el formulario antes de cambiar
        # los resultados visibles.
        self.limpiar_formulario()

        resultados = []

        for estado in self.estados:

            contenido = " ".join([
                str(estado["id_estado"]),
                estado["nombre"],
                estado["descripcion"] or "",
                estado["tipo_registro"]
            ]).casefold()

            if texto in contenido:
                resultados.append(estado)

        self.mostrar_estados(resultados)

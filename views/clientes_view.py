from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QAbstractItemView
)

from controllers.clientes_controller import ClientesController


class Clientes(QWidget):

    # ==========================================
    # 1. INICIALIZACIÓN
    # ==========================================

    def __init__(self):
        super().__init__()

        self.controller = ClientesController()

        # Identificador del cliente seleccionado
        self.id_cliente_seleccionado = None

        # Clientes consultados desde MySQL
        self.clientes_cargados = {}

        self.crear_interfaz()
        self.setup_signals()
        self.cargar_clientes()

    # ==========================================
    # 2. CONSTRUCCIÓN DE LA INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # -------- FORMULARIO --------

        grupo_formulario = QGroupBox("Datos del cliente")
        layout_formulario = QVBoxLayout(grupo_formulario)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.txt_cedula = QLineEdit()
        self.txt_nombre_completos = QLineEdit()
        self.txt_apellido = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_correo = QLineEdit()
        self.txt_direccion = QLineEdit()

        self.cbx_tipo_cliente = QComboBox()
        self.cbx_tipo_cliente.addItems([
            "Particular",
            "Empresarial"
        ])

        self.txe_observacion_cliente = QTextEdit()
        self.txe_observacion_cliente.setMaximumHeight(80)

        # Ayudas visuales
        self.txt_cedula.setPlaceholderText("000-000000-0000A")
        self.txt_telefono.setPlaceholderText("8 dígitos")
        self.txt_correo.setPlaceholderText("ejemplo@correo.com")

        # Campos del formulario
        form_layout.addRow("Cédula:", self.txt_cedula)
        form_layout.addRow(
            "Nombres:", self.txt_nombre_completos
        )
        form_layout.addRow("Apellidos:", self.txt_apellido)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Correo:", self.txt_correo)
        form_layout.addRow("Dirección:", self.txt_direccion)
        form_layout.addRow(
            "Tipo de cliente:", self.cbx_tipo_cliente
        )
        form_layout.addRow(
            "Observaciones:", self.txe_observacion_cliente
        )

        # -------- BOTONES --------

        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar Cliente")
        self.btn_editar = QPushButton("Editar Cliente")
        self.btn_eliminar = QPushButton("Eliminar Cliente")
        self.btn_limpiar = QPushButton("Limpiar")

        layout_botones.addWidget(self.btn_guardar)
        layout_botones.addWidget(self.btn_editar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_botones.addWidget(self.btn_limpiar)

        layout_formulario.addLayout(form_layout)
        layout_formulario.addLayout(layout_botones)
        layout_formulario.addStretch()

        # -------- TABLA --------

        grupo_tabla = QGroupBox("Listado de Clientes")
        layout_tabla = QVBoxLayout(grupo_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar cliente por cédula o nombre..."
        )

        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(4)

        self.tabla_clientes.setHorizontalHeaderLabels([
            "Cédula",
            "Nombre completo",
            "Teléfono",
            "Correo"
        ])

        self.tabla_clientes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla_clientes.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla_clientes.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla_clientes.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        layout_tabla.addWidget(self.txt_buscar)
        layout_tabla.addWidget(self.tabla_clientes)

        # -------- DISTRIBUCIÓN --------

        layout_principal.addWidget(grupo_formulario, 1)
        layout_principal.addWidget(grupo_tabla, 2)

        self.actualizar_botones()

    # ==========================================
    # 3. CONEXIÓN DE EVENTOS
    # ==========================================

    def setup_signals(self):

        self.btn_guardar.clicked.connect(self.guardar_cliente)
        self.btn_editar.clicked.connect(self.editar_cliente)
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.txt_buscar.textChanged.connect(self.filtrar_clientes)

        self.tabla_clientes.itemSelectionChanged.connect(
            self.seleccionar_cliente
        )

    # ==========================================
    # 4. OBTENER DATOS DEL FORMULARIO
    # ==========================================

    def obtener_datos_formulario(self):

        return {
            "cedula": self.txt_cedula.text().strip(),
            "nombre": self.txt_nombre_completos.text().strip(),
            "apellido": self.txt_apellido.text().strip(),
            "telefono": self.txt_telefono.text().strip(),
            "correo": self.txt_correo.text().strip(),
            "direccion": self.txt_direccion.text().strip(),
            "tipo_cliente": self.cbx_tipo_cliente.currentText(),
            "observaciones": (
                self.txe_observacion_cliente.toPlainText().strip()
            )
        }

    # ==========================================
    # 5. REGISTRAR CLIENTE
    # ==========================================

    def guardar_cliente(self):

        datos = self.obtener_datos_formulario()

        try:
            self.controller.registrar_cliente(datos)

            self.cargar_clientes()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Registro exitoso",
                "El cliente fue registrado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al registrar",
                str(error)
            )

    # ==========================================
    # 6. CONSULTAR CLIENTES
    # ==========================================

    def cargar_clientes(self):

        try:
            clientes = self.controller.listar_clientes()

        except RuntimeError as error:
            QMessageBox.warning(
                self,
                "Error de consulta",
                str(error)
            )
            return

        # Guardar los datos consultados por ID
        self.clientes_cargados = {
            cliente["id_cliente"]: cliente
            for cliente in clientes
        }

        # Evitar eventos durante la recarga
        self.tabla_clientes.blockSignals(True)

        try:
            self.tabla_clientes.setRowCount(0)

            for cliente in clientes:

                fila = self.tabla_clientes.rowCount()
                self.tabla_clientes.insertRow(fila)

                valores = [
                    cliente["cedula"] or "",
                    (
                        f'{cliente["nombre"]} '
                        f'{cliente["apellido"]}'
                    ),
                    cliente["telefono"] or "",
                    cliente["correo"] or ""
                ]

                for columna, valor in enumerate(valores):

                    item = QTableWidgetItem(str(valor))

                    # Guardar el ID real en la primera celda
                    if columna == 0:
                        item.setData(
                            Qt.UserRole,
                            cliente["id_cliente"]
                        )

                    self.tabla_clientes.setItem(
                        fila, columna, item
                    )

            self.tabla_clientes.clearSelection()
            self.tabla_clientes.setCurrentCell(-1, -1)

        finally:
            self.tabla_clientes.blockSignals(False)

        self.id_cliente_seleccionado = None
        self.actualizar_botones()
        self.filtrar_clientes(self.txt_buscar.text())

    # ==========================================
    # 7. SELECCIONAR CLIENTE
    # ==========================================

    def seleccionar_cliente(self):

        fila = self.tabla_clientes.currentRow()

        if fila < 0 or not self.tabla_clientes.selectedItems():
            self.id_cliente_seleccionado = None
            self.actualizar_botones()
            return

        item = self.tabla_clientes.item(fila, 0)

        if item is None:
            return

        id_cliente = item.data(Qt.UserRole)
        cliente = self.clientes_cargados.get(id_cliente)

        if cliente is None:
            return

        self.id_cliente_seleccionado = id_cliente

        # Cargar información en el formulario
        self.txt_cedula.setText(cliente["cedula"] or "")
        self.txt_nombre_completos.setText(cliente["nombre"])
        self.txt_apellido.setText(cliente["apellido"])
        self.txt_telefono.setText(cliente["telefono"] or "")
        self.txt_correo.setText(cliente["correo"] or "")
        self.txt_direccion.setText(cliente["direccion"] or "")

        self.cbx_tipo_cliente.setCurrentText(
            cliente["tipo_cliente"]
        )

        self.txe_observacion_cliente.setPlainText(
            cliente["observaciones"] or ""
        )

        self.actualizar_botones()

    # ==========================================
    # 8. EDITAR CLIENTE
    # ==========================================

    def editar_cliente(self):

        if self.id_cliente_seleccionado is None:
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_cliente(
                self.id_cliente_seleccionado,
                datos
            )

            self.cargar_clientes()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "El cliente fue actualizado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al actualizar",
                str(error)
            )

    # ==========================================
    # 9. ELIMINAR CLIENTE
    # ==========================================

    def eliminar_cliente(self):

        if self.id_cliente_seleccionado is None:
            return

        cliente = self.clientes_cargados.get(
            self.id_cliente_seleccionado
        )

        if cliente is None:
            return

        nombre_completo = (
            f'{cliente["nombre"]} {cliente["apellido"]}'
        )

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Desea eliminar al cliente {nombre_completo}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:
            self.controller.eliminar_cliente(self.id_cliente_seleccionado)

            self.cargar_clientes()
            self.limpiar_formulario()

            QMessageBox.information(self,"Eliminación exitosa","El cliente fue eliminado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(self,"Error al eliminar",str(error))

    # ==========================================
    # 10. BUSCAR CLIENTES
    # ==========================================

    def filtrar_clientes(self, texto):

        texto = texto.strip().casefold()

        for fila in range(self.tabla_clientes.rowCount()):

            cedula = self.tabla_clientes.item(fila, 0)
            nombre = self.tabla_clientes.item(fila, 1)

            contenido = " ".join([cedula.text() if cedula else "",nombre.text() if nombre else ""]).casefold()

            self.tabla_clientes.setRowHidden(fila,texto not in contenido)

    # ==========================================
    # 11. ESTADO DE LOS BOTONES
    # ==========================================

    def actualizar_botones(self):

        hay_seleccion = (
            self.id_cliente_seleccionado is not None
        )

        self.btn_guardar.setEnabled(not hay_seleccion)
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)

    # ==========================================
    # 12. LIMPIAR FORMULARIO
    # ==========================================

    def limpiar_formulario(self):

        self.id_cliente_seleccionado = None

        self.tabla_clientes.blockSignals(True)

        try:
            self.tabla_clientes.clearSelection()
            self.tabla_clientes.setCurrentCell(-1, -1)
        finally:
            self.tabla_clientes.blockSignals(False)

        self.txt_cedula.clear()
        self.txt_nombre_completos.clear()
        self.txt_apellido.clear()
        self.txt_telefono.clear()
        self.txt_correo.clear()
        self.txt_direccion.clear()

        self.cbx_tipo_cliente.setCurrentIndex(0)
        self.txe_observacion_cliente.clear()

        self.actualizar_botones()
        self.txt_cedula.setFocus()

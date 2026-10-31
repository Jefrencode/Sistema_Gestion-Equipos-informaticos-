
from PySide6.QtCore import QDate, Qt

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
    QDateEdit,
    QAbstractItemView
)

from controllers.equipo_controller import EquiposController


class Equipos(QWidget):

    # ==========================================
    # 1. INICIALIZACIÓN
    # ==========================================

    def __init__(self):
        super().__init__()

        self.controller = EquiposController()

        # ID del equipo seleccionado
        self.id_equipo_seleccionado = None

        # Equipos consultados desde MySQL
        self.equipos_cargados = {}

        self.crear_interfaz()
        self.conexiones_botones()

        # Cargar información inicial
        self.cargar_clientes()
        self.cargar_equipos()

    # ==========================================
    # 2. CONSTRUCCIÓN DE LA INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal_equipos = QHBoxLayout(self)
        layout_principal_equipos.setContentsMargins(
            20, 20, 20, 20
        )
        layout_principal_equipos.setSpacing(25)

        # -------- FORMULARIO --------

        info_formulario = QGroupBox("DATOS DEL EQUIPO")
        layout_contenedor_form = QVBoxLayout(info_formulario)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.cbx_cliente_asociado = QComboBox()
        self.cbx_cliente_asociado.addItem(
            "Seleccione un cliente", None
        )

        self.cbx_tipo_equipo = QComboBox()
        self.cbx_tipo_equipo.addItems([
            "Laptop",
            "Computadora de Escritorio",
            "Teléfono",
            "Otros"
        ])

        self.txt_marca = QLineEdit()
        self.txt_modelo = QLineEdit()
        self.txt_numero_serie_equipo = QLineEdit()

        self.date_fecha_registro = QDateEdit()
        self.date_fecha_registro.setDate(
            QDate.currentDate()
        )
        self.date_fecha_registro.setCalendarPopup(True)
        self.date_fecha_registro.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.cbx_estado_equipo = QComboBox()
        self.cbx_estado_equipo.addItems([
            "No enciende",
            "Enciende pero no da video",
            "Enciende con error de pantalla negra",
            "Reinicio constante"
        ])

        self.txtEd_descripcion_equipo = QTextEdit()
        self.txtEd_descripcion_equipo.setMaximumHeight(80)

        # -------- CAMPOS --------

        form_layout.addRow(
            "Cliente:", self.cbx_cliente_asociado
        )
        form_layout.addRow(
            "Tipo de equipo:", self.cbx_tipo_equipo
        )
        form_layout.addRow("Marca:", self.txt_marca)
        form_layout.addRow("Modelo:", self.txt_modelo)
        form_layout.addRow(
            "Número de serie:",
            self.txt_numero_serie_equipo
        )
        form_layout.addRow(
            "Fecha de registro:",
            self.date_fecha_registro
        )
        form_layout.addRow(
            "Estado:", self.cbx_estado_equipo
        )
        form_layout.addRow(
            "Descripción del problema:",
            self.txtEd_descripcion_equipo
        )

        # -------- BOTONES --------

        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar Equipo")
        self.btn_editar = QPushButton("Editar Equipo")
        self.btn_eliminar = QPushButton("Eliminar Equipo")
        self.btn_limpiar = QPushButton("Limpiar")

        layout_botones.addWidget(self.btn_guardar)
        layout_botones.addWidget(self.btn_editar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_botones.addWidget(self.btn_limpiar)

        layout_contenedor_form.addLayout(form_layout)
        layout_contenedor_form.addLayout(layout_botones)
        layout_contenedor_form.addStretch()

        # -------- TABLA Y BÚSQUEDA --------

        info_tabla = QGroupBox("Listado de Equipos")
        layout_contenedor_tabla = QVBoxLayout(info_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por ID, cliente, marca, modelo o serie..."
        )

        self.tabla_equipos = QTableWidget()
        self.tabla_equipos.setColumnCount(6)

        self.tabla_equipos.setHorizontalHeaderLabels([
            "Cliente",
            "Marca",
            "Modelo",
            "Número de serie",
            "Fecha de registro",
            "Estado"
        ])

        self.tabla_equipos.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla_equipos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla_equipos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla_equipos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        layout_contenedor_tabla.addWidget(self.txt_buscar)
        layout_contenedor_tabla.addWidget(self.tabla_equipos)

        # -------- DISTRIBUCIÓN PRINCIPAL --------

        layout_principal_equipos.addWidget(
            info_formulario, 1
        )
        layout_principal_equipos.addWidget(
            info_tabla, 2
        )

        self.actualizar_botones()

    # ==========================================
    # 3. CONEXIÓN DE EVENTOS
    # ==========================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_equipos
        )

        self.btn_editar.clicked.connect(
            self.editar_equipo
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_equipo
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_equipos
        )

        self.tabla_equipos.itemSelectionChanged.connect(
            self.seleccionar_equipo
        )

    # ==========================================
    # 4. CARGAR CLIENTES DESDE MYSQL
    # ==========================================

    def cargar_clientes(self):

        try:
            clientes = self.controller.listar_clientes()

            self.cbx_cliente_asociado.clear()
            self.cbx_cliente_asociado.addItem(
                "Seleccione un cliente", None
            )

            for cliente in clientes:
                self.cbx_cliente_asociado.addItem(
                    cliente["nombre_completo"],
                    cliente["id_cliente"]
                )

        except RuntimeError as error:
            QMessageBox.warning(
                self,
                "Error de consulta",
                str(error)
            )

    # ==========================================
    # 5. OBTENER DATOS DEL FORMULARIO
    # ==========================================

    def obtener_datos_formulario(self):

        # Convertir QDate a date de Python
        fecha = self.date_fecha_registro.date()

        fecha_python = fecha.toPython()

        return {
            "id_cliente": (
                self.cbx_cliente_asociado.currentData()
            ),
            "tipo": self.cbx_tipo_equipo.currentText(),
            "marca": self.txt_marca.text().strip(),
            "modelo": self.txt_modelo.text().strip(),
            "numero_serie": (
                self.txt_numero_serie_equipo.text().strip()
            ),
            "fecha_registro": fecha_python,
            "estado_recepcion": (
                self.cbx_estado_equipo.currentText()
            ),
            "descripcion_problema": (
                self.txtEd_descripcion_equipo
                .toPlainText().strip()
            )
        }

    # ==========================================
    # 6. REGISTRAR EQUIPO
    # ==========================================

    def guardar_equipos(self):

        if self.id_equipo_seleccionado is not None:
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.registrar_equipo(datos)

            self.cargar_equipos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Registro exitoso",
                "El equipo fue registrado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al registrar",
                str(error)
            )

    # ==========================================
    # 7. CONSULTAR EQUIPOS DESDE MYSQL
    # ==========================================

    def cargar_equipos(self):

        try:
            equipos = self.controller.listar_equipos()

        except RuntimeError as error:
            QMessageBox.warning(
                self,
                "Error de consulta",
                str(error)
            )
            return

        # Almacenar los registros por su ID
        self.equipos_cargados = {
            equipo["id_equipo"]: equipo
            for equipo in equipos
        }

        # Evitar señales durante la actualización
        self.tabla_equipos.blockSignals(True)

        try:
            self.tabla_equipos.setRowCount(0)

            for equipo in equipos:

                fila = self.tabla_equipos.rowCount()
                self.tabla_equipos.insertRow(fila)

                fecha = equipo["fecha_registro"]

                valores = [
                    equipo["nombre_cliente"],
                    equipo["marca"],
                    equipo["modelo"] or "",
                    equipo["numero_serie"] or "",
                    fecha.strftime("%d/%m/%Y"),
                    equipo["estado_recepcion"]
                ]

                for columna, valor in enumerate(valores):

                    item = QTableWidgetItem(str(valor))

                    if columna == 0:
                        item.setData(
                            Qt.UserRole,
                            equipo["id_equipo"]
                        )

                    self.tabla_equipos.setItem(
                        fila,
                        columna,
                        item
                    )

            self.tabla_equipos.clearSelection()
            self.tabla_equipos.setCurrentCell(-1, -1)

        finally:
            self.tabla_equipos.blockSignals(False)

        self.id_equipo_seleccionado = None
        self.actualizar_botones()
        self.filtrar_equipos(self.txt_buscar.text())

    # ==========================================
    # 8. SELECCIONAR EQUIPO
    # ==========================================

    def seleccionar_equipo(self):

        fila = self.tabla_equipos.currentRow()

        if (
            fila < 0
            or not self.tabla_equipos.selectedItems()
        ):
            self.id_equipo_seleccionado = None
            self.actualizar_botones()
            return

        item = self.tabla_equipos.item(fila, 0)

        if item is None:
            return

        id_equipo = item.data(Qt.UserRole)

        equipo = self.equipos_cargados.get(id_equipo)

        if equipo is None:
            return

        self.id_equipo_seleccionado = id_equipo

        # Recuperar cliente asociado
        indice_cliente = (
            self.cbx_cliente_asociado.findData(
                equipo["id_cliente"]
            )
        )

        if indice_cliente >= 0:
            self.cbx_cliente_asociado.setCurrentIndex(
                indice_cliente
            )

        # Recuperar tipo de equipo
        indice_tipo = self.cbx_tipo_equipo.findText(
            equipo["tipo"]
        )

        if indice_tipo >= 0:
            self.cbx_tipo_equipo.setCurrentIndex(
                indice_tipo
            )

        # Recuperar datos de texto
        self.txt_marca.setText(equipo["marca"])
        self.txt_modelo.setText(
            equipo["modelo"] or ""
        )

        self.txt_numero_serie_equipo.setText(
            equipo["numero_serie"] or ""
        )

        # Recuperar fecha
        fecha = equipo["fecha_registro"]

        self.date_fecha_registro.setDate(
            QDate(
                fecha.year,
                fecha.month,
                fecha.day
            )
        )

        # Recuperar estado
        indice_estado = self.cbx_estado_equipo.findText(
            equipo["estado_recepcion"]
        )

        if indice_estado >= 0:
            self.cbx_estado_equipo.setCurrentIndex(
                indice_estado
            )

        self.txtEd_descripcion_equipo.setPlainText(
            equipo["descripcion_problema"] or ""
        )

        self.actualizar_botones()

    # ==========================================
    # 9. EDITAR EQUIPO
    # ==========================================

    def editar_equipo(self):

        if self.id_equipo_seleccionado is None:
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_equipo(
                self.id_equipo_seleccionado,
                datos
            )

            self.cargar_equipos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "El equipo fue actualizado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al actualizar",
                str(error)
            )

    # ==========================================
    # 10. ELIMINAR EQUIPO
    # ==========================================

    def eliminar_equipo(self):

        if self.id_equipo_seleccionado is None:
            return

        equipo = self.equipos_cargados.get(
            self.id_equipo_seleccionado
        )

        if equipo is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            (
                "¿Desea eliminar el equipo "
                f'{equipo["marca"]} '
                f'{equipo["modelo"] or ""}?'
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:
            self.controller.eliminar_equipo(
                self.id_equipo_seleccionado
            )

            self.cargar_equipos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "El equipo fue eliminado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al eliminar",
                str(error)
            )

    # ==========================================
    # 11. BUSCAR EQUIPOS
    # ==========================================

    def filtrar_equipos(self, texto):

        texto = texto.strip().casefold()

        for fila in range(self.tabla_equipos.rowCount()):

            item_id = self.tabla_equipos.item(fila, 0)

            if item_id is None:
                continue

            id_equipo = item_id.data(Qt.UserRole)

            equipo = self.equipos_cargados.get(
                id_equipo
            )

            if equipo is None:
                continue

            contenido = " ".join([
                str(equipo["id_equipo"]),
                equipo["nombre_cliente"],
                equipo["tipo"],
                equipo["marca"],
                equipo["modelo"] or "",
                equipo["numero_serie"] or ""
            ]).casefold()

            self.tabla_equipos.setRowHidden(
                fila,
                texto not in contenido
            )

    # ==========================================
    # 12. CONTROL DE BOTONES
    # ==========================================

    def actualizar_botones(self):

        hay_seleccion = (
            self.id_equipo_seleccionado is not None
        )

        self.btn_guardar.setEnabled(
            not hay_seleccion
        )

        self.btn_editar.setEnabled(
            hay_seleccion
        )

        self.btn_eliminar.setEnabled(
            hay_seleccion
        )

    # ==========================================
    # 13. LIMPIAR FORMULARIO
    # ==========================================

    def limpiar_formulario(self):

        self.id_equipo_seleccionado = None

        self.tabla_equipos.blockSignals(True)

        try:
            self.tabla_equipos.clearSelection()
            self.tabla_equipos.setCurrentCell(-1, -1)
        finally:
            self.tabla_equipos.blockSignals(False)

        self.cbx_cliente_asociado.setCurrentIndex(0)
        self.cbx_tipo_equipo.setCurrentIndex(0)

        self.txt_marca.clear()
        self.txt_modelo.clear()
        self.txt_numero_serie_equipo.clear()

        self.date_fecha_registro.setDate(
            QDate.currentDate()
        )

        self.cbx_estado_equipo.setCurrentIndex(0)
        self.txtEd_descripcion_equipo.clear()

        self.actualizar_botones()
        self.txt_marca.setFocus()

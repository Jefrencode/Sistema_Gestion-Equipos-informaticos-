
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QMessageBox,
    QHeaderView, QTableWidget, QTableWidgetItem,
    QGroupBox, QDateEdit, QTextEdit,
    QAbstractItemView
)

from PySide6.QtCore import QDate, Qt

from controllers.mantenimiento_controller import MantenimientosController


class Mantenimientos_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = MantenimientosController()

        self.id_mantenimiento_seleccionado = None
        self.mantenimientos = []

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_datos_iniciales()

    # ==============================================
    # CREAR INTERFAZ
    # ==============================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # FORMULARIO DE MANTENIMIENTOS

        grupo_formulario = QGroupBox(
            "Datos del mantenimiento"
        )

        layout_formulario = QVBoxLayout(
            grupo_formulario
        )

        formulario = QFormLayout()
        formulario.setSpacing(15)

        # EQUIPO
        self.cbx_equipo = QComboBox()
        formulario.addRow(
            "Equipo:", self.cbx_equipo
        )

        # TIPO
        self.cbx_tipo_mantenimiento = QComboBox()
        self.cbx_tipo_mantenimiento.addItems([
            "Preventivo",
            "Correctivo"
        ])

        formulario.addRow(
            "Tipo de mantenimiento:",
            self.cbx_tipo_mantenimiento
        )

        # FECHA
        self.date_fecha_mantenimiento = QDateEdit()
        self.date_fecha_mantenimiento.setDate(
            QDate.currentDate()
        )
        self.date_fecha_mantenimiento.setCalendarPopup(
            True
        )
        self.date_fecha_mantenimiento.setDisplayFormat(
            "dd/MM/yyyy"
        )

        formulario.addRow(
            "Fecha de mantenimiento:",
            self.date_fecha_mantenimiento
        )

        # DESCRIPCIÓN
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setPlaceholderText(
            "Describe las actividades realizadas..."
        )

        formulario.addRow(
            "Descripción:", self.txt_descripcion
        )

        # RESPONSABLE
        self.txt_responsable = QLineEdit()
        self.txt_responsable.setMaxLength(160)
        self.txt_responsable.setPlaceholderText(
            "Nombre del responsable"
        )

        formulario.addRow(
            "Responsable:", self.txt_responsable
        )

        # COSTO
        self.txt_costo = QLineEdit()
        self.txt_costo.setPlaceholderText(
            "Ej. 350.00"
        )

        formulario.addRow(
            "Costo (C$):", self.txt_costo
        )

        # ESTADO
        self.cbx_estado = QComboBox()
        formulario.addRow(
            "Estado:", self.cbx_estado
        )

        layout_formulario.addLayout(formulario)

        # BOTONES
        self.btn_guardar = QPushButton(
            "Guardar mantenimiento"
        )

        self.btn_editar = QPushButton(
            "Editar mantenimiento"
        )

        self.btn_eliminar = QPushButton(
            "Eliminar mantenimiento"
        )

        self.btn_limpiar = QPushButton("Limpiar")

        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        layout_formulario.addWidget(
            self.btn_guardar
        )
        layout_formulario.addWidget(
            self.btn_editar
        )
        layout_formulario.addWidget(
            self.btn_eliminar
        )
        layout_formulario.addWidget(
            self.btn_limpiar
        )

        # TABLA
        grupo_tabla = QGroupBox(
            "Registro de mantenimientos"
        )

        layout_tabla = QVBoxLayout(
            grupo_tabla
        )

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar mantenimiento..."
        )

        layout_tabla.addWidget(
            self.txt_buscar
        )

        self.tabla_mantenimientos = QTableWidget()
        self.tabla_mantenimientos.setColumnCount(7)

        self.tabla_mantenimientos.setHorizontalHeaderLabels([
            "Equipo",
            "Tipo",
            "Fecha",
            "Descripción",
            "Responsable",
            "Costo (C$)",
            "Estado"
        ])

        self.tabla_mantenimientos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_mantenimientos.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla_mantenimientos.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla_mantenimientos.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        layout_tabla.addWidget(
            self.tabla_mantenimientos
        )

        layout_principal.addWidget(
            grupo_formulario, 1
        )

        layout_principal.addWidget(
            grupo_tabla, 2
        )

    # ==============================================
    # CONECTAR BOTONES Y EVENTOS
    # ==============================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_mantenimiento
        )

        self.btn_editar.clicked.connect(
            self.editar_mantenimiento
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_mantenimiento
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_mantenimientos
        )

        self.tabla_mantenimientos.itemSelectionChanged.connect(
            self.seleccionar_mantenimiento
        )

    # ==============================================
    # CARGAR DATOS INICIALES
    # ==============================================

    def cargar_datos_iniciales(self):

        self.cargar_equipos()
        self.cargar_estados()
        self.cargar_mantenimientos()

    # ==============================================
    # CARGAR EQUIPOS DESDE MYSQL
    # ==============================================

    def cargar_equipos(self):

        self.cbx_equipo.clear()
        self.cbx_equipo.addItem(
            "Seleccione un equipo", None
        )

        try:
            equipos = self.controller.listar_equipos()

            for equipo in equipos:

                self.cbx_equipo.addItem(
                    equipo["descripcion"],
                    equipo["id_equipo"]
                )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error al cargar equipos",
                str(error)
            )

    # ==============================================
    # CARGAR ESTADOS DESDE MYSQL
    # ==============================================

    def cargar_estados(self):

        self.cbx_estado.clear()
        self.cbx_estado.addItem(
            "Seleccione un estado", None
        )

        try:
            estados = self.controller.listar_estados()

            for estado in estados:

                self.cbx_estado.addItem(
                    estado["nombre"],
                    estado["id_estado"]
                )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error al cargar estados",
                str(error)
            )

    # ==============================================
    # DATOS DEL FORMULARIO
    # ==============================================

    def obtener_datos_formulario(self):

        return {
            "id_equipo":
                self.cbx_equipo.currentData(),

            "tipo_mantenimiento":
                self.cbx_tipo_mantenimiento.currentText(),

            "fecha":
                self.date_fecha_mantenimiento.date().toPython(),

            "descripcion":
                self.txt_descripcion.toPlainText().strip(),

            "responsable":
                self.txt_responsable.text().strip(),

            "costo":
                self.txt_costo.text().strip(),

            "id_estado":
                self.cbx_estado.currentData()
        }

    # ==============================================
    # GUARDAR MANTENIMIENTO
    # ==============================================

    def guardar_mantenimiento(self):

        datos = self.obtener_datos_formulario()

        try:
            id_mantenimiento = (
                self.controller.registrar_mantenimiento(
                    datos
                )
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"Mantenimiento #{id_mantenimiento} "
                "registrado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_mantenimientos()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error)
            )

    # ==============================================
    # CONSULTAR MANTENIMIENTOS
    # ==============================================

    def cargar_mantenimientos(self):

        try:
            self.mantenimientos = (
                self.controller.listar_mantenimientos()
            )

            self.filtrar_mantenimientos(
                self.txt_buscar.text()
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error de consulta",
                str(error)
            )

    # ==============================================
    # MOSTRAR EN LA TABLA
    # ==============================================

    def mostrar_mantenimientos(self, mantenimientos):

        self.tabla_mantenimientos.blockSignals(True)

        try:
            self.tabla_mantenimientos.setRowCount(0)

            for mantenimiento in mantenimientos:

                fila = self.tabla_mantenimientos.rowCount()
                self.tabla_mantenimientos.insertRow(fila)

                datos = [
                    mantenimiento["nombre_equipo"],
                    mantenimiento["tipo_mantenimiento"],
                    mantenimiento["fecha"].strftime(
                        "%d/%m/%Y"
                    ),
                    mantenimiento["descripcion"],
                    mantenimiento["responsable"],
                    f"{mantenimiento['costo']:.2f}",
                    mantenimiento["nombre_estado"]
                ]

                for columna, dato in enumerate(datos):

                    item = QTableWidgetItem(
                        str(dato)
                    )

                    if columna == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            mantenimiento["id_mantenimiento"]
                        )

                    self.tabla_mantenimientos.setItem(
                        fila,
                        columna,
                        item
                    )

        finally:
            self.tabla_mantenimientos.blockSignals(
                False
            )

    # ==============================================
    # BUSCAR MANTENIMIENTOS
    # ==============================================

    def filtrar_mantenimientos(self, texto):

        # Limpiar selección anterior para evitar
        # editar un registro que ya no esté visible.
        self.id_mantenimiento_seleccionado = None
        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        texto = texto.strip().lower()

        resultados = []

        for mantenimiento in self.mantenimientos:

            contenido = " ".join([
                str(mantenimiento["id_mantenimiento"]),
                mantenimiento["nombre_equipo"],
                mantenimiento["tipo_mantenimiento"],
                mantenimiento["fecha"].strftime(
                    "%d/%m/%Y"
                ),
                mantenimiento["descripcion"],
                mantenimiento["responsable"],
                str(mantenimiento["costo"]),
                mantenimiento["nombre_estado"]
            ]).lower()

            if texto in contenido:
                resultados.append(mantenimiento)

        self.mostrar_mantenimientos(resultados)

    # ==============================================
    # SELECCIONAR MANTENIMIENTO
    # ==============================================

    def seleccionar_mantenimiento(self):

        fila = self.tabla_mantenimientos.currentRow()

        if fila < 0:
            return

        item = self.tabla_mantenimientos.item(
            fila, 0
        )

        if item is None:
            return

        id_mantenimiento = item.data(
            Qt.ItemDataRole.UserRole
        )

        mantenimiento = next(
            (
                m for m in self.mantenimientos
                if m["id_mantenimiento"]
                == id_mantenimiento
            ),
            None
        )

        if mantenimiento is None:
            return

        self.id_mantenimiento_seleccionado = (
            id_mantenimiento
        )

        # EQUIPO
        indice_equipo = self.cbx_equipo.findData(
            mantenimiento["id_equipo"]
        )

        if indice_equipo >= 0:
            self.cbx_equipo.setCurrentIndex(
                indice_equipo
            )

        # TIPO
        indice_tipo = (
            self.cbx_tipo_mantenimiento.findText(
                mantenimiento["tipo_mantenimiento"]
            )
        )

        if indice_tipo >= 0:
            self.cbx_tipo_mantenimiento.setCurrentIndex(
                indice_tipo
            )

        # FECHA
        fecha = mantenimiento["fecha"]

        self.date_fecha_mantenimiento.setDate(
            QDate(
                fecha.year,
                fecha.month,
                fecha.day
            )
        )

        # DESCRIPCIÓN
        self.txt_descripcion.setPlainText(
            mantenimiento["descripcion"]
        )

        # RESPONSABLE
        self.txt_responsable.setText(
            mantenimiento["responsable"]
        )

        # COSTO
        self.txt_costo.setText(
            f"{mantenimiento['costo']:.2f}"
        )

        # ESTADO
        indice_estado = self.cbx_estado.findData(
            mantenimiento["id_estado"]
        )

        if indice_estado >= 0:
            self.cbx_estado.setCurrentIndex(
                indice_estado
            )

        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    # ==============================================
    # EDITAR MANTENIMIENTO
    # ==============================================

    def editar_mantenimiento(self):

        if self.id_mantenimiento_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un mantenimiento para editar."
            )
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_mantenimiento(
                self.id_mantenimiento_seleccionado,
                datos
            )

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "Mantenimiento actualizado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_mantenimientos()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

    # ==============================================
    # ELIMINAR MANTENIMIENTO
    # ==============================================

    def eliminar_mantenimiento(self):

        if self.id_mantenimiento_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un mantenimiento para eliminar."
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar este mantenimiento?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.controller.eliminar_mantenimiento(
                self.id_mantenimiento_seleccionado
            )

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "Mantenimiento eliminado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_mantenimientos()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                str(error)
            )

    # ==============================================
    # LIMPIAR FORMULARIO
    # ==============================================

    def limpiar_formulario(self):

        self.id_mantenimiento_seleccionado = None

        self.cbx_equipo.setCurrentIndex(0)
        self.cbx_tipo_mantenimiento.setCurrentIndex(0)

        self.date_fecha_mantenimiento.setDate(
            QDate.currentDate()
        )

        self.txt_descripcion.clear()
        self.txt_responsable.clear()
        self.txt_costo.clear()

        self.cbx_estado.setCurrentIndex(0)

        self.tabla_mantenimientos.clearSelection()

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.txt_descripcion.setFocus()

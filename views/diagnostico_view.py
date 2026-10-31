
# ==========================================
# VISTA: GESTIÓN DE DIAGNÓSTICOS
# ==========================================

from PySide6.QtCore import QDate, Qt

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QDateEdit,
    QTextEdit,
    QAbstractItemView
)

from controllers.diagnostico_controller import DiagnosticosController


class Diagnostico_Equipos(QWidget):

    # ==========================================
    # 1. INICIALIZACIÓN
    # ==========================================

    def __init__(self):
        super().__init__()

        self.controller = DiagnosticosController()

        # Identificador del diagnóstico seleccionado
        self.id_diagnostico_seleccionado = None

        # Registros obtenidos desde MySQL
        self.diagnosticos_cargados = {}

        self.crear_interfaz()
        self.conexiones_botones()

        self.cargar_equipos()
        self.cargar_diagnosticos()

    # ==========================================
    # 2. CONSTRUCCIÓN DE LA INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # -------- FORMULARIO --------

        grupo_formulario = QGroupBox("Datos del diagnóstico")
        layout_formulario = QVBoxLayout(grupo_formulario)

        formulario_diagnostico = QFormLayout()
        formulario_diagnostico.setSpacing(10)

        # Equipo asociado
        self.cbx_equipo_diagnosticado = QComboBox()
        self.cbx_equipo_diagnosticado.addItem(
            "Seleccione un equipo", None
        )

        # Fecha
        self.date_fecha_diagnostico = QDateEdit()
        self.date_fecha_diagnostico.setDate(
            QDate.currentDate()
        )
        self.date_fecha_diagnostico.setCalendarPopup(True)
        self.date_fecha_diagnostico.setDisplayFormat(
            "dd/MM/yyyy"
        )

        # Síntoma
        self.txt_sintoma = QLineEdit()
        self.txt_sintoma.setPlaceholderText(
            "Ej.: el equipo no enciende"
        )

        # Evaluación
        self.txt_evaluacion = QTextEdit()
        self.txt_evaluacion.setPlaceholderText(
            "Describa las comprobaciones y pruebas realizadas..."
        )
        self.txt_evaluacion.setMaximumHeight(90)

        # Resultado
        self.txt_resultado = QTextEdit()
        self.txt_resultado.setPlaceholderText(
            "Describa el resultado del diagnóstico..."
        )
        self.txt_resultado.setMaximumHeight(90)

        # Observación (campo opcional)
        self.txt_observacion = QTextEdit()
        self.txt_observacion.setPlaceholderText(
            "Recomendaciones u observaciones adicionales..."
        )
        self.txt_observacion.setMaximumHeight(80)

        # -------- CAMPOS DEL FORMULARIO --------

        formulario_diagnostico.addRow(
            "Equipo:",
            self.cbx_equipo_diagnosticado
        )

        formulario_diagnostico.addRow(
            "Fecha del diagnóstico:",
            self.date_fecha_diagnostico
        )

        formulario_diagnostico.addRow(
            "Síntoma:",
            self.txt_sintoma
        )

        formulario_diagnostico.addRow(
            "Evaluación:",
            self.txt_evaluacion
        )

        formulario_diagnostico.addRow(
            "Resultado:",
            self.txt_resultado
        )

        formulario_diagnostico.addRow(
            "Observación:",
            self.txt_observacion
        )

        # -------- BOTONES --------

        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton(
            "Guardar diagnóstico"
        )
        self.btn_editar = QPushButton(
            "Editar diagnóstico"
        )
        self.btn_eliminar = QPushButton(
            "Eliminar diagnóstico"
        )
        self.btn_limpiar = QPushButton("Limpiar")

        layout_botones.addWidget(self.btn_guardar)
        layout_botones.addWidget(self.btn_editar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_botones.addWidget(self.btn_limpiar)

        layout_formulario.addLayout(formulario_diagnostico)
        layout_formulario.addLayout(layout_botones)
        layout_formulario.addStretch()

        # -------- TABLA --------

        grupo_tabla = QGroupBox("Listado de diagnósticos")
        layout_tabla = QVBoxLayout(grupo_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por ID, equipo, cliente o síntoma..."
        )

        self.tabla_diagnosticos = QTableWidget()
        self.tabla_diagnosticos.setColumnCount(5)

        self.tabla_diagnosticos.setHorizontalHeaderLabels([
            "Equipo",
            "Fecha",
            "Síntoma",
            "Evaluación",
            "Resultado"
        ])

        self.tabla_diagnosticos.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla_diagnosticos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabla_diagnosticos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabla_diagnosticos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        layout_tabla.addWidget(self.txt_buscar)
        layout_tabla.addWidget(self.tabla_diagnosticos)

        # -------- DISTRIBUCIÓN PRINCIPAL --------

        layout_principal.addWidget(grupo_formulario, 1)
        layout_principal.addWidget(grupo_tabla, 2)

        self.actualizar_botones()

    # ==========================================
    # 3. CONEXIÓN DE EVENTOS
    # ==========================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_diagnostico
        )

        self.btn_editar.clicked.connect(
            self.editar_diagnostico
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_diagnostico
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_diagnosticos
        )

        self.tabla_diagnosticos.itemSelectionChanged.connect(
            self.seleccionar_diagnostico
        )

    # ==========================================
    # 4. CARGAR EQUIPOS DESDE MYSQL
    # ==========================================

    def cargar_equipos(self):

        try:
            equipos = self.controller.listar_equipos()

            self.cbx_equipo_diagnosticado.clear()
            self.cbx_equipo_diagnosticado.addItem(
                "Seleccione un equipo", None
            )

            for equipo in equipos:
                self.cbx_equipo_diagnosticado.addItem(
                    equipo["descripcion"],
                    equipo["id_equipo"]
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

        fecha = self.date_fecha_diagnostico.date()

        return {
            "id_equipo": (
                self.cbx_equipo_diagnosticado.currentData()
            ),
            "fecha": fecha.toPython(),
            "sintoma": self.txt_sintoma.text().strip(),
            "evaluacion": (
                self.txt_evaluacion.toPlainText().strip()
            ),
            "resultado": (
                self.txt_resultado.toPlainText().strip()
            ),
            "observacion": (
                self.txt_observacion.toPlainText().strip()
            )
        }

    # ==========================================
    # 6. GUARDAR DIAGNÓSTICO
    # ==========================================

    def guardar_diagnostico(self):

        if self.id_diagnostico_seleccionado is not None:
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.registrar_diagnostico(datos)

            self.cargar_diagnosticos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Registro exitoso",
                "El diagnóstico fue registrado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al registrar",
                str(error)
            )

    # ==========================================
    # 7. CARGAR DIAGNÓSTICOS DESDE MYSQL
    # ==========================================

    def cargar_diagnosticos(self):

        try:
            diagnosticos = (
                self.controller.listar_diagnosticos()
            )

        except RuntimeError as error:
            QMessageBox.warning(
                self,
                "Error de consulta",
                str(error)
            )
            return

        self.diagnosticos_cargados = {
            diagnostico["id_diagnostico"]: diagnostico
            for diagnostico in diagnosticos
        }

        self.tabla_diagnosticos.blockSignals(True)

        try:
            self.tabla_diagnosticos.setRowCount(0)

            for diagnostico in diagnosticos:

                fila = self.tabla_diagnosticos.rowCount()
                self.tabla_diagnosticos.insertRow(fila)

                fecha = diagnostico["fecha"]

                valores = [
                    diagnostico["nombre_equipo"],
                    fecha.strftime("%d/%m/%Y"),
                    diagnostico["sintoma"],
                    diagnostico["evaluacion"],
                    diagnostico["resultado"]
                ]

                for columna, valor in enumerate(valores):

                    item = QTableWidgetItem(str(valor))

                    if columna == 0:
                        item.setData(
                            Qt.UserRole,
                            diagnostico["id_diagnostico"]
                        )

                    self.tabla_diagnosticos.setItem(
                        fila,
                        columna,
                        item
                    )

            self.tabla_diagnosticos.clearSelection()
            self.tabla_diagnosticos.setCurrentCell(-1, -1)

        finally:
            self.tabla_diagnosticos.blockSignals(False)

        self.id_diagnostico_seleccionado = None
        self.actualizar_botones()

        self.filtrar_diagnosticos(
            self.txt_buscar.text()
        )

    # ==========================================
    # 8. SELECCIONAR DIAGNÓSTICO
    # ==========================================

    def seleccionar_diagnostico(self):

        fila = self.tabla_diagnosticos.currentRow()

        if (
            fila < 0
            or not self.tabla_diagnosticos.selectedItems()
        ):
            self.id_diagnostico_seleccionado = None
            self.actualizar_botones()
            return

        item = self.tabla_diagnosticos.item(fila, 0)

        if item is None:
            return

        id_diagnostico = item.data(Qt.UserRole)

        diagnostico = self.diagnosticos_cargados.get(
            id_diagnostico
        )

        if diagnostico is None:
            return

        self.id_diagnostico_seleccionado = id_diagnostico

        # Seleccionar equipo asociado
        indice_equipo = (
            self.cbx_equipo_diagnosticado.findData(
                diagnostico["id_equipo"]
            )
        )

        if indice_equipo >= 0:
            self.cbx_equipo_diagnosticado.setCurrentIndex(
                indice_equipo
            )

        # Fecha
        fecha = diagnostico["fecha"]

        self.date_fecha_diagnostico.setDate(
            QDate(
                fecha.year,
                fecha.month,
                fecha.day
            )
        )

        # Datos del diagnóstico
        self.txt_sintoma.setText(
            diagnostico["sintoma"]
        )

        self.txt_evaluacion.setPlainText(
            diagnostico["evaluacion"]
        )

        self.txt_resultado.setPlainText(
            diagnostico["resultado"]
        )

        self.txt_observacion.setPlainText(
            diagnostico["observacion"] or ""
        )

        self.actualizar_botones()

    # ==========================================
    # 9. EDITAR DIAGNÓSTICO
    # ==========================================

    def editar_diagnostico(self):

        if self.id_diagnostico_seleccionado is None:
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_diagnostico(
                self.id_diagnostico_seleccionado,
                datos
            )

            self.cargar_diagnosticos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "El diagnóstico fue actualizado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al actualizar",
                str(error)
            )

    # ==========================================
    # 10. ELIMINAR DIAGNÓSTICO
    # ==========================================

    def eliminar_diagnostico(self):

        if self.id_diagnostico_seleccionado is None:
            return

        diagnostico = self.diagnosticos_cargados.get(
            self.id_diagnostico_seleccionado
        )

        if diagnostico is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            (
                "¿Desea eliminar el diagnóstico del equipo "
                f'{diagnostico["nombre_equipo"]}?'
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:
            self.controller.eliminar_diagnostico(
                self.id_diagnostico_seleccionado
            )

            self.cargar_diagnosticos()
            self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "El diagnóstico fue eliminado correctamente."
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error al eliminar",
                str(error)
            )

    # ==========================================
    # 11. BUSCAR DIAGNÓSTICOS
    # ==========================================

    def filtrar_diagnosticos(self, texto):

        texto = texto.strip().casefold()

        for fila in range(
            self.tabla_diagnosticos.rowCount()
        ):

            item = self.tabla_diagnosticos.item(
                fila, 0
            )

            if item is None:
                continue

            id_diagnostico = item.data(Qt.UserRole)

            diagnostico = self.diagnosticos_cargados.get(
                id_diagnostico
            )

            if diagnostico is None:
                continue

            contenido = " ".join([
                str(diagnostico["id_diagnostico"]),
                diagnostico["nombre_equipo"],
                diagnostico["nombre_cliente"],
                diagnostico["sintoma"],
                diagnostico["evaluacion"],
                diagnostico["resultado"]
            ]).casefold()

            self.tabla_diagnosticos.setRowHidden(
                fila,
                texto not in contenido
            )

    # ==========================================
    # 12. ACTUALIZAR BOTONES
    # ==========================================

    def actualizar_botones(self):

        hay_seleccion = (
            self.id_diagnostico_seleccionado is not None
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

        self.id_diagnostico_seleccionado = None

        self.tabla_diagnosticos.blockSignals(True)

        try:
            self.tabla_diagnosticos.clearSelection()
            self.tabla_diagnosticos.setCurrentCell(-1, -1)
        finally:
            self.tabla_diagnosticos.blockSignals(False)

        self.cbx_equipo_diagnosticado.setCurrentIndex(0)

        self.date_fecha_diagnostico.setDate(
            QDate.currentDate()
        )

        self.txt_sintoma.clear()
        self.txt_evaluacion.clear()
        self.txt_resultado.clear()
        self.txt_observacion.clear()

        self.actualizar_botones()
        self.txt_sintoma.setFocus()


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QDateEdit,
    QLabel,
    QFileDialog
)

from PySide6.QtCore import QDate

from controllers.reportes_controller import (
    ReportesController
)


class Reportes_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = ReportesController()

        self.registros_reporte = []
        self.reporte_generado = False

        self.crear_interfaz()
        self.conexiones_botones()

    # ==========================================
    # CREAR INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(
            20, 20, 20, 20
        )
        layout_principal.setSpacing(20)

        # ENCABEZADO

        titulo = QLabel(
            "Reportes del sistema"
        )

        descripcion = QLabel(
            "Consulta y exporta información de "
            "los equipos y las actividades del taller."
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # ======================================
        # FILTROS
        # ======================================

        grupo_filtros = QGroupBox(
            "Parámetros del reporte"
        )

        layout_filtros = QVBoxLayout(
            grupo_filtros
        )

        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.cbx_tipo_reporte = QComboBox()

        self.cbx_tipo_reporte.addItems([
            "Todos los registros",
            "Equipos",
            "Diagnósticos",
            "Reparaciones",
            "Mantenimientos"
        ])

        formulario.addRow(
            "Tipo de reporte:",
            self.cbx_tipo_reporte
        )

        # FECHA INICIAL

        self.date_fecha_inicio = QDateEdit()

        self.date_fecha_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.date_fecha_inicio.setCalendarPopup(
            True
        )

        self.date_fecha_inicio.setDisplayFormat(
            "dd/MM/yyyy"
        )

        formulario.addRow(
            "Fecha inicial:",
            self.date_fecha_inicio
        )

        # FECHA FINAL

        self.date_fecha_fin = QDateEdit()

        self.date_fecha_fin.setDate(
            QDate.currentDate()
        )

        self.date_fecha_fin.setCalendarPopup(
            True
        )

        self.date_fecha_fin.setDisplayFormat(
            "dd/MM/yyyy"
        )

        formulario.addRow(
            "Fecha final:",
            self.date_fecha_fin
        )

        layout_filtros.addLayout(formulario)

        # ======================================
        # BOTONES
        # ======================================

        botones = QHBoxLayout()

        self.btn_generar = QPushButton(
            "Generar reporte"
        )

        self.btn_exportar = QPushButton(
            "Exportar Excel"
        )

        self.btn_exportar_pdf = QPushButton(
            "Exportar PDF"
        )

        self.btn_limpiar = QPushButton(
            "Limpiar filtros"
        )

        botones.addWidget(
            self.btn_generar
        )

        botones.addWidget(
            self.btn_exportar
        )

        botones.addWidget(
            self.btn_exportar_pdf
        )

        botones.addWidget(
            self.btn_limpiar
        )

        layout_filtros.addLayout(botones)

        layout_principal.addWidget(
            grupo_filtros
        )

        # ======================================
        # TABLA DE RESULTADOS
        # ======================================

        grupo_resultados = QGroupBox(
            "Resultados del reporte"
        )

        layout_resultados = QVBoxLayout(
            grupo_resultados
        )

        self.lbl_total = QLabel(
            "Total de registros: 0"
        )

        layout_resultados.addWidget(
            self.lbl_total
        )

        self.tabla_reportes = QTableWidget()

        self.tabla_reportes.setColumnCount(5)

        self.tabla_reportes.setHorizontalHeaderLabels([
            "Fecha",
            "Tipo",
            "Equipo",
            "Descripción",
            "Estado"
        ])

        self.tabla_reportes.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_reportes.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla_reportes.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabla_reportes.setAlternatingRowColors(
            True
        )

        layout_resultados.addWidget(
            self.tabla_reportes
        )

        layout_principal.addWidget(
            grupo_resultados
        )

        # Inicialmente no hay datos para exportar.

        self.btn_exportar.setEnabled(False)
        self.btn_exportar_pdf.setEnabled(False)

    # ==========================================
    # CONEXIONES DE BOTONES
    # ==========================================

    def conexiones_botones(self):

        self.btn_generar.clicked.connect(
            self.generar_reporte
        )

        self.btn_exportar.clicked.connect(
            self.exportar_excel
        )

        self.btn_exportar_pdf.clicked.connect(
            self.exportar_pdf
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_filtros
        )

        # Invalidar resultados cuando cambien filtros.

        self.cbx_tipo_reporte.currentIndexChanged.connect(
            self.invalidar_reporte
        )

        self.date_fecha_inicio.dateChanged.connect(
            self.invalidar_reporte
        )

        self.date_fecha_fin.dateChanged.connect(
            self.invalidar_reporte
        )

    # ==========================================
    # INVALIDAR REPORTE
    # ==========================================

    def invalidar_reporte(self, *args):

        self.reporte_generado = False
        self.registros_reporte = []

        self.tabla_reportes.setRowCount(0)

        self.actualizar_total()

    # ==========================================
    # GENERAR REPORTE
    # ==========================================

    def generar_reporte(self):

        tipo = (
            self.cbx_tipo_reporte.currentText()
        )

        fecha_inicio = (
            self.date_fecha_inicio.date().toPython()
        )

        fecha_fin = (
            self.date_fecha_fin.date().toPython()
        )

        try:

            registros = (
                self.controller.generar_reporte(
                    tipo,
                    fecha_inicio,
                    fecha_fin
                )
            )

            self.registros_reporte = registros
            self.reporte_generado = True

            self.mostrar_registros()
            self.actualizar_total()

            if not registros:

                QMessageBox.information(
                    self,
                    "Sin resultados",
                    "No se encontraron registros "
                    "en el período seleccionado."
                )

        except (ValueError, RuntimeError) as error:

            self.invalidar_reporte()

            QMessageBox.warning(
                self,
                "Error al generar reporte",
                str(error)
            )

    # ==========================================
    # MOSTRAR REGISTROS
    # ==========================================

    def mostrar_registros(self):

        self.tabla_reportes.setRowCount(0)

        for registro in self.registros_reporte:

            fila = (
                self.tabla_reportes.rowCount()
            )

            self.tabla_reportes.insertRow(
                fila
            )

            datos = [
                registro["fecha"].strftime(
                    "%d/%m/%Y"
                ),
                registro["tipo"],
                registro["equipo"],
                registro["descripcion"],
                registro["estado"]
            ]

            for columna, valor in enumerate(datos):

                item = QTableWidgetItem(
                    str(valor)
                )

                item.setToolTip(
                    str(valor)
                )

                self.tabla_reportes.setItem(
                    fila,
                    columna,
                    item
                )

    # ==========================================
    # ACTUALIZAR TOTAL
    # ==========================================

    def actualizar_total(self):

        total = len(
            self.registros_reporte
        )

        self.lbl_total.setText(
            f"Total de registros: {total}"
        )

        habilitar = (
            self.reporte_generado
            and total > 0
        )

        self.btn_exportar.setEnabled(
            habilitar
        )

        self.btn_exportar_pdf.setEnabled(
            habilitar
        )

    # ==========================================
    # DATOS DEL REPORTE ACTUAL
    # ==========================================

    def obtener_parametros(self):

        return {
            "registros": self.registros_reporte,
            "tipo_reporte": (
                self.cbx_tipo_reporte.currentText()
            ),
            "fecha_inicio": (
                self.date_fecha_inicio.date().toPython()
            ),
            "fecha_fin": (
                self.date_fecha_fin.date().toPython()
            )
        }

    # ==========================================
    # EXPORTAR EXCEL
    # ==========================================

    def exportar_excel(self):

        if (
            not self.reporte_generado
            or not self.registros_reporte
        ):

            QMessageBox.warning(
                self,
                "Sin resultados",
                "Primero debe generar un reporte."
            )
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte Excel",
            "reporte_sistema.xlsx",
            "Archivos Excel (*.xlsx)"
        )

        if not ruta:
            return

        if not ruta.lower().endswith(".xlsx"):
            ruta += ".xlsx"

        try:

            parametros = self.obtener_parametros()

            self.controller.exportar_excel(
                ruta=ruta,
                **parametros
            )

            QMessageBox.information(
                self,
                "Exportación completada",
                "El reporte Excel se guardó "
                "correctamente."
            )

        except (OSError, ValueError, PermissionError) as error:

            QMessageBox.critical(
                self,
                "Error al exportar Excel",
                f"No se pudo guardar el archivo:\n"
                f"{error}"
            )

    # ==========================================
    # EXPORTAR PDF
    # ==========================================

    def exportar_pdf(self):

        if (
            not self.reporte_generado
            or not self.registros_reporte
        ):

            QMessageBox.warning(
                self,
                "Sin resultados",
                "Primero debe generar un reporte."
            )
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte PDF",
            "reporte_sistema.pdf",
            "Archivos PDF (*.pdf)"
        )

        if not ruta:
            return

        if not ruta.lower().endswith(".pdf"):
            ruta += ".pdf"

        try:

            parametros = self.obtener_parametros()

            self.controller.exportar_pdf(
                ruta=ruta,
                **parametros
            )

            QMessageBox.information(
                self,
                "Exportación completada",
                "El reporte PDF se guardó "
                "correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al exportar PDF",
                f"No se pudo generar el archivo:\n"
                f"{error}"
            )

    # ==========================================
    # LIMPIAR FILTROS
    # ==========================================

    def limpiar_filtros(self):

        self.cbx_tipo_reporte.setCurrentIndex(0)

        self.date_fecha_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.date_fecha_fin.setDate(
            QDate.currentDate()
        )

        self.invalidar_reporte()


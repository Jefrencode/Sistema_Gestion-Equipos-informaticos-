
import csv

from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QPushButton,QMessageBox,QHeaderView,QTableWidget,QTableWidgetItem,QGroupBox,QDateEdit,QLabel,QFileDialog
)
from PySide6.QtCore import QDate
 

class Reportes_Equipos(QWidget):

    def __init__(self):
        super().__init__()
        self.crear_interfaz()
        self.conexiones_botones()

    def crear_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # ENCABEZADO

        titulo = QLabel("Reportes del sistema")

        descripcion = QLabel("Consulta y exporta información de los equipos " "y las actividades del taller.")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # FILTROS DEL REPORTE

        grupo_filtros = QGroupBox("Parámetros del reporte")
        layout_filtros = QVBoxLayout(grupo_filtros)

        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.cbx_tipo_reporte = QComboBox()
        self.cbx_tipo_reporte.addItems(["Todos los registros","Equipos","Diagnósticos","Reparaciones","Mantenimientos"])

        formulario.addRow("Tipo de reporte:",self.cbx_tipo_reporte)

        self.date_fecha_inicio = QDateEdit()
        self.date_fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.date_fecha_inicio.setCalendarPopup(True)
        self.date_fecha_inicio.setDisplayFormat("dd/MM/yyyy")

        formulario.addRow("Fecha inicial:",self.date_fecha_inicio)

        self.date_fecha_fin = QDateEdit()
        self.date_fecha_fin.setDate(QDate.currentDate())
        self.date_fecha_fin.setCalendarPopup(True)
        self.date_fecha_fin.setDisplayFormat("dd/MM/yyyy")

        formulario.addRow("Fecha final:",self.date_fecha_fin)

        layout_filtros.addLayout(formulario)

        botones = QHBoxLayout()

        self.btn_generar = QPushButton("Generar reporte")
        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_limpiar = QPushButton("Limpiar filtros")

        botones.addWidget(self.btn_generar)
        botones.addWidget(self.btn_exportar)
        botones.addWidget(self.btn_limpiar)

        layout_filtros.addLayout(botones)
        layout_principal.addWidget(grupo_filtros)


        # TABLA DE RESULTADOS
    

        grupo_resultados = QGroupBox("Resultados del reporte")
        layout_resultados = QVBoxLayout(grupo_resultados)

        self.lbl_total = QLabel("Total de registros: 0")
        layout_resultados.addWidget(self.lbl_total)

        self.tabla_reportes = QTableWidget()
        self.tabla_reportes.setColumnCount(5)

        self.tabla_reportes.setHorizontalHeaderLabels(["Fecha","Tipo","Equipo","Descripción","Estado"])

        self.tabla_reportes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.tabla_reportes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.tabla_reportes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.tabla_reportes.setAlternatingRowColors(True)

        layout_resultados.addWidget(self.tabla_reportes)
        layout_principal.addWidget(grupo_resultados)

        # El reporte inicia vacío hasta consultar los datos.
        self.btn_exportar.setEnabled(False)

    def conexiones_botones(self):
        self.btn_generar.clicked.connect(self.generar_reporte)

        self.btn_exportar.clicked.connect(self.exportar_csv)

        self.btn_limpiar.clicked.connect(self.limpiar_filtros)

    def generar_reporte(self):
        fecha_inicio = self.date_fecha_inicio.date()
        fecha_fin = self.date_fecha_fin.date()

        if fecha_inicio > fecha_fin:
            QMessageBox.warning(self,"Rango de fechas inválido","La fecha inicial no puede ser posterior " "a la fecha final.")
            return

        # Aún no hay conexión con MySQL.
        # En esta etapa solo preparamos los filtros.
        self.tabla_reportes.setRowCount(0)
        self.actualizar_total()

        QMessageBox.information(
            self,"Reporte preparado","Los filtros son válidos. Cuando conectemos ""MySQL, aquí se cargarán los resultados reales.")

    def actualizar_total(self):
        total = self.tabla_reportes.rowCount()
        self.lbl_total.setText(f"Total de registros: {total}")

        self.btn_exportar.setEnabled(total > 0)

    def exportar_csv(self):
        if self.tabla_reportes.rowCount() == 0:
            QMessageBox.warning(self,"Sin resultados","No hay registros para exportar.")
            return

        ruta, _ = QFileDialog.getSaveFileName(self,"Guardar reporte","reporte.csv","Archivos CSV (*.csv)")

        if not ruta:
            return

        if not ruta.lower().endswith(".csv"):
            ruta += ".csv"

        try:
            with open(ruta,"w",newline="",encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo)

                encabezados = [self.tabla_reportes.horizontalHeaderItem(columna).text() for columna in range( self.tabla_reportes.columnCount())]

                escritor.writerow(encabezados)

                for fila in range(
                    self.tabla_reportes.rowCount()):
                    datos = []

                    for columna in range(self.tabla_reportes.columnCount()):
                        item = self.tabla_reportes.item(fila, columna)

                        datos.append( item.text() if item else "")

                    escritor.writerow(datos)

            QMessageBox.information(self,"Exportación completada","El reporte se exportó correctamente."
            )

        except OSError as error:
            QMessageBox.critical(self,"Error al exportar",f"No se pudo guardar el archivo:\n{error}")

    def limpiar_filtros(self):
        self.cbx_tipo_reporte.setCurrentIndex(0)

        self.date_fecha_inicio.setDate(QDate.currentDate().addMonths(-1) )

        self.date_fecha_fin.setDate(QDate.currentDate())

        self.tabla_reportes.setRowCount(0)
        self.actualizar_total()

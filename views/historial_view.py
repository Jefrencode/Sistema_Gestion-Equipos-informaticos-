
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QMessageBox,
    QAbstractItemView
)

from PySide6.QtCore import Qt

from controllers.historial_controllers import HistorialController


class Historial_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = HistorialController()
        self.registros_historial = []

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_historial()

    # ==============================================
    # CREAR INTERFAZ
    # ==============================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # ENCABEZADO
        titulo = QLabel("Historial del sistema")

        descripcion = QLabel(
            "Consulta los registros existentes "
            "de las actividades del sistema."
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # FILTROS DE BÚSQUEDA
        grupo_filtros = QGroupBox(
            "Filtros de búsqueda"
        )

        layout_filtros = QHBoxLayout(
            grupo_filtros
        )

        self.cbx_tipo_registro = QComboBox()

        self.cbx_tipo_registro.addItems([
            "Todos los registros",
            "Clientes",
            "Equipos",
            "Diagnósticos",
            "Reparaciones",
            "Mantenimientos"
        ])

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por equipo, referencia o descripción..."
        )

        self.btn_limpiar_filtros = QPushButton(
            "Limpiar filtros"
        )

        self.btn_actualizar = QPushButton(
            "Actualizar historial"
        )

        layout_filtros.addWidget(QLabel("Tipo:"))
        layout_filtros.addWidget(
            self.cbx_tipo_registro
        )
        layout_filtros.addWidget(
            self.txt_buscar, 1
        )
        layout_filtros.addWidget(
            self.btn_limpiar_filtros
        )
        layout_filtros.addWidget(
            self.btn_actualizar
        )

        layout_principal.addWidget(
            grupo_filtros
        )

        # TABLA DEL HISTORIAL
        grupo_tabla = QGroupBox(
            "Registros históricos"
        )

        layout_tabla = QVBoxLayout(
            grupo_tabla
        )

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(5)

        self.tabla_historial.setHorizontalHeaderLabels([
            "Fecha",
            "Tipo de registro",
            "Equipo / Referencia",
            "Descripción",
            "Estado"
        ])

        self.tabla_historial.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_historial.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla_historial.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla_historial.setAlternatingRowColors(
            True
        )

        layout_tabla.addWidget(
            self.tabla_historial
        )

        layout_principal.addWidget(
            grupo_tabla
        )

        # CONTADOR
        self.lbl_total_registros = QLabel(
            "Registros encontrados: 0"
        )

        layout_principal.addWidget(
            self.lbl_total_registros
        )

    # ==============================================
    # CONECTAR EVENTOS
    # ==============================================

    def conexiones_botones(self):

        self.txt_buscar.textChanged.connect(
            self.filtrar_historial
        )

        self.cbx_tipo_registro.currentTextChanged.connect(
            self.filtrar_historial
        )

        self.btn_limpiar_filtros.clicked.connect(
            self.limpiar_filtros
        )

        self.btn_actualizar.clicked.connect(
            self.cargar_historial
        )

    # ==============================================
    # CARGAR REGISTROS DESDE MYSQL
    # ==============================================

    def cargar_historial(self):

        try:
            registros = (
                self.controller.listar_historial()
            )

            self.registros_historial = registros
            self.filtrar_historial()

        except RuntimeError as error:

            QMessageBox.critical(
                self,
                "Error de consulta",
                str(error)
            )

    # ==============================================
    # MOSTRAR REGISTROS
    # ==============================================

    def mostrar_historial(self, registros):

        self.tabla_historial.setRowCount(0)

        for registro in registros:

            fila = self.tabla_historial.rowCount()
            self.tabla_historial.insertRow(fila)

            fecha = registro["fecha"]

            if fecha is None:
                fecha_texto = "Sin fecha"
            else:
                fecha_texto = fecha.strftime(
                    "%d/%m/%Y"
                )

            datos = [
                fecha_texto,
                registro["tipo"],
                registro["referencia"],
                registro["descripcion"],
                registro["estado"]
            ]

            for columna, valor in enumerate(datos):

                item = QTableWidgetItem(
                    str(valor)
                )

                # Guardar el ID para futuras consultas.
                if columna == 0:
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        (
                            registro["tipo"],
                            registro["id"]
                        )
                    )

                # Mostrar el texto completo al pasar
                # el cursor, útil para descripciones largas.
                item.setToolTip(str(valor))

                self.tabla_historial.setItem(
                    fila,
                    columna,
                    item
                )

        self.lbl_total_registros.setText(
            f"Registros encontrados: {len(registros)}"
        )

    # ==============================================
    # FILTRAR HISTORIAL
    # ==============================================

    def filtrar_historial(self, *args):

        texto = (
            self.txt_buscar.text()
            .strip()
            .casefold()
        )

        tipo = (
            self.cbx_tipo_registro.currentText()
        )

        resultados = []

        for registro in self.registros_historial:

            coincide_tipo = (
                tipo == "Todos los registros"
                or registro["tipo"] == tipo
            )

            fecha = registro["fecha"]

            fecha_texto = (
                fecha.strftime("%d/%m/%Y")
                if fecha is not None
                else "Sin fecha"
            )

            contenido = " ".join([
                str(registro["id"]),
                fecha_texto,
                registro["tipo"],
                registro["referencia"],
                registro["descripcion"],
                registro["estado"]
            ]).casefold()

            coincide_texto = (
                texto in contenido
            )

            if coincide_tipo and coincide_texto:
                resultados.append(registro)

        self.mostrar_historial(resultados)

    # ==============================================
    # LIMPIAR FILTROS
    # ==============================================

    def limpiar_filtros(self):

        self.txt_buscar.clear()
        self.cbx_tipo_registro.setCurrentIndex(0)
        self.filtrar_historial()


from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QMessageBox,
    QHeaderView, QTableWidget, QTableWidgetItem,
    QGroupBox, QDateEdit, QTextEdit, QLabel,
    QListWidget, QListWidgetItem, QAbstractItemView
)

from PySide6.QtCore import QDate, Qt

from controllers.reparacion_controller import ReparacionesController


class Reparaciones_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = ReparacionesController()

        # ID de la reparación seleccionada para editar.
        self.id_reparacion_seleccionada = None

        # Componentes seleccionados para la reparación.
        self.componentes_seleccionados = []

        # Registros cargados desde MySQL.
        self.reparaciones = []

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_datos_iniciales()

    # ======================================================
    # 1. CREAR INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # --------------------------------------------------
        # FORMULARIO
        # --------------------------------------------------

        grupo_formulario = QGroupBox("Datos de la reparación")
        layout_formulario = QVBoxLayout(grupo_formulario)

        formulario = QFormLayout()
        formulario.setSpacing(15)

        # Equipo relacionado.
        self.cbx_equipo = QComboBox()
        formulario.addRow("Equipo:", self.cbx_equipo)

        # Diagnóstico relacionado.
        self.cbx_diagnostico = QComboBox()
        formulario.addRow("Diagnóstico:", self.cbx_diagnostico)

        # Fecha.
        self.date_fecha_reparacion = QDateEdit()
        self.date_fecha_reparacion.setDate(QDate.currentDate())
        self.date_fecha_reparacion.setCalendarPopup(True)
        self.date_fecha_reparacion.setDisplayFormat("dd/MM/yyyy")

        formulario.addRow(
            "Fecha de reparación:",
            self.date_fecha_reparacion
        )

        # Trabajo realizado.
        self.txt_trabajo_realizado = QTextEdit()
        self.txt_trabajo_realizado.setPlaceholderText(
            "Describe el trabajo realizado..."
        )
        self.txt_trabajo_realizado.setMaximumHeight(110)

        formulario.addRow(
            "Trabajo realizado:",
            self.txt_trabajo_realizado
        )

        # --------------------------------------------------
        # COMPONENTES UTILIZADOS
        # --------------------------------------------------

        self.cbx_componente = QComboBox()
        formulario.addRow(
            "Componente:",
            self.cbx_componente
        )

        self.btn_agregar_componente = QPushButton(
            "Agregar componente"
        )

        formulario.addRow(
            "",
            self.btn_agregar_componente
        )

        # Lista de componentes asociados.
        self.lista_componentes = QListWidget()
        self.lista_componentes.setMaximumHeight(110)

        formulario.addRow(
            "Repuestos utilizados:",
            self.lista_componentes
        )

        self.btn_quitar_componente = QPushButton(
            "Quitar componente"
        )

        formulario.addRow(
            "",
            self.btn_quitar_componente
        )

        # Costo.
        self.txt_costo = QLineEdit()
        self.txt_costo.setPlaceholderText("Ej. 500.00")

        formulario.addRow(
            "Costo (C$):",
            self.txt_costo
        )

        # Estado.
        self.cbx_estado_reparacion = QComboBox()

        formulario.addRow(
            "Estado de reparación:",
            self.cbx_estado_reparacion
        )

        layout_formulario.addLayout(formulario)

        # --------------------------------------------------
        # BOTONES CRUD
        # --------------------------------------------------

        self.btn_guardar = QPushButton("Guardar reparación")
        self.btn_editar = QPushButton("Editar reparación")
        self.btn_eliminar = QPushButton("Eliminar reparación")
        self.btn_limpiar = QPushButton("Limpiar")

        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        layout_formulario.addWidget(self.btn_guardar)
        layout_formulario.addWidget(self.btn_editar)
        layout_formulario.addWidget(self.btn_eliminar)
        layout_formulario.addWidget(self.btn_limpiar)

        layout_formulario.addStretch()

        # --------------------------------------------------
        # TABLA DE REPARACIONES
        # --------------------------------------------------

        grupo_tabla = QGroupBox("Registro de reparaciones")
        layout_tabla = QVBoxLayout(grupo_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar por equipo, diagnóstico, trabajo, "
            "componente o estado..."
        )

        layout_tabla.addWidget(self.txt_buscar)

        self.tabla_reparaciones = QTableWidget()
        self.tabla_reparaciones.setColumnCount(7)

        self.tabla_reparaciones.setHorizontalHeaderLabels([
            "Equipo",
            "Diagnóstico",
            "Fecha",
            "Trabajo realizado",
            "Repuestos",
            "Costo (C$)",
            "Estado"
        ])

        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_reparaciones.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla_reparaciones.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla_reparaciones.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        layout_tabla.addWidget(self.tabla_reparaciones)

        # Distribución original: formulario y tabla.
        layout_principal.addWidget(grupo_formulario, 1)
        layout_principal.addWidget(grupo_tabla, 2)

    # ======================================================
    # 2. CONECTAR EVENTOS
    # ======================================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_reparacion
        )

        self.btn_editar.clicked.connect(
            self.editar_reparacion
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_reparacion
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.btn_agregar_componente.clicked.connect(
            self.agregar_componente
        )

        self.btn_quitar_componente.clicked.connect(
            self.quitar_componente
        )

        # Actualizar diagnósticos al cambiar de equipo.
        self.cbx_equipo.currentIndexChanged.connect(
            self.cargar_diagnosticos
        )

        # Seleccionar reparación para editar.
        self.tabla_reparaciones.itemSelectionChanged.connect(
            self.seleccionar_reparacion
        )

        # Buscar registros.
        self.txt_buscar.textChanged.connect(
            self.filtrar_reparaciones
        )

    # ======================================================
    # 3. CARGAR DATOS INICIALES
    # ======================================================

    def cargar_datos_iniciales(self):

        try:
            self.cargar_equipos()
            self.cargar_estados()
            self.cargar_componentes()
            self.cargar_reparaciones()

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error de carga",
                str(error)
            )

    # ======================================================
    # 4. CARGAR EQUIPOS
    # ======================================================

    def cargar_equipos(self):

        equipos = self.controller.listar_equipos()

        self.cbx_equipo.blockSignals(True)
        self.cbx_equipo.clear()

        self.cbx_equipo.addItem(
            "Seleccione un equipo",
            None
        )

        for equipo in equipos:
            self.cbx_equipo.addItem(
                equipo["descripcion"],
                equipo["id_equipo"]
            )

        self.cbx_equipo.blockSignals(False)

        self.cargar_diagnosticos()

    # ======================================================
    # 5. CARGAR DIAGNÓSTICOS DEL EQUIPO
    # ======================================================

    def cargar_diagnosticos(self, *args):

        id_equipo = self.cbx_equipo.currentData()

        self.cbx_diagnostico.clear()
        self.cbx_diagnostico.addItem(
            "Sin diagnóstico",
            None
        )

        if id_equipo is None:
            return

        try:
            diagnosticos = (
                self.controller.listar_diagnosticos(
                    id_equipo
                )
            )

            for diagnostico in diagnosticos:
                self.cbx_diagnostico.addItem(
                    diagnostico["descripcion"],
                    diagnostico["id_diagnostico"]
                )

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "Error",
                str(error)
            )

    # ======================================================
    # 6. CARGAR ESTADOS
    # ======================================================

    def cargar_estados(self):

        estados = self.controller.listar_estados()

        self.cbx_estado_reparacion.clear()
        self.cbx_estado_reparacion.addItem(
            "Seleccione un estado",
            None
        )

        for estado in estados:
            self.cbx_estado_reparacion.addItem(
                estado["nombre"],
                estado["id_estado"]
            )

    # ======================================================
    # 7. CARGAR COMPONENTES
    # ======================================================

    def cargar_componentes(self):

        componentes = self.controller.listar_componentes()

        self.cbx_componente.clear()
        self.cbx_componente.addItem(
            "Seleccione un componente",
            None
        )

        for componente in componentes:

            descripcion = (
                f"#{componente['id_componente']} - "
                f"{componente['nombre']} "
                f"{componente['marca'] or ''} "
                f"{componente['modelo'] or ''}"
            ).strip()

            self.cbx_componente.addItem(
                descripcion,
                componente["id_componente"]
            )

    # ======================================================
    # 8. AGREGAR COMPONENTE A LA LISTA
    # ======================================================

    def agregar_componente(self):

        id_componente = self.cbx_componente.currentData()

        if id_componente is None:
            QMessageBox.warning(
                self,
                "Componente requerido",
                "Seleccione un componente."
            )
            return

        if id_componente in self.componentes_seleccionados:
            QMessageBox.warning(
                self,
                "Componente repetido",
                "Este componente ya fue agregado."
            )
            return

        self.componentes_seleccionados.append(
            id_componente
        )

        item = QListWidgetItem(
            self.cbx_componente.currentText()
        )

        item.setData(
            Qt.ItemDataRole.UserRole,
            id_componente
        )

        self.lista_componentes.addItem(item)

        self.cbx_componente.setCurrentIndex(0)

    # ======================================================
    # 9. QUITAR COMPONENTE
    # ======================================================

    def quitar_componente(self):

        fila = self.lista_componentes.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un componente de la lista."
            )
            return

        item = self.lista_componentes.takeItem(fila)

        id_componente = item.data(
            Qt.ItemDataRole.UserRole
        )

        if id_componente in self.componentes_seleccionados:
            self.componentes_seleccionados.remove(
                id_componente
            )

    # ======================================================
    # 10. OBTENER DATOS DEL FORMULARIO
    # ======================================================

    def obtener_datos_formulario(self):

        return {
            "id_equipo": self.cbx_equipo.currentData(),

            "id_diagnostico": (
                self.cbx_diagnostico.currentData()
            ),

            "fecha": (
                self.date_fecha_reparacion.date().toPython()
            ),

            "trabajo_realizado": (
                self.txt_trabajo_realizado
                .toPlainText()
                .strip()
            ),

            "costo": self.txt_costo.text().strip(),

            "id_estado": (
                self.cbx_estado_reparacion.currentData()
            )
        }

    # ======================================================
    # 11. GUARDAR REPARACIÓN
    # ======================================================

    def guardar_reparacion(self):

        datos = self.obtener_datos_formulario()

        try:
            id_reparacion = (
                self.controller.registrar_reparacion(
                    datos,
                    self.componentes_seleccionados
                )
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"Reparación #{id_reparacion} registrada "
                "correctamente."
            )

            self.limpiar_formulario()
            self.cargar_reparaciones()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error)
            )

    # ======================================================
    # 12. CARGAR REPARACIONES DESDE MYSQL
    # ======================================================

    def cargar_reparaciones(self):

        try:
            self.reparaciones = (
                self.controller.listar_reparaciones()
            )

            self.filtrar_reparaciones(
                self.txt_buscar.text()
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error",
                str(error)
            )

    # ======================================================
    # 13. MOSTRAR REPARACIONES EN LA TABLA
    # ======================================================

    def mostrar_reparaciones(self, reparaciones):

        self.tabla_reparaciones.blockSignals(True)

        try:
            self.tabla_reparaciones.setRowCount(0)

            for reparacion in reparaciones:

                fila = self.tabla_reparaciones.rowCount()
                self.tabla_reparaciones.insertRow(fila)

                datos = [
                    reparacion["nombre_equipo"],
                    reparacion["nombre_diagnostico"],
                    reparacion["fecha"].strftime(
                        "%d/%m/%Y"
                    ),
                    reparacion["trabajo_realizado"],
                    reparacion["componentes"],
                    f"{reparacion['costo']:.2f}",
                    reparacion["nombre_estado"]
                ]

                for columna, valor in enumerate(datos):

                    item = QTableWidgetItem(str(valor))

                    if columna == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            reparacion["id_reparacion"]
                        )

                    self.tabla_reparaciones.setItem(
                        fila,
                        columna,
                        item
                    )

        finally:
            self.tabla_reparaciones.blockSignals(False)

    # ======================================================
    # 14. BUSCAR REPARACIONES
    # ======================================================

    def filtrar_reparaciones(self, texto):

        texto = texto.strip().lower()

        resultados = []

        for reparacion in self.reparaciones:

            contenido = " ".join([
                str(reparacion["id_reparacion"]),
                reparacion["nombre_equipo"],
                reparacion["nombre_diagnostico"],
                reparacion["trabajo_realizado"],
                reparacion["componentes"],
                reparacion["nombre_estado"],
                reparacion["fecha"].strftime("%d/%m/%Y")
            ]).lower()

            if texto in contenido:
                resultados.append(reparacion)

        self.mostrar_reparaciones(resultados)

    # ======================================================
    # 15. SELECCIONAR REPARACIÓN
    # ======================================================

    def seleccionar_reparacion(self):

        fila = self.tabla_reparaciones.currentRow()

        if fila < 0:
            return

        item = self.tabla_reparaciones.item(fila, 0)

        if item is None:
            return

        id_reparacion = item.data(
            Qt.ItemDataRole.UserRole
        )

        reparacion = next(
            (
                r for r in self.reparaciones
                if r["id_reparacion"] == id_reparacion
            ),
            None
        )

        if reparacion is None:
            return

        self.id_reparacion_seleccionada = id_reparacion

        # Seleccionar equipo.
        indice_equipo = self.cbx_equipo.findData(
            reparacion["id_equipo"]
        )

        self.cbx_equipo.setCurrentIndex(indice_equipo)

        # Seleccionar diagnóstico del equipo.
        indice_diagnostico = (
            self.cbx_diagnostico.findData(
                reparacion["id_diagnostico"]
            )
        )

        self.cbx_diagnostico.setCurrentIndex(
            indice_diagnostico
            if indice_diagnostico >= 0 else 0
        )

        # Fecha.
        fecha = reparacion["fecha"]

        self.date_fecha_reparacion.setDate(
            QDate(
                fecha.year,
                fecha.month,
                fecha.day
            )
        )

        # Trabajo y costo.
        self.txt_trabajo_realizado.setPlainText(
            reparacion["trabajo_realizado"]
        )

        self.txt_costo.setText(
            f"{reparacion['costo']:.2f}"
        )

        # Estado.
        indice_estado = (
            self.cbx_estado_reparacion.findData(
                reparacion["id_estado"]
            )
        )

        self.cbx_estado_reparacion.setCurrentIndex(
            indice_estado
        )

        # Cargar componentes asociados.
        self.lista_componentes.clear()
        self.componentes_seleccionados.clear()

        for id_componente in reparacion["ids_componentes"]:

            indice = self.cbx_componente.findData(
                id_componente
            )

            if indice < 0:
                continue

            item = QListWidgetItem(
                self.cbx_componente.itemText(indice)
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                id_componente
            )

            self.lista_componentes.addItem(item)

            self.componentes_seleccionados.append(
                id_componente
            )

        # Habilitar edición y eliminación.
        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    # ======================================================
    # 16. EDITAR REPARACIÓN
    # ======================================================

    def editar_reparacion(self):

        if self.id_reparacion_seleccionada is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione una reparación para editar."
            )
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_reparacion(
                self.id_reparacion_seleccionada,
                datos,
                self.componentes_seleccionados
            )

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "La reparación fue actualizada correctamente."
            )

            self.limpiar_formulario()
            self.cargar_reparaciones()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

    # ======================================================
    # 17. ELIMINAR REPARACIÓN
    # ======================================================

    def eliminar_reparacion(self):

        if self.id_reparacion_seleccionada is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione una reparación para eliminar."
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar esta reparación?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.controller.eliminar_reparacion(
                self.id_reparacion_seleccionada
            )

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "La reparación fue eliminada correctamente."
            )

            self.limpiar_formulario()
            self.cargar_reparaciones()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                str(error)
            )

    # ======================================================
    # 18. LIMPIAR FORMULARIO
    # ======================================================

    def limpiar_formulario(self):

        self.id_reparacion_seleccionada = None

        self.cbx_equipo.setCurrentIndex(0)
        self.cbx_diagnostico.setCurrentIndex(0)

        self.date_fecha_reparacion.setDate(
            QDate.currentDate()
        )

        self.txt_trabajo_realizado.clear()
        self.txt_costo.clear()

        self.cbx_estado_reparacion.setCurrentIndex(0)
        self.cbx_componente.setCurrentIndex(0)

        self.lista_componentes.clear()
        self.componentes_seleccionados.clear()

        self.tabla_reparaciones.clearSelection()

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.txt_trabajo_realizado.setFocus()

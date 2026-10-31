
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QMessageBox,
    QHeaderView, QTableWidget, QTableWidgetItem,
    QGroupBox, QTextEdit, QAbstractItemView
)

from PySide6.QtCore import Qt

from controllers.componentes_controller import ComponentesController


class Componentes_Equipos(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = ComponentesController()

        self.id_componente_seleccionado = None
        self.componentes = []

        self.crear_interfaz()
        self.conexiones_botones()
        self.cargar_componentes()

    # ==================================================
    # 1. CREAR INTERFAZ
    # ==================================================

    def crear_interfaz(self):

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # FORMULARIO
        grupo_formulario = QGroupBox(
            "DATOS DEL COMPONENTE"
        )

        layout_formulario = QVBoxLayout(
            grupo_formulario
        )

        formulario = QFormLayout()
        formulario.setSpacing(10)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(120)

        self.cbx_categoria = QComboBox()
        self.cbx_categoria.addItems([
            "Almacenamiento",
            "Memoria RAM",
            "Procesador",
            "Fuente de alimentación",
            "Tarjeta gráfica",
            "Placa base",
            "Otro"
        ])

        self.txt_marca = QLineEdit()
        self.txt_marca.setMaxLength(80)

        self.txt_modelo = QLineEdit()
        self.txt_modelo.setMaxLength(100)

        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setPlaceholderText(
            "Ejemplo: 5"
        )

        self.txt_costo = QLineEdit()
        self.txt_costo.setPlaceholderText(
            "Ejemplo: 650.00"
        )

        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setPlaceholderText(
            "Descripción del componente (opcional)"
        )
        self.txt_descripcion.setMaximumHeight(90)

        formulario.addRow(
            "Nombre:", self.txt_nombre
        )

        formulario.addRow(
            "Categoría:", self.cbx_categoria
        )

        formulario.addRow(
            "Marca:", self.txt_marca
        )

        formulario.addRow(
            "Modelo:", self.txt_modelo
        )

        formulario.addRow(
            "Descripción:", self.txt_descripcion
        )

        formulario.addRow(
            "Cantidad:", self.txt_cantidad
        )

        formulario.addRow(
            "Costo (C$):", self.txt_costo
        )

        # BOTONES CRUD
        self.btn_guardar = QPushButton(
            "Guardar componente"
        )

        self.btn_editar = QPushButton(
            "Editar componente"
        )

        self.btn_eliminar = QPushButton(
            "Eliminar componente"
        )

        self.btn_limpiar = QPushButton("Limpiar")

        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        botones = QVBoxLayout()

        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_editar)
        botones.addWidget(self.btn_eliminar)
        botones.addWidget(self.btn_limpiar)

        layout_formulario.addLayout(formulario)
        layout_formulario.addLayout(botones)
        layout_formulario.addStretch()

        # TABLA
        grupo_tabla = QGroupBox(
            "LISTADO DE COMPONENTES"
        )

        layout_tabla = QVBoxLayout(grupo_tabla)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar componente por nombre, "
            "categoría, marca o modelo..."
        )

        self.tabla_componentes = QTableWidget()
        self.tabla_componentes.setColumnCount(7)

        self.tabla_componentes.setHorizontalHeaderLabels([
            "Nombre",
            "Categoría",
            "Marca",
            "Modelo",
            "Descripción",
            "Cantidad",
            "Costo (C$)"
        ])

        self.tabla_componentes.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabla_componentes.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabla_componentes.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla_componentes.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        layout_tabla.addWidget(self.txt_buscar)
        layout_tabla.addWidget(self.tabla_componentes)

        layout_principal.addWidget(
            grupo_formulario, 1
        )

        layout_principal.addWidget(
            grupo_tabla, 2
        )

    # ==================================================
    # 2. CONEXIONES
    # ==================================================

    def conexiones_botones(self):

        self.btn_guardar.clicked.connect(
            self.guardar_componente
        )

        self.btn_editar.clicked.connect(
            self.editar_componente
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_componente
        )

        self.btn_limpiar.clicked.connect(
            self.limpiar_formulario
        )

        self.txt_buscar.textChanged.connect(
            self.filtrar_componentes
        )

        self.tabla_componentes.itemSelectionChanged.connect(
            self.seleccionar_componente
        )

    # ==================================================
    # 3. OBTENER DATOS DEL FORMULARIO
    # ==================================================

    def obtener_datos_formulario(self):

        return {
            "nombre": self.txt_nombre.text().strip(),

            "categoria": (
                self.cbx_categoria.currentText()
            ),

            "marca": self.txt_marca.text().strip(),

            "modelo": self.txt_modelo.text().strip(),

            "descripcion": (
                self.txt_descripcion
                .toPlainText()
                .strip()
            ),

            "cantidad": self.txt_cantidad.text().strip(),

            "costo": self.txt_costo.text().strip()
        }

    # ==================================================
    # 4. GUARDAR COMPONENTE
    # ==================================================

    def guardar_componente(self):

        datos = self.obtener_datos_formulario()

        try:
            id_componente = (
                self.controller.registrar_componente(
                    datos
                )
            )

            QMessageBox.information(
                self,
                "Registro exitoso",
                f"Componente #{id_componente} "
                "registrado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_componentes()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error)
            )

    # ==================================================
    # 5. CARGAR COMPONENTES DESDE MYSQL
    # ==================================================

    def cargar_componentes(self):

        try:
            self.componentes = (
                self.controller.listar_componentes()
            )

            self.filtrar_componentes(
                self.txt_buscar.text()
            )

        except (ValueError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "Error de carga",
                str(error)
            )

    # ==================================================
    # 6. MOSTRAR COMPONENTES EN TABLA
    # ==================================================

    def mostrar_componentes(self, componentes):

        self.tabla_componentes.blockSignals(True)

        try:
            self.tabla_componentes.setRowCount(0)

            for componente in componentes:

                fila = self.tabla_componentes.rowCount()
                self.tabla_componentes.insertRow(fila)

                datos = [
                    componente["nombre"],
                    componente["categoria"] or "",
                    componente["marca"] or "",
                    componente["modelo"] or "",
                    componente["descripcion"] or "",
                    str(componente["cantidad"]),
                    f"{componente['costo']:.2f}"
                ]

                for columna, valor in enumerate(datos):

                    item = QTableWidgetItem(str(valor))

                    if columna == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            componente["id_componente"]
                        )

                    self.tabla_componentes.setItem(
                        fila,
                        columna,
                        item
                    )

        finally:
            self.tabla_componentes.blockSignals(False)

    # ==================================================
    # 7. FILTRAR COMPONENTES
    # ==================================================

    def filtrar_componentes(self, texto):

        texto = texto.strip().lower()

        resultados = []

        for componente in self.componentes:

            contenido = " ".join([
                componente["nombre"],
                componente["categoria"] or "",
                componente["marca"] or "",
                componente["modelo"] or "",
                componente["descripcion"] or ""
            ]).lower()

            if texto in contenido:
                resultados.append(componente)

        self.mostrar_componentes(resultados)

    # ==================================================
    # 8. SELECCIONAR COMPONENTE
    # ==================================================

    def seleccionar_componente(self):

        fila = self.tabla_componentes.currentRow()

        if fila < 0:
            return

        item = self.tabla_componentes.item(fila, 0)

        if item is None:
            return

        id_componente = item.data(
            Qt.ItemDataRole.UserRole
        )

        componente = next(
            (
                c for c in self.componentes
                if c["id_componente"] == id_componente
            ),
            None
        )

        if componente is None:
            return

        self.id_componente_seleccionado = id_componente

        self.txt_nombre.setText(
            componente["nombre"]
        )

        categoria = componente["categoria"] or ""

        indice = self.cbx_categoria.findText(
            categoria
        )

        if indice >= 0:
            self.cbx_categoria.setCurrentIndex(indice)
        else:
            self.cbx_categoria.setCurrentIndex(6)

        self.txt_marca.setText(
            componente["marca"] or ""
        )

        self.txt_modelo.setText(
            componente["modelo"] or ""
        )

        self.txt_descripcion.setPlainText(
            componente["descripcion"] or ""
        )

        self.txt_cantidad.setText(
            str(componente["cantidad"])
        )

        self.txt_costo.setText(
            f"{componente['costo']:.2f}"
        )

        self.btn_guardar.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    # ==================================================
    # 9. EDITAR COMPONENTE
    # ==================================================

    def editar_componente(self):

        if self.id_componente_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un componente para editar."
            )
            return

        datos = self.obtener_datos_formulario()

        try:
            self.controller.actualizar_componente(
                self.id_componente_seleccionado,
                datos
            )

            QMessageBox.information(
                self,
                "Actualización exitosa",
                "El componente fue actualizado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_componentes()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

    # ==================================================
    # 10. ELIMINAR COMPONENTE
    # ==================================================

    def eliminar_componente(self):

        if self.id_componente_seleccionado is None:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Seleccione un componente para eliminar."
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar este componente?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.controller.eliminar_componente(
                self.id_componente_seleccionado
            )

            QMessageBox.information(
                self,
                "Eliminación exitosa",
                "El componente fue eliminado correctamente."
            )

            self.limpiar_formulario()
            self.cargar_componentes()

        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                str(error)
            )

    # ==================================================
    # 11. LIMPIAR FORMULARIO
    # ==================================================

    def limpiar_formulario(self):

        self.id_componente_seleccionado = None

        self.txt_nombre.clear()
        self.cbx_categoria.setCurrentIndex(0)

        self.txt_marca.clear()
        self.txt_modelo.clear()
        self.txt_descripcion.clear()

        self.txt_cantidad.clear()
        self.txt_costo.clear()

        self.tabla_componentes.clearSelection()

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        self.txt_nombre.setFocus()

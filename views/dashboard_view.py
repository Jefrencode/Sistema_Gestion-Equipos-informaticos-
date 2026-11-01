from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QSizePolicy
)

from PySide6.QtCore import Qt

from controllers.dashboard_controller import DashboardController


class DashboardView(QWidget):

    def __init__(self):
        super().__init__()

        # Controlador
        self.controller = DashboardController()

        self.resize(1500, 1000)

        # Construir interfaz y conectar eventos
        self.crear_interfaz()
        self.conexiones_botones()

        # Cargar información desde MySQL
        self.actualizar_dashboard()

    # ==========================================
    # CREAR INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        self.setObjectName("dashboardView")

        # ======================================
        # ENCABEZADO
        # ======================================

        self.lbl_titulo = QLabel("Panel principal")
        self.lbl_titulo.setObjectName("dashboardTitle")

        self.lbl_subtitulo = QLabel(
            "Resumen general de la gestión de equipos informáticos")
        self.lbl_subtitulo.setObjectName("dashboardSubtitle")
        self.lbl_subtitulo.setWordWrap(True)

        self.btn_actualizar = QPushButton("Actualizar datos")
        self.btn_actualizar.setObjectName("btnActualizarDashboard")
        self.btn_actualizar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout_textos = QVBoxLayout()
        layout_textos.setSpacing(5)

        layout_textos.addWidget(self.lbl_titulo)
        layout_textos.addWidget(self.lbl_subtitulo)

        layout_encabezado = QHBoxLayout()
        layout_encabezado.addLayout(layout_textos)
        layout_encabezado.addStretch()
        layout_encabezado.addWidget(self.btn_actualizar)

        # ======================================
        # TARJETAS ESTADÍSTICAS
        # ======================================

        self.card_equipos, self.lbl_total_equipos = (
            self.crear_tarjeta("Equipos registrados")
        )

        self.card_pendientes, self.lbl_diagnosticos_pendientes = (
            self.crear_tarjeta("Diagnósticos registrados")
        )

        self.card_reparacion, self.lbl_reparaciones_proceso = (
            self.crear_tarjeta("Reparaciones en proceso")
        )

        self.card_mantenimiento, self.lbl_mantenimientos_pendientes = (
            self.crear_tarjeta("Mantenimientos pendientes")
        )

        # Distribución de tarjetas
        self.grid_tarjetas = QGridLayout()
        self.grid_tarjetas.setSpacing(15)

        self.grid_tarjetas.addWidget(
            self.card_equipos, 0, 0
        )

        self.grid_tarjetas.addWidget(
            self.card_pendientes, 0, 1
        )

        self.grid_tarjetas.addWidget(
            self.card_reparacion, 0, 2
        )

        self.grid_tarjetas.addWidget(
            self.card_mantenimiento, 0, 3
        )

        for columna in range(4):
            self.grid_tarjetas.setColumnStretch(
                columna, 1
            )

        # ======================================
        # EQUIPOS RECIENTES
        # ======================================

        self.frame_recientes = QFrame()
        self.frame_recientes.setObjectName("recentCard")

        self.layout_recientes = QVBoxLayout(
            self.frame_recientes
        )
        self.layout_recientes.setSpacing(12)

        self.lbl_recientes = QLabel(
            "Últimos equipos registrados"
        )
        self.lbl_recientes.setObjectName("sectionTitle")

        self.layout_recientes.addWidget(
            self.lbl_recientes
        )

        # Contenedor independiente para registros
        self.contenedor_equipos = QWidget()

        self.layout_equipos = QVBoxLayout(
            self.contenedor_equipos
        )

        self.layout_equipos.setContentsMargins(
            0, 0, 0, 0
        )

        self.layout_equipos.setSpacing(8)

        self.layout_recientes.addWidget(
            self.contenedor_equipos
        )

        # ======================================
        # MENSAJE DE ESTADO
        # ======================================

        self.lbl_estado = QLabel(
            "Cargando información..."
        )

        self.lbl_estado.setObjectName(
            "dashboardStatus"
        )

        # ======================================
        # LAYOUT PRINCIPAL
        # ======================================

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            30, 30, 30, 30
        )

        layout_principal.setSpacing(20)

        layout_principal.addLayout(
            layout_encabezado
        )

        layout_principal.addSpacing(15)

        layout_principal.addLayout(
            self.grid_tarjetas
        )

        layout_principal.addSpacing(15)

        layout_principal.addWidget(
            self.frame_recientes
        )

        layout_principal.addWidget(
            self.lbl_estado
        )

        layout_principal.addStretch()

    # ==========================================
    # CREAR TARJETA ESTADÍSTICA
    # ==========================================

    def crear_tarjeta(self, titulo):

        tarjeta = QFrame()
        tarjeta.setObjectName("dashboardCard")

        tarjeta.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        layout = QVBoxLayout(tarjeta)

        layout.setContentsMargins(
            20, 20, 20, 20
        )

        layout.setSpacing(12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitle")
        lbl_titulo.setWordWrap(True)

        lbl_valor = QLabel("0")
        lbl_valor.setObjectName("cardValue")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addStretch()

        return tarjeta, lbl_valor

    # ==========================================
    # CONECTAR BOTONES
    # ==========================================

    def conexiones_botones(self):

        self.btn_actualizar.clicked.connect(
            self.actualizar_dashboard
        )

    # ==========================================
    # MOSTRAR ESTADÍSTICAS
    # ==========================================

    def mostrar_estadisticas(self, datos):

        # Total de equipos
        self.lbl_total_equipos.setText(
            str(datos["total_equipos"])
        )

        # Total de diagnósticos
        self.lbl_diagnosticos_pendientes.setText(
            str(datos["total_diagnosticos"])
        )

        # Reparaciones en proceso
        self.lbl_reparaciones_proceso.setText(
            str(datos["reparaciones_proceso"])
        )

        # Mantenimientos pendientes
        self.lbl_mantenimientos_pendientes.setText(
            str(datos["mantenimientos_pendientes"])
        )

    # ==========================================
    # MOSTRAR EQUIPOS RECIENTES
    # ==========================================

    def mostrar_equipos_recientes(self, equipos):

        # Limpiar registros anteriores
        while self.layout_equipos.count():

            item = self.layout_equipos.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # Sin equipos registrados
        if not equipos:

            lbl_vacio = QLabel(
                "No hay equipos registrados recientemente."
            )

            lbl_vacio.setObjectName("recentItem")

            self.layout_equipos.addWidget(
                lbl_vacio
            )

            return

        # Mostrar equipos de MySQL
        for equipo in equipos:

            codigo = equipo.get(
                "codigo", "Sin código"
            )

            tipo = equipo.get(
                "tipo", "Sin tipo"
            )

            marca = equipo.get(
                "marca", "Sin marca"
            )

            modelo = equipo.get(
                "modelo", ""
            )

            estado = equipo.get(
                "estado", "Sin estado"
            )

            # Información del equipo
            descripcion = (
                f"{codigo}  |  "
                f"{tipo} {marca} {modelo}  |  "
                f"Estado de recepción: {estado}"
            )

            lbl_equipo = QLabel(
                descripcion
            )

            lbl_equipo.setObjectName(
                "recentItem"
            )

            lbl_equipo.setWordWrap(True)

            self.layout_equipos.addWidget(
                lbl_equipo
            )

    # ==========================================
    # ACTUALIZAR DASHBOARD
    # ==========================================

    def actualizar_dashboard(self):

        self.btn_actualizar.setEnabled(False)

        self.lbl_estado.setText(
            "Consultando información de MySQL..."
        )

        try:

            # Consultar estadísticas
            estadisticas = (
                self.controller.obtener_estadisticas()
            )

            # Consultar equipos recientes
            equipos_recientes = (
                self.controller.obtener_equipos_recientes(
                    limite=5
                )
            )

            # Actualizar tarjetas
            self.mostrar_estadisticas(
                estadisticas
            )

            # Actualizar lista de equipos
            self.mostrar_equipos_recientes(
                equipos_recientes
            )

            self.lbl_estado.setText(
                "Información actualizada correctamente."
            )

        except Exception as error:

            self.lbl_estado.setText(
                "No se pudieron actualizar los datos."
            )

            QMessageBox.critical(
                self,
                "Error del Dashboard",
                "Ocurrió un error al consultar MySQL.\n\n"
                f"Detalle: {error}"
            )

        finally:

            self.btn_actualizar.setEnabled(True)

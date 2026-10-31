from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout
)


class DashboardView(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(1500,1000)

        self.crear_interfaz()

    def crear_interfaz(self):

        self.setObjectName("dashboardView")

        # TÍTULO

        self.lbl_titulo = QLabel("Panel principal")

        self.lbl_titulo.setObjectName("dashboardTitle")

        self.lbl_subtitulo = QLabel("Resumen de la gestión de equipos")

        self.lbl_subtitulo.setObjectName("dashboardSubtitle")

        # TARJETAS

        self.card_equipos = self.crear_tarjeta("Equipos registrados","24")

        self.card_pendientes = self.crear_tarjeta("Diagnosticos Pendientes", "8")

        self.card_reparacion = self.crear_tarjeta(" Reparacion en reparación","5")

        self.card_mantenimiento = self.crear_tarjeta("Mantenimiento Proximos","3")

        # GRID DE TARJETAS

        grid_tarjetas = QGridLayout()

        grid_tarjetas.addWidget(self.card_equipos, 0, 0)

        grid_tarjetas.addWidget(self.card_pendientes,0, 1)

        grid_tarjetas.addWidget(self.card_reparacion,0, 2
        )

        grid_tarjetas.addWidget(self.card_mantenimiento,0, 3)

        # SECCIÓN EQUIPOS RECIENTES


        self.frame_recientes = QFrame()

        self.frame_recientes.setObjectName("recentCard")

        layout_recientes = QVBoxLayout()

        self.lbl_recientes = QLabel("Equipos recientes")

        self.lbl_recientes.setObjectName("sectionTitle")

        layout_recientes.addWidget(self.lbl_recientes)

        # Ejemplo temporal
        equipo1 = QLabel("PC-001        En reparación")

        equipo2 = QLabel("LAP-002       Diagnóstico")

        equipo3 = QLabel("PC-003       Mantenimiento")

        equipo1.setObjectName("recentItem")
        equipo2.setObjectName("recentItem")
        equipo3.setObjectName("recentItem")

        layout_recientes.addWidget(equipo1)
        layout_recientes.addWidget(equipo2)
        layout_recientes.addWidget(equipo3)

        self.frame_recientes.setLayout(layout_recientes)

        # LAYOUT PRINCIPAL

        layout_principal = QVBoxLayout()

        layout_principal.setContentsMargins(30, 30, 30, 30
        )

        layout_principal.addWidget(self.lbl_titulo)

        layout_principal.addWidget(self.lbl_subtitulo)

        layout_principal.addSpacing(25)

        layout_principal.addLayout(grid_tarjetas)

        layout_principal.addSpacing(25)

        layout_principal.addWidget(
            self.frame_recientes
        )

        layout_principal.addStretch()

        self.setLayout(layout_principal)

    # CREAR TARJETA
    def crear_tarjeta(self, titulo, valor):

        tarjeta = QFrame()

        tarjeta.setObjectName("dashboardCard")

        layout = QVBoxLayout()

        lbl_titulo = QLabel(titulo)

        lbl_titulo.setObjectName("cardTitle")

        lbl_valor = QLabel(valor)

        lbl_valor.setObjectName("cardValue")

        layout.addWidget(lbl_titulo)

        layout.addWidget(lbl_valor)

        tarjeta.setLayout(layout)

        return tarjeta
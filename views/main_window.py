from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget
)
from PySide6.QtCore import Qt

# Importando modulos a la ventana Principal.

from views.dashboard_view import DashboardView
from views.clientes_view import Clientes
from views.equipo_view import Equipos
from views.diagnostico_view import Diagnostico_Equipos
from views.reparaciones_view import Reparaciones_Equipos
from views.historial_view import Historial_Equipos
from views.mantenimiento_view import Mantenimientos_Equipos
from views.componentes_view import Componentes_Equipos
from views.estados_view import Estados_Equipos
from views.reportes_view import Reportes_Equipos
from views.configuraciones_view import Configuraciones_sistema
from views.usuario_view import Usuarios

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Diagnóstico y Control de Equipos Informáticos")
        self.setMinimumSize(1500, 1000)
        # Estado del menú (True: Expandido, False: Colapsado)
        self.menu_expandido = True
        self.crear_interfaz()
        self.conectar_eventos()

    def crear_interfaz(self):

        contenedor = QWidget()

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # Menú lateral asignado a la instancia
        self.menu_lateral = self.crear_menu()

        # Contenedor del área derecha (Barra Superior  StackedWidget)
        layout_derecho = QVBoxLayout()
        layout_derecho.setContentsMargins(0, 0, 0, 0)
        layout_derecho.setSpacing(0)

        # Barra superior para el botón de toggle (identificada para QSS)
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(50)

        layout_top = QHBoxLayout(top_bar)
        layout_top.setContentsMargins(10, 0, 15, 0)

        # Botón para encoger/expandir el menú
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setObjectName("btnToggleMenu")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)

        layout_top.addWidget(self.btn_toggle)
        layout_top.addStretch()

        # Área de contenido (QStackedWidget)

        self.contenido_menu_lateral = QStackedWidget()

        # Instanciar las Vistas

        self.dashboard = DashboardView()
        self.clientes = Clientes()
        self.equipos = Equipos()
        self.diagnostico = Diagnostico_Equipos()
        self.componentes = Componentes_Equipos()
        self.reparaciones = Reparaciones_Equipos()
        self.mantenimiento = Mantenimientos_Equipos()
        self.historial = Historial_Equipos()
        self.estados = Estados_Equipos()
        self.reportes = Reportes_Equipos()
        self.configuraciones = Configuraciones_sistema()
        self.usuarios = Usuarios()


        # Agregar las vistas al StackedWidget

        self.contenido_menu_lateral.addWidget(self.dashboard)  # Pagina 0
        self.contenido_menu_lateral.addWidget(self.clientes)   # Pagina 1
        self.contenido_menu_lateral.addWidget(self.equipos)    # Pagina 2
        self.contenido_menu_lateral.addWidget(self.diagnostico) # pagina 3
        self.contenido_menu_lateral.addWidget(self.componentes)  # pagina 4 
        self.contenido_menu_lateral.addWidget(self.reparaciones) # Pagina 5
        self.contenido_menu_lateral.addWidget(self.mantenimiento) # Pagina 6 
        self.contenido_menu_lateral.addWidget(self.historial)          
        self.contenido_menu_lateral.addWidget(self.estados)
        self.contenido_menu_lateral.addWidget(self.reportes)
        self.contenido_menu_lateral.addWidget(self.configuraciones)
        self.contenido_menu_lateral.addWidget(self.usuarios)

        # Ensamblar parte derecha
        layout_derecho.addWidget(top_bar)
        layout_derecho.addWidget(self.contenido_menu_lateral)

        contenedor_derecho = QWidget()
        contenedor_derecho.setLayout(layout_derecho)

        # Agregar menú y contenido al layout principal
        layout_principal.addWidget(self.menu_lateral)
        layout_principal.addWidget(contenedor_derecho)

        contenedor.setLayout(layout_principal)
        self.setCentralWidget(contenedor)

    def crear_menu(self):

        menu = QFrame()
        menu.setObjectName("menuLateral")
        menu.setFixedWidth(230)

        layout_menu = QVBoxLayout()
        layout_menu.setContentsMargins(15, 20, 15, 20)
        layout_menu.setSpacing(8)

        self.lbl_titulo = QLabel("SGE")
        self.lbl_titulo.setObjectName("menuTitulo")

        layout_menu.addWidget(self.lbl_titulo)
        layout_menu.addSpacing(20)

        # Lista de botones con sus textos originales guardados para el menu del dasboard
        self.btn_dashboard_principal = QPushButton("Dashboard")
        self.btn_clientes_principal = QPushButton("Clientes")
        self.btn_equipos_principal = QPushButton("Equipos")
        self.btn_diagnosticos_principal = QPushButton("Diagnósticos")
        self.btn_componentes_principal = QPushButton("Componentes")
        self.btn_reparaciones_principal = QPushButton("Reparaciones")
        self.btn_mantenimientos_principal = QPushButton("Mantenimientos")
        self.btn_estados_principal = QPushButton("Estados")
        self.btn_historial_principal = QPushButton("Historial")
        self.btn_reportes_principal = QPushButton("Reportes")
        self.btn_configuracion_principal = QPushButton("Configuracion")
        self.btn_gestion_usuarios =QPushButton("Gestion de usuarios")
        

        self.botones_menu = [
            (self.btn_dashboard_principal, "Dashboard"),
            (self.btn_clientes_principal, "Clientes"),
            (self.btn_equipos_principal, "Equipos"),
            (self.btn_diagnosticos_principal, "Diagnósticos"),
            (self.btn_componentes_principal, "Componentes"),
            (self.btn_reparaciones_principal, "Reparaciones"),
            (self.btn_mantenimientos_principal, "Mantenimientos"),
            (self.btn_historial_principal, "Historial"),
            (self.btn_estados_principal, "Estados"),
            (self.btn_reportes_principal,"Reportes"),
            (self.btn_configuracion_principal,"Configuracion"),
            (self.btn_gestion_usuarios,"Gestion de usuarios")
        ]

        for boton, texto in self.botones_menu:
            boton.setObjectName("menuButton")
            boton.setMinimumHeight(42)
            boton.setCursor(Qt.PointingHandCursor)
            layout_menu.addWidget(boton)

        layout_menu.addStretch()

        self.btn_salir = QPushButton("Cerrar sesión")
        self.btn_salir.setObjectName("btnSalir")
        self.btn_salir.setCursor(Qt.PointingHandCursor)
        self.texto_btn_salir = "Cerrar sesión"

        layout_menu.addWidget(self.btn_salir)

        menu.setLayout(layout_menu)

        return menu

    # MÉTODOS DE CONEXIÓN DE EVENTOS

    def conectar_eventos(self):
        """Conecta los clics de los botones con el cambio de vista y la animación del menú."""
        self.btn_dashboard_principal.clicked.connect(self.mostrar_dashboard)
        self.btn_clientes_principal.clicked.connect(self.mostrar_clientes)
        self.btn_equipos_principal.clicked.connect(self.mostrar_equipos)
        self.btn_diagnosticos_principal.clicked.connect(self.mostrar_diagnosticos)
        self.btn_componentes_principal.clicked.connect(self.mostrar_componentes)
        self.btn_reparaciones_principal.clicked.connect(self.mostrar_reparaciones)
        self.btn_mantenimientos_principal.clicked.connect(self.mostrar_mantenimientos)
        self.btn_historial_principal.clicked.connect(self.mostrar_historial)
        self.btn_estados_principal.clicked.connect(self.mostrar_estados)
        self.btn_reportes_principal.clicked.connect(self.mostrar_reportes)
        self.btn_configuracion_principal.clicked.connect(self.mostrar_configuracion_sistema)
        self.btn_gestion_usuarios.clicked.connect(self.mostrar_gestion_usuarios)
        self.btn_toggle.clicked.connect(self.toggle_menu)

    def toggle_menu(self):
        """Alterna el tamaño del menú lateral entre expandido (230px) y colapsado (60px)."""
        if self.menu_expandido:
            # Colapsar menú
            self.menu_lateral.setFixedWidth(60)
            self.lbl_titulo.setText("S")  # Versión corta del título
            
            # Ocultar textos de los botones principales
            for boton, _ in self.botones_menu:
                boton.setText("")
                
            self.btn_salir.setText("")
            self.menu_expandido = False
        else:
            # Expandir menú
            self.menu_lateral.setFixedWidth(230)
            self.lbl_titulo.setText("SGE")
            
            # Restaurar textos originales
            for boton, texto_original in self.botones_menu:
                boton.setText(texto_original)
                
            self.btn_salir.setText(self.texto_btn_salir)
            self.menu_expandido = True

    def mostrar_dashboard(self):
        """Muestra la vista del Dashboard."""
        self.contenido_menu_lateral.setCurrentWidget(self.dashboard)

    def mostrar_clientes(self):
        """Muestra la vista de Clientes reemplazando el contenido."""
        self.contenido_menu_lateral.setCurrentWidget(self.clientes)

    def mostrar_equipos(self):
        """ Muestra la vista de los equipos """
        self.contenido_menu_lateral.setCurrentWidget(self.equipos)

    def mostrar_diagnosticos(self):
        """muestra la ventana de diagnostico"""
        self.contenido_menu_lateral.setCurrentWidget(self.diagnostico)

    def mostrar_componentes(self):
        """Muestra el menu..."""
        self.contenido_menu_lateral.setCurrentWidget(self.componentes)

    def mostrar_reparaciones(self):
            """Muestra el menu..."""
            self.contenido_menu_lateral.setCurrentWidget(self.reparaciones)

    def mostrar_mantenimientos(self):
            """Muestra el menu..."""
            self.contenido_menu_lateral.setCurrentWidget(self.mantenimiento)

    def mostrar_historial(self):
                """Muestra el menu..."""
                self.contenido_menu_lateral.setCurrentWidget(self.historial)

    def mostrar_estados(self):
                """Muestra el menu..."""
                self.contenido_menu_lateral.setCurrentWidget(self.estados)

    def mostrar_reportes(self):
                """Muestra el menu..."""
                self.contenido_menu_lateral.setCurrentWidget(self.reportes)

    def mostrar_configuracion_sistema(self):
                """Muestra el menu..."""
                self.contenido_menu_lateral.setCurrentWidget(self.configuraciones)

    def mostrar_gestion_usuarios(self):
            """Muestra el menu de gestion de usuario"""
            self.contenido_menu_lateral.setCurrentWidget(self.usuarios)


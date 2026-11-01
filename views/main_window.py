from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
    QSizePolicy,
    QButtonGroup
)

from PySide6.QtCore import Qt, Signal, QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

# Importación de las vistas
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


# Íconos vectoriales dibujados en memoria: no requieren archivos externos.
# PySide6.QtSvg viene incluido normalmente con la instalación de PySide6.
ICON_PATHS = {
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    "clientes": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "equipos": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "diagnosticos": '<rect x="8" y="3" width="12" height="18" rx="2"/><path d="M4 7V5a2 2 0 0 1 2-2h2M11 8h6M11 12h6M11 16h4"/>',
    "componentes": '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/>',
    "reparaciones": '<path d="M14.7 6.3a5 5 0 0 0-6.4 6.4l-6.3 6.3a2 2 0 0 0 2.8 2.8l6.3-6.3a5 5 0 0 0 6.4-6.4l-3.3 3.3-2.8-2.8z"/>',
    "mantenimientos": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M8 16h3"/>',
    "historial": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
    "estados": '<path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h11"/>',
    "reportes": '<path d="M4 21V10M10 21V3M16 21v-7M22 21v-11"/>',
    "configuracion": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06-1.87 1.87-.06-.06A1.7 1.7 0 0 0 16 18.4a1.7 1.7 0 0 0-1.2 1.6V21h-5.6v-1a1.7 1.7 0 0 0-1.2-1.6 1.7 1.7 0 0 0-1.87.34l-.06.06L4.2 16.93l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.6-1.2H2v-3.6h1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87L4.2 7.07 6.07 5.2l.06.06A1.7 1.7 0 0 0 8 5.6 1.7 1.7 0 0 0 9.2 4V3h5.6v1A1.7 1.7 0 0 0 16 5.6a1.7 1.7 0 0 0 1.87-.34l.06-.06 1.87 1.87-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.6 1.2h1v3.6h-1a1.7 1.7 0 0 0-1.6 1.2z"/>',
    "usuarios": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M18 8v6M15 11h6"/>',
    "salir": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
}


def crear_icono(nombre, color="#FFFFFF"):
    dibujo = ICON_PATHS[nombre]
    svg = ( f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'{dibujo}</svg>')
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    renderizador = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    painter = QPainter(pixmap)
    renderizador.render(painter)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):

    # Señal para comunicar el cierre de sesión a main.py
    cerrar_sesion_solicitada = Signal()

    def __init__(self, usuario_actual):
        super().__init__()

        # Datos del usuario autenticado
        self.usuario_actual = usuario_actual

        self.setWindowTitle(
            "Sistema de Diagnóstico y Control de Equipos Informáticos"
        )
        self.setMinimumSize(1100, 700)

        # Estado del menú lateral
        self.menu_expandido = True

        self.crear_interfaz()
        self.conectar_eventos()
        self.configurar_permisos()
        self.configurar_estado_activo()

    # ==========================================
    # CREAR INTERFAZ PRINCIPAL
    # ==========================================

    def crear_interfaz(self):

        contenedor = QWidget()

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # Menú lateral
        self.menu_lateral = self.crear_menu()

        # Contenedor derecho
        layout_derecho = QVBoxLayout()
        layout_derecho.setContentsMargins(0, 0, 0, 0)
        layout_derecho.setSpacing(0)

        # Barra superior
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(50)

        layout_top = QHBoxLayout(top_bar)
        layout_top.setContentsMargins(10, 0, 15, 0)

        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setObjectName("btnToggleMenu")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)

        layout_top.addWidget(self.btn_toggle)
        layout_top.addStretch()

        # Información del usuario
        self.lbl_usuario_actual = QLabel(
            f"{self.usuario_actual['nombre']} "
            f"({self.usuario_actual['rol']})"
        )

        layout_top.addWidget(self.lbl_usuario_actual)

        # ======================================
        # QSTACKEDWIDGET
        # ======================================

        self.contenido_menu_lateral = QStackedWidget()

        # Instanciar vistas
        self.dashboard = DashboardView()
        self.clientes = Clientes()
        self.equipos = Equipos()
        self.diagnostico = Diagnostico_Equipos()
        self.componentes = Componentes_Equipos()
        self.reparaciones = Reparaciones_Equipos()
        self.mantenimiento = Mantenimientos_Equipos()
        self.historial = Historial_Equipos()
        self.reportes = Reportes_Equipos()

        # Vistas administrativas
        self.estados = None
        self.configuraciones = None
        self.usuarios = None

        if self.es_administrador():

            self.estados = Estados_Equipos()

            self.configuraciones = Configuraciones_sistema(id_administrador=self.usuario_actual["id_usuario"])

            self.usuarios = Usuarios(
                id_administrador=(
                    self.usuario_actual["id_usuario"]
                )
            )

        # Agregar vistas al QStackedWidget
        self.contenido_menu_lateral.addWidget(
            self.dashboard
        )
        self.contenido_menu_lateral.addWidget(
            self.clientes
        )
        self.contenido_menu_lateral.addWidget(
            self.equipos
        )
        self.contenido_menu_lateral.addWidget(
            self.diagnostico
        )
        self.contenido_menu_lateral.addWidget(
            self.componentes
        )
        self.contenido_menu_lateral.addWidget(
            self.reparaciones
        )
        self.contenido_menu_lateral.addWidget(
            self.mantenimiento
        )
        self.contenido_menu_lateral.addWidget(
            self.historial
        )
        self.contenido_menu_lateral.addWidget(
            self.reportes
        )

        if self.estados is not None:
            self.contenido_menu_lateral.addWidget(
                self.estados
            )

        if self.configuraciones is not None:
            self.contenido_menu_lateral.addWidget(
                self.configuraciones
            )

        if self.usuarios is not None:
            self.contenido_menu_lateral.addWidget(
                self.usuarios
            )

        # Ensamblar parte derecha
        layout_derecho.addWidget(top_bar)
        layout_derecho.addWidget(
            self.contenido_menu_lateral
        )

        contenedor_derecho = QWidget()
        contenedor_derecho.setLayout(layout_derecho)

        layout_principal.addWidget(
            self.menu_lateral
        )
        layout_principal.addWidget(
            contenedor_derecho
        )

        contenedor.setLayout(layout_principal)
        self.setCentralWidget(contenedor)

    # ==========================================
    # CREAR MENÚ LATERAL
    # ==========================================

    def crear_menu(self):

        menu = QFrame()
        menu.setObjectName("menuLateral")
        menu.setFixedWidth(250)

        layout_menu = QVBoxLayout()
        layout_menu.setContentsMargins(12, 18, 12, 18)
        layout_menu.setSpacing(5)

        self.lbl_titulo = QLabel("")
        self.lbl_titulo.setObjectName("menuTitulo")

        layout_menu.addWidget(self.lbl_titulo)
        layout_menu.addSpacing(12)

        # Botones principales
        self.btn_dashboard_principal = QPushButton(
            "Dashboard"
        )
        self.btn_clientes_principal = QPushButton(
            "Clientes"
        )
        self.btn_equipos_principal = QPushButton(
            "Equipos"
        )
        self.btn_diagnosticos_principal = QPushButton(
            "Diagnósticos"
        )
        self.btn_componentes_principal = QPushButton(
            "Componentes"
        )
        self.btn_reparaciones_principal = QPushButton(
            "Reparaciones"
        )
        self.btn_mantenimientos_principal = QPushButton(
            "Mantenimientos"
        )
        self.btn_estados_principal = QPushButton(
            "Estados"
        )
        self.btn_historial_principal = QPushButton(
            "Historial"
        )
        self.btn_reportes_principal = QPushButton(
            "Reportes"
        )
        self.btn_configuracion_principal = QPushButton(
            "Configuracion"
        )
        self.btn_gestion_usuarios = QPushButton(
            "Gestion de usuarios"
        )

        # Lista de botones, textos originales e iconos
        self.botones_menu = [
            (self.btn_dashboard_principal, "Dashboard", "dashboard"),
            (self.btn_clientes_principal, "Clientes", "clientes"),
            (self.btn_equipos_principal, "Equipos", "equipos"),
            (self.btn_diagnosticos_principal, "Diagnósticos", "diagnosticos"),
            (self.btn_componentes_principal, "Componentes", "componentes"),
            (self.btn_reparaciones_principal, "Reparaciones", "reparaciones"),
            (self.btn_mantenimientos_principal, "Mantenimientos", "mantenimientos"),
            (self.btn_historial_principal, "Historial", "historial"),
            (self.btn_estados_principal, "Estados", "estados"),
            (self.btn_reportes_principal, "Reportes", "reportes"),
            (self.btn_configuracion_principal, "Configuración", "configuracion"),
            (self.btn_gestion_usuarios, "Gestión de usuarios", "usuarios")
        ]

        for boton, texto, icono in self.botones_menu:
            boton.setObjectName("menuButton")
            boton.setText(texto)
            boton.setIcon(crear_icono(icono))
            boton.setIconSize(QSize(20, 20))
            boton.setToolTip(texto)
            boton.setCheckable(True)
            boton.setFixedHeight(42)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setStyleSheet("text-align: left; padding-left: 12px;")
            layout_menu.addWidget(boton)

        layout_menu.addStretch()

        # Botón de cerrar sesión
        self.btn_salir = QPushButton(
            "Cerrar sesión"
        )
        self.btn_salir.setObjectName("btnSalir")
        self.btn_salir.setCursor(Qt.PointingHandCursor)

        self.btn_salir.setIcon(crear_icono("salir"))
        self.btn_salir.setIconSize(QSize(20, 20))
        self.btn_salir.setFixedHeight(42)
        self.btn_salir.setToolTip("Cerrar sesión")
        self.texto_btn_salir = "Cerrar sesión"

        layout_menu.addWidget(self.btn_salir)

        menu.setLayout(layout_menu)

        return menu

    # ==========================================
    # CONECTAR EVENTOS
    # ==========================================

    def conectar_eventos(self):

        self.btn_dashboard_principal.clicked.connect(
            self.mostrar_dashboard
        )
        self.btn_clientes_principal.clicked.connect(
            self.mostrar_clientes
        )
        self.btn_equipos_principal.clicked.connect(
            self.mostrar_equipos
        )
        self.btn_diagnosticos_principal.clicked.connect(
            self.mostrar_diagnosticos
        )
        self.btn_componentes_principal.clicked.connect(
            self.mostrar_componentes
        )
        self.btn_reparaciones_principal.clicked.connect(
            self.mostrar_reparaciones
        )
        self.btn_mantenimientos_principal.clicked.connect(
            self.mostrar_mantenimientos
        )
        self.btn_historial_principal.clicked.connect(
            self.mostrar_historial
        )
        self.btn_estados_principal.clicked.connect(
            self.mostrar_estados
        )
        self.btn_reportes_principal.clicked.connect(
            self.mostrar_reportes
        )
        self.btn_configuracion_principal.clicked.connect(
            self.mostrar_configuracion_sistema
        )
        self.btn_gestion_usuarios.clicked.connect(
            self.mostrar_gestion_usuarios
        )

        self.btn_toggle.clicked.connect(
            self.toggle_menu
        )

        self.btn_salir.clicked.connect(
            self.solicitar_cierre_sesion
        )

    # ==========================================
    # VERIFICAR ROL
    # ==========================================

    def es_administrador(self):

        return (
            self.usuario_actual["rol"]
            == "Administrador"
        )

    # ==========================================
    # CONFIGURAR PERMISOS VISUALES
    # ==========================================

    def configurar_permisos(self):

        administrador = self.es_administrador()

        self.btn_gestion_usuarios.setVisible(
            administrador
        )

        self.btn_estados_principal.setVisible(
            administrador
        )

        self.btn_configuracion_principal.setVisible(
            administrador
        )

    # ==========================================
    # EXPANDIR / CONTRAER MENÚ
    # ==========================================

    def toggle_menu(self):
        self.menu_expandido = not self.menu_expandido

        if self.menu_expandido:
            self.menu_lateral.setFixedWidth(250)
            self.menu_lateral.layout().setContentsMargins(12, 18, 12, 18)
            self.lbl_titulo.setText("SGE")
            self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            self.menu_lateral.setFixedWidth(68)
            self.menu_lateral.layout().setContentsMargins(8, 18, 8, 18)
            self.lbl_titulo.setText("S")
            self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for boton, texto, _ in self.botones_menu:
            boton.setText(texto if self.menu_expandido else "")
            boton.setToolTip(texto)
            boton.setStyleSheet(
                "text-align: left; padding-left: 12px;"
                if self.menu_expandido
                else "padding-left: 0px;"
            )

        self.btn_salir.setText(
            self.texto_btn_salir if self.menu_expandido else ""
        )
        self.btn_salir.setToolTip(self.texto_btn_salir)
        self.btn_salir.setStyleSheet(
            "text-align: left; padding-left: 12px;"
            if self.menu_expandido else "padding-left: 0px;"
        )

    def configurar_estado_activo(self):
        # Se actualiza al cambiar de página, incluso usando métodos anteriores.
        self.pagina_por_boton = {
            self.btn_dashboard_principal: self.dashboard,
            self.btn_clientes_principal: self.clientes,
            self.btn_equipos_principal: self.equipos,
            self.btn_diagnosticos_principal: self.diagnostico,
            self.btn_componentes_principal: self.componentes,
            self.btn_reparaciones_principal: self.reparaciones,
            self.btn_mantenimientos_principal: self.mantenimiento,
            self.btn_historial_principal: self.historial,
            self.btn_reportes_principal: self.reportes,
        }
        if self.estados is not None:
            self.pagina_por_boton[self.btn_estados_principal] = self.estados
        if self.configuraciones is not None:
            self.pagina_por_boton[self.btn_configuracion_principal] = self.configuraciones
        if self.usuarios is not None:
            self.pagina_por_boton[self.btn_gestion_usuarios] = self.usuarios

        self.contenido_menu_lateral.currentChanged.connect(
            self.actualizar_boton_activo
        )
        self.actualizar_boton_activo()

    def actualizar_boton_activo(self, indice=None):
        pagina = self.contenido_menu_lateral.currentWidget()
        for boton, vista in self.pagina_por_boton.items():
            boton.setChecked(vista is pagina)

    # ==========================================
    # NAVEGACIÓN GENERAL
    # ==========================================

    def mostrar_dashboard(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.dashboard
        )

    def mostrar_clientes(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.clientes
        )

    def mostrar_equipos(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.equipos
        )

    def mostrar_diagnosticos(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.diagnostico
        )

    def mostrar_componentes(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.componentes
        )

    def mostrar_reparaciones(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.reparaciones
        )

    def mostrar_mantenimientos(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.mantenimiento
        )

    def mostrar_historial(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.historial
        )

    def mostrar_reportes(self):

        self.contenido_menu_lateral.setCurrentWidget(
            self.reportes
        )

    # ==========================================
    # NAVEGACIÓN ADMINISTRATIVA
    # ==========================================

    def mostrar_estados(self):

        if not self.es_administrador():
            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No tienes permisos para gestionar estados."
            )
            return

        if self.estados is not None:
            self.contenido_menu_lateral.setCurrentWidget(
                self.estados
            )

    def mostrar_configuracion_sistema(self):

        if not self.es_administrador():
            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No tienes permisos para acceder "
                "a la configuración."
            )
            return

        if self.configuraciones is not None:
            self.contenido_menu_lateral.setCurrentWidget(
                self.configuraciones
            )

    def mostrar_gestion_usuarios(self):

        if not self.es_administrador():
            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No tienes permisos para gestionar usuarios."
            )
            return

        if self.usuarios is not None:
            self.contenido_menu_lateral.setCurrentWidget(
                self.usuarios
            )

    # ==========================================
    # CERRAR SESIÓN
    # ==========================================

    def solicitar_cierre_sesion(self):

        respuesta = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Deseas cerrar tu sesión actual?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:

            self.cerrar_sesion_solicitada.emit()

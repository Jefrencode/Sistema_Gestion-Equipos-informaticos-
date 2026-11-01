
import re

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QComboBox,
    QLabel,
    QSizePolicy
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from controllers.configuracion_controller import ConfiguracionController


class Configuraciones_sistema(QWidget):

    def __init__(self, id_administrador):
        super().__init__()

        self.controller = ConfiguracionController(id_administrador)

        self.crear_interfaz()
        self.conexiones_botones()

        self.cargar_configuracion()
        self.verificar_conexion()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def crear_interfaz(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 20, 25, 20)
        layout_principal.setSpacing(20)

        # ENCABEZADO
        titulo = QLabel("Configuración del sistema")
        titulo.setObjectName("tituloConfiguracion")

        descripcion = QLabel(
            "Administra la información del taller "
            "y las preferencias de la aplicación."
        )
        descripcion.setWordWrap(True)

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(descripcion)

        # ======================================
        # INFORMACIÓN DEL TALLER
        # ======================================

        grupo_taller = QGroupBox("Información del taller")
        formulario_taller = QFormLayout(grupo_taller)
        formulario_taller.setSpacing(15)

        self.txt_nombre_taller = QLineEdit()
        self.txt_nombre_taller.setPlaceholderText(
            "Nombre del taller"
        )
        self.txt_nombre_taller.setMaxLength(160)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText(
            "Número de teléfono"
        )
        self.txt_telefono.setMaxLength(30)

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText(
            "Correo electrónico"
        )
        self.txt_correo.setMaxLength(160)

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText(
            "Dirección del taller"
        )
        self.txt_direccion.setMaxLength(255)

        formulario_taller.addRow(
            "Nombre:", self.txt_nombre_taller
        )
        formulario_taller.addRow(
            "Teléfono:", self.txt_telefono
        )
        formulario_taller.addRow(
            "Correo:", self.txt_correo
        )
        formulario_taller.addRow(
            "Dirección:", self.txt_direccion
        )

        layout_principal.addWidget(grupo_taller)

        # ======================================
        # PREFERENCIAS DEL SISTEMA
        # ======================================

        grupo_preferencias = QGroupBox(
            "Preferencias del sistema"
        )

        formulario_preferencias = QFormLayout(
            grupo_preferencias
        )
        formulario_preferencias.setSpacing(15)

        self.cbx_formato_fecha = QComboBox()
        self.cbx_formato_fecha.addItems([
            "dd/MM/yyyy",
            "yyyy-MM-dd"
        ])

        self.cbx_confirmacion = QComboBox()
        self.cbx_confirmacion.addItems([
            "Sí",
            "No"
        ])

        formulario_preferencias.addRow(
            "Formato de fecha:",
            self.cbx_formato_fecha
        )

        formulario_preferencias.addRow(
            "Confirmar acciones:",
            self.cbx_confirmacion
        )

        layout_principal.addWidget(
            grupo_preferencias
        )

        # ======================================
        # ESTADO DE CONEXIÓN
        # ======================================

        grupo_datos = QGroupBox(
            "Estado de la conexión"
        )

        layout_datos = QVBoxLayout(grupo_datos)

        fila_conexion = QHBoxLayout()

        self.lbl_estado_conexion = QLabel(
            "Comprobando conexión..."
        )
        self.lbl_estado_conexion.setWordWrap(True)

        self.btn_verificar = QPushButton(
            "Verificar conexión"
        )

        fila_conexion.addWidget(
            self.lbl_estado_conexion, 1
        )
        fila_conexion.addWidget(
            self.btn_verificar
        )

        layout_datos.addLayout(fila_conexion)
        layout_principal.addWidget(grupo_datos)

        # ======================================
        # BOTONES
        # ======================================

        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton(
            "Guardar configuración"
        )

        self.btn_limpiar = QPushButton(
            "Restablecer formulario"
        )

        layout_botones.addStretch()
        layout_botones.addWidget(
            self.btn_limpiar
        )
        layout_botones.addWidget(
            self.btn_guardar
        )

        layout_principal.addLayout(
            layout_botones
        )

        layout_principal.addStretch()

    # ==========================================
    # CONEXIONES
    # ==========================================

    def conexiones_botones(self):
        self.btn_guardar.clicked.connect(
            self.guardar_configuracion
        )

        self.btn_limpiar.clicked.connect(
            self.restablecer_formulario
        )

        self.btn_verificar.clicked.connect(
            self.verificar_conexion
        )

    # ==========================================
    # CARGAR CONFIGURACIÓN
    # ==========================================

    def cargar_configuracion(self):
        try:
            datos = self.controller.obtener_configuracion()

            if datos is None:
                self.limpiar_campos()
                return

            self.txt_nombre_taller.setText(
                datos["nombre_taller"]
            )

            self.txt_telefono.setText(
                datos["telefono"]
            )

            self.txt_correo.setText(
                datos["correo"]
            )

            self.txt_direccion.setText(
                datos["direccion"]
            )

            self.cbx_formato_fecha.setCurrentText(
                datos["formato_fecha"]
            )

            self.cbx_confirmacion.setCurrentText(
                "Sí" if datos["confirmar_acciones"] else "No"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error de carga",
                "No se pudo cargar la configuración.\n"
                f"Detalle: {error}"
            )

    # ==========================================
    # VALIDACIONES
    # ==========================================

    def validar_formulario(self):
        nombre = self.txt_nombre_taller.text().strip()
        telefono = self.txt_telefono.text().strip()
        correo = self.txt_correo.text().strip()

        if not nombre:
            QMessageBox.warning(
                self,
                "Campo obligatorio",
                "Introduce el nombre del taller."
            )
            self.txt_nombre_taller.setFocus()
            return False

        if telefono and not re.fullmatch(
            r"[0-9+\-\s()]{7,30}",
            telefono
        ):
            QMessageBox.warning(
                self,
                "Teléfono inválido",
                "Introduce un número de teléfono válido."
            )
            self.txt_telefono.setFocus()
            return False

        if correo and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            correo
        ):
            QMessageBox.warning(
                self,
                "Correo inválido",
                "Introduce un correo electrónico válido."
            )
            self.txt_correo.setFocus()
            return False

        return True

    # ==========================================
    # GUARDAR CONFIGURACIÓN
    # ==========================================

    def guardar_configuracion(self):
        if not self.validar_formulario():
            return

        datos = {
            "nombre_taller":
                self.txt_nombre_taller.text().strip(),

            "telefono":
                self.txt_telefono.text().strip(),

            "correo":
                self.txt_correo.text().strip(),

            "direccion":
                self.txt_direccion.text().strip(),

            "formato_fecha":
                self.cbx_formato_fecha.currentText(),

            "confirmar_acciones":
                self.cbx_confirmacion.currentText() == "Sí"
        }

        try:
            # Consultamos la preferencia guardada
            configuracion_actual = (
                self.controller.obtener_configuracion()
            )

            requiere_confirmacion = True

            if configuracion_actual is not None:
                requiere_confirmacion = (
                    configuracion_actual["confirmar_acciones"]
                )

            if requiere_confirmacion:
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar cambios",
                    "¿Deseas guardar los cambios "
                    "de configuración?",
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if respuesta != QMessageBox.StandardButton.Yes:
                    return

            self.controller.guardar_configuracion(
                datos
            )

            QMessageBox.information(
                self,
                "Configuración guardada",
                "Los cambios se guardaron "
                "correctamente en MySQL."
            )

        except PermissionError as error:
            QMessageBox.warning(
                self,
                "Acceso denegado",
                str(error)
            )

        except (ValueError, KeyError) as error:
            QMessageBox.warning(
                self,
                "Datos inválidos",
                str(error)
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al guardar",
                "No se pudo guardar la configuración.\n"
                f"Detalle: {error}"
            )

    # ==========================================
    # RESTABLECER FORMULARIO
    # ==========================================

    def restablecer_formulario(self):
        respuesta = QMessageBox.question(
            self,
            "Restablecer formulario",
            "¿Deseas recuperar los últimos "
            "valores guardados?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.cargar_configuracion()

    def limpiar_campos(self):
        self.txt_nombre_taller.clear()
        self.txt_telefono.clear()
        self.txt_correo.clear()
        self.txt_direccion.clear()

        self.cbx_formato_fecha.setCurrentIndex(0)
        self.cbx_confirmacion.setCurrentIndex(0)

    # ==========================================
    # VERIFICAR CONEXIÓN MYSQL
    # ==========================================

    def verificar_conexion(self):
        conectado = self.controller.verificar_conexion()

        if conectado:
            self.lbl_estado_conexion.setText(
                "MySQL: conexión establecida correctamente."
            )
            self.lbl_estado_conexion.setStyleSheet(
                "color: #16A34A;"
            )
        else:
            self.lbl_estado_conexion.setText(
                "MySQL: no se pudo establecer la conexión."
            )
            self.lbl_estado_conexion.setStyleSheet(
                "color: #DC2626;"
            )

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from views.login_view import LoginView
from views.main_window import MainWindow


def cargar_estilos(app):

    ruta_base = Path(__file__).resolve().parent

    ruta_estilos = (ruta_base/ "resourse"/ "images"/ "styles"/ "style.qss")

    with open(
        ruta_estilos,
        "r",
        encoding="utf-8"
    ) as archivo:

        app.setStyleSheet(
            archivo.read()
        )


class Aplicacion:

    def __init__(self):

        self.login = None
        self.ventana_principal = None

        self.mostrar_login()

    # ==========================================
    # MOSTRAR LOGIN
    # ==========================================

    def mostrar_login(self):

        self.login = LoginView()

        self.login.login_exitoso.connect(
            self.abrir_ventana_principal
        )

        self.login.showMaximized()

    # ==========================================
    # ABRIR VENTANA PRINCIPAL
    # ==========================================

    def abrir_ventana_principal(
        self,
        usuario_autenticado
    ):

        try:

            self.ventana_principal = MainWindow(
                usuario_actual=usuario_autenticado
            )

            # La ventana principal emitirá esta
            # señal cuando se cierre la sesión.
            self.ventana_principal.cerrar_sesion_solicitada.connect(
                self.cerrar_sesion
            )

            self.ventana_principal.showMaximized()

            self.login.hide()

        except Exception as error:

            QMessageBox.critical(
                self.login,
                "Error al abrir el sistema",
                f"No fue posible iniciar la aplicación:\n"
                f"{error}"
            )

    # ==========================================
    # CERRAR SESIÓN
    # ==========================================

    def cerrar_sesion(self):

        if self.ventana_principal is not None:

            self.ventana_principal.close()
            self.ventana_principal = None

        if self.login is not None:

            self.login.usuario.clear()
            self.login.contrasena.clear()

            self.login.showMaximized()
            self.login.usuario.setFocus()


def main():

    app = QApplication(sys.argv)

    cargar_estilos(app)

    # Mantener una referencia viva al gestor.
    gestor = Aplicacion()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

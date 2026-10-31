import sys

from PySide6.QtWidgets import QApplication

from views.login_view import LoginView
from views.main_window import MainWindow


def cargar_estilos(app):

    with open("resourse/icons/styles/style.qss","r",encoding="utf-8") as archivo:
        app.setStyleSheet(archivo.read())


def main():

    app = QApplication(sys.argv)

    cargar_estilos(app)

    ventana_principal = MainWindow()
    ventana_principal.showMaximized()

    login = LoginView(ventana_principal)

    login.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


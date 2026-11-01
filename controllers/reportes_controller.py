
from datetime import date, datetime
from html import escape
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Border,
    Side,
    Alignment
)
from openpyxl.worksheet.page import PageMargins

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    LongTable,
    TableStyle
)

from controllers.historial_controllers import HistorialController


class ReportesController:

    TIPOS_PERMITIDOS = {
        "Todos los registros",
        "Equipos",
        "Diagnósticos",
        "Reparaciones",
        "Mantenimientos"
    }

    def __init__(self):
        self.historial_controller = HistorialController()

    # ==========================================
    # VALIDAR FILTROS
    # ==========================================

    def validar_filtros(
        self,
        tipo_reporte,
        fecha_inicio,
        fecha_fin
    ):

        if tipo_reporte not in self.TIPOS_PERMITIDOS:
            raise ValueError(
                "El tipo de reporte no es válido."
            )

        if (
            not isinstance(fecha_inicio, date)
            or isinstance(fecha_inicio, datetime)
            or not isinstance(fecha_fin, date)
            or isinstance(fecha_fin, datetime)
        ):
            raise ValueError(
                "Las fechas seleccionadas no son válidas."
            )

        if fecha_inicio > fecha_fin:
            raise ValueError(
                "La fecha inicial no puede ser "
                "posterior a la fecha final."
            )

    # ==========================================
    # CONSULTAR REGISTROS
    # ==========================================

    def generar_reporte(
        self,
        tipo_reporte,
        fecha_inicio,
        fecha_fin
    ):

        self.validar_filtros(
            tipo_reporte,
            fecha_inicio,
            fecha_fin
        )

        historial = (
            self.historial_controller.listar_historial()
        )

        resultados = []

        for registro in historial:

            tipo = registro["tipo"]
            fecha = registro["fecha"]

            # Clientes no tiene fecha de registro
            # en nuestro esquema actual.
            if tipo == "Clientes":
                continue

            if fecha is None:
                continue

            # Por seguridad, normalizar datetime.
            if isinstance(fecha, datetime):
                fecha = fecha.date()

            if not (
                fecha_inicio <= fecha <= fecha_fin
            ):
                continue

            if (
                tipo_reporte != "Todos los registros"
                and tipo != tipo_reporte
            ):
                continue

            resultados.append({
                "fecha": fecha,
                "tipo": tipo,
                "equipo": registro["referencia"],
                "descripcion": registro["descripcion"],
                "estado": registro["estado"]
            })

        resultados.sort(
            key=lambda item: item["fecha"],
            reverse=True
        )

        return resultados

    # ==========================================
    # VALIDAR DATOS DE EXPORTACIÓN
    # ==========================================

    def validar_exportacion(
        self,
        ruta,
        registros,
        tipo_reporte,
        fecha_inicio,
        fecha_fin,
        extension
    ):

        self.validar_filtros(
            tipo_reporte,
            fecha_inicio,
            fecha_fin
        )

        if not registros:
            raise ValueError(
                "No existen registros para exportar."
            )

        ruta = Path(ruta)

        if ruta.suffix.lower() != extension:
            raise ValueError(
                f"El archivo debe tener extensión {extension}."
            )

        return ruta

    # ==========================================
    # EVITAR FÓRMULAS EN TEXTO EXCEL
    # ==========================================

    @staticmethod
    def texto_excel(valor):

        texto = str(
            "" if valor is None else valor
        )

        # Los datos provienen de campos editables.
        # Evitar que Excel los interprete
        # como fórmulas al abrir el archivo.
        if texto.lstrip().startswith(
            ("=", "+", "-", "@")
        ):
            texto = "'" + texto

        return texto

    # ==========================================
    # EXPORTAR EXCEL
    # ==========================================

    def exportar_excel(
        self,
        ruta,
        registros,
        tipo_reporte,
        fecha_inicio,
        fecha_fin
    ):

        ruta = self.validar_exportacion(
            ruta,
            registros,
            tipo_reporte,
            fecha_inicio,
            fecha_fin,
            ".xlsx"
        )

        libro = Workbook()
        hoja = libro.active
        hoja.title = "Reporte"

        azul_oscuro = "17365D"
        azul_medio = "245A81"
        blanco = "FFFFFF"
        gris_claro = "F1F5F9"
        gris_borde = "D5DFE8"

        # ENCABEZADO PRINCIPAL

        hoja.merge_cells("A1:E2")

        titulo = hoja["A1"]
        titulo.value = (
            "SISTEMA DE GESTIÓN Y DIAGNÓSTICO "
            "DE EQUIPOS INFORMÁTICOS"
        )

        titulo.font = Font(
            name="Calibri",
            size=15,
            bold=True,
            color=blanco
        )

        titulo.fill = PatternFill(
            fill_type="solid",
            fgColor=azul_oscuro
        )

        titulo.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

        hoja.row_dimensions[1].height = 26
        hoja.row_dimensions[2].height = 26

        # SUBTÍTULO

        hoja.merge_cells("A4:E4")

        subtitulo = hoja["A4"]
        subtitulo.value = (
            f"REPORTE DE {tipo_reporte.upper()}"
        )

        subtitulo.font = Font(
            name="Calibri",
            size=13,
            bold=True,
            color=azul_oscuro
        )

        subtitulo.alignment = Alignment(
            horizontal="center"
        )

        # INFORMACIÓN GENERAL

        hoja["A6"] = "Fecha inicial:"
        hoja["B6"] = fecha_inicio
        hoja["B6"].number_format = "DD/MM/YYYY"

        hoja["C6"] = "Fecha final:"
        hoja["D6"] = fecha_fin
        hoja["D6"].number_format = "DD/MM/YYYY"

        hoja["A7"] = "Total de registros:"
        hoja["B7"] = len(registros)

        hoja["C7"] = "Generado:"
        hoja["D7"] = datetime.now()
        hoja["D7"].number_format = (
            "DD/MM/YYYY HH:MM"
        )

        for posicion in (
            "A6", "C6", "A7", "C7"
        ):
            hoja[posicion].font = Font(
                bold=True,
                color=azul_oscuro
            )

        # ENCABEZADOS DE LA TABLA

        encabezados = [
            "Fecha",
            "Tipo",
            "Equipo / Referencia",
            "Descripción",
            "Estado"
        ]

        fila_encabezados = 9

        for columna, encabezado in enumerate(
            encabezados,
            start=1
        ):

            celda = hoja.cell(
                row=fila_encabezados,
                column=columna,
                value=encabezado
            )

            celda.font = Font(
                bold=True,
                color=blanco
            )

            celda.fill = PatternFill(
                fill_type="solid",
                fgColor=azul_medio
            )

            celda.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )

        hoja.row_dimensions[9].height = 30

        # REGISTROS

        borde_inferior = Border(
            bottom=Side(
                style="thin",
                color=gris_borde
            )
        )

        for fila, registro in enumerate(
            registros,
            start=10
        ):

            datos = [
                registro["fecha"],
                self.texto_excel(registro["tipo"]),
                self.texto_excel(registro["equipo"]),
                self.texto_excel(
                    registro["descripcion"]
                ),
                self.texto_excel(registro["estado"])
            ]

            for columna, valor in enumerate(
                datos,
                start=1
            ):

                celda = hoja.cell(
                    row=fila,
                    column=columna,
                    value=valor
                )

                celda.alignment = Alignment(
                    vertical="top",
                    wrap_text=True
                )

                celda.border = borde_inferior

                if fila % 2 == 0:
                    celda.fill = PatternFill(
                        fill_type="solid",
                        fgColor=gris_claro
                    )

            hoja.cell(
                row=fila,
                column=1
            ).number_format = "DD/MM/YYYY"

            hoja.row_dimensions[fila].height = 42

        # ANCHOS DE COLUMNAS

        anchos = {
            "A": 17,
            "B": 21,
            "C": 43,
            "D": 85,
            "E": 23
        }

        for columna, ancho in anchos.items():
            hoja.column_dimensions[
                columna
            ].width = ancho

        ultima_fila = 9 + len(registros)

        # FILTROS Y VISTA

        hoja.auto_filter.ref = (
            f"A9:E{ultima_fila}"
        )

        hoja.freeze_panes = "A10"
        hoja.sheet_view.showGridLines = False

        # IMPRESIÓN

        hoja.print_title_rows = "1:9"
        hoja.print_options.horizontalCentered = True

        hoja.sheet_properties.pageSetUpPr.fitToPage = True
        hoja.page_setup.orientation = "landscape"
        hoja.page_setup.paperSize = hoja.PAPERSIZE_A3
        hoja.page_setup.fitToWidth = 1
        hoja.page_setup.fitToHeight = 0

        hoja.page_margins = PageMargins(
            left=0.25,
            right=0.25,
            top=0.5,
            bottom=0.5,
            header=0.2,
            footer=0.2
        )

        hoja.oddFooter.center.text = (
            "Página &P de &N"
        )

        libro.save(str(ruta))

        return str(ruta)

    # ==========================================
    # CONFIGURAR FUENTES PDF
    # ==========================================

    @staticmethod
    def configurar_fuentes_pdf():

        # Fuentes comunes de Windows.
        regular = Path(
            "C:/Windows/Fonts/arial.ttf"
        )

        negrita = Path(
            "C:/Windows/Fonts/arialbd.ttf"
        )

        if regular.exists():

            if (
                "ReporteArial"
                not in pdfmetrics.getRegisteredFontNames()
            ):
                pdfmetrics.registerFont(
                    TTFont(
                        "ReporteArial",
                        str(regular)
                    )
                )

            fuente = "ReporteArial"
            fuente_negrita = fuente

            if negrita.exists():

                if (
                    "ReporteArialBold"
                    not in pdfmetrics.getRegisteredFontNames()
                ):
                    pdfmetrics.registerFont(
                        TTFont(
                            "ReporteArialBold",
                            str(negrita)
                        )
                    )

                fuente_negrita = "ReporteArialBold"

            return fuente, fuente_negrita

        return "Helvetica", "Helvetica-Bold"

    # ==========================================
    # EXPORTAR PDF
    # ==========================================

    def exportar_pdf(
        self,
        ruta,
        registros,
        tipo_reporte,
        fecha_inicio,
        fecha_fin
    ):

        ruta = self.validar_exportacion(
            ruta,
            registros,
            tipo_reporte,
            fecha_inicio,
            fecha_fin,
            ".pdf"
        )

        fuente, fuente_negrita = (
            self.configurar_fuentes_pdf()
        )

        documento = SimpleDocTemplate(
            str(ruta),
            pagesize=landscape(A4),
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title="Reporte del sistema",
            author=(
                "Sistema de gestión y diagnóstico "
                "de equipos informáticos"
            )
        )

        estilo_titulo = ParagraphStyle(
            "TituloReporte",
            fontName=fuente_negrita,
            fontSize=15,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=12
        )

        estilo_info = ParagraphStyle(
            "InfoReporte",
            fontName=fuente,
            fontSize=9,
            leading=13,
            spaceAfter=5
        )

        estilo_celda = ParagraphStyle(
            "CeldaReporte",
            fontName=fuente,
            fontSize=8,
            leading=11,
            splitLongWords=True
        )

        estilo_encabezado = ParagraphStyle(
            "EncabezadoReporte",
            parent=estilo_celda,
            fontName=fuente_negrita,
            textColor=colors.white
        )

        elementos = []

        # TÍTULO

        elementos.append(
            Paragraph(
                "Sistema de gestión y diagnóstico "
                "de equipos informáticos",
                estilo_titulo
            )
        )

        # INFORMACIÓN DEL REPORTE

        elementos.append(
            Paragraph(
                f"Tipo de reporte: "
                f"{escape(tipo_reporte)}",
                estilo_info
            )
        )

        elementos.append(
            Paragraph(
                "Período: "
                f"{fecha_inicio:%d/%m/%Y} al "
                f"{fecha_fin:%d/%m/%Y}",
                estilo_info
            )
        )

        elementos.append(
            Paragraph(
                f"Total de registros: {len(registros)}",
                estilo_info
            )
        )

        elementos.append(
            Spacer(1, 7 * mm)
        )

        # TABLA

        encabezados = [
            "Fecha",
            "Tipo",
            "Equipo",
            "Descripción",
            "Estado"
        ]

        datos_tabla = [
            [
                Paragraph(
                    escape(encabezado),
                    estilo_encabezado
                )
                for encabezado in encabezados
            ]
        ]

        for registro in registros:

            valores = [
                registro["fecha"].strftime("%d/%m/%Y"),
                registro["tipo"],
                registro["equipo"],
                registro["descripcion"],
                registro["estado"]
            ]

            datos_tabla.append([
                Paragraph(
                    escape(str(
                        "" if valor is None else valor
                    )).replace("\n", "<br/>"),
                    estilo_celda
                )
                for valor in valores
            ])

        tabla = LongTable(
            datos_tabla,
            colWidths=[
                26 * mm,
                31 * mm,
                49 * mm,
                111 * mm,
                35 * mm
            ],
            repeatRows=1,
            hAlign="CENTER"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#203B59")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#CAD3DB")
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F2F5F8")
                    ]
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        elementos.append(tabla)

        # PIE DE PÁGINA

        def dibujar_pagina(canvas, doc):

            canvas.saveState()
            canvas.setFont(fuente, 8)

            ancho, _ = landscape(A4)

            canvas.drawRightString(
                ancho - 12 * mm,
                9 * mm,
                f"Página {doc.page}"
            )

            canvas.restoreState()

        documento.build(
            elementos,
            onFirstPage=dibujar_pagina,
            onLaterPages=dibujar_pagina
        )

        return str(ruta)

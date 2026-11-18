"""Genera el informe técnico en PDF (2-3 páginas, Times 12, interlineado 1.5).

Uso:  python docs/informe/generar_informe.py
Si existen capturas en docs/informe/capturas/ (01_compose.png, 02_api.png,
03_actions.png) se insertan automáticamente; si no, se dibuja un recuadro.
"""
import os

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ---- EDITA ESTOS DATOS ----
AUTOR = "[Nombre del estudiante]"
CURSO = "[Nombre del curso] · Actividad de aprendizaje 3"
REPO_URL = "https://github.com/USUARIO/REPO"
# ---------------------------

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "Informe_Tecnico.pdf")

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=12, leading=18, alignment=TA_JUSTIFY)
h1 = ParagraphStyle("h1", parent=body, fontName="Times-Bold", spaceBefore=4, alignment=0)
title = ParagraphStyle("title", parent=body, fontName="Times-Bold", fontSize=14, alignment=TA_CENTER)
sub = ParagraphStyle("sub", parent=body, alignment=TA_CENTER)
cap = ParagraphStyle("cap", parent=body, fontSize=10, leading=12, alignment=TA_CENTER)


def diagrama():
    d = Drawing(440, 78)
    f = "Times-Roman"

    def caja(x, y, w, h, texto, fill):
        d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=colors.black, rx=4, ry=4))
        for i, t in enumerate(texto):
            d.add(String(x + w / 2, y + h / 2 + 5 - i * 12, t, fontName=f, fontSize=10, textAnchor="middle"))

    d.add(Rect(112, 4, 318, 70, fillColor=None, strokeColor=colors.grey, strokeDashArray=[3, 2]))
    d.add(String(118, 62, "red backend (bridge)", fontName=f, fontSize=9, fillColor=colors.grey))
    caja(0, 22, 80, 34, ["Cliente", "curl / navegador"], colors.HexColor("#EEEEEE"))
    caja(135, 16, 120, 38, ["app", "Flask + Gunicorn :8000"], colors.HexColor("#DCE9F7"))
    caja(310, 16, 110, 38, ["db", "PostgreSQL 16"], colors.HexColor("#DDF0DD"))
    d.add(Line(80, 38, 135, 38))
    d.add(Line(255, 38, 310, 38))
    d.add(String(108, 42, "", fontName=f, fontSize=8, textAnchor="middle"))
    d.add(String(365, 6, "volumen pgdata", fontName=f, fontSize=9, textAnchor="middle"))
    return d


def captura(archivo, texto):
    ruta = os.path.join(AQUI, "capturas", archivo)
    ancho, alto = 5.2 * cm, 3.4 * cm
    if os.path.exists(ruta):
        img = Image(ruta, width=ancho, height=alto, kind="proportional")
    else:
        d = Drawing(ancho, alto)
        d.add(Rect(0, 0, ancho, alto, fillColor=colors.HexColor("#F5F5F5"), strokeColor=colors.grey, strokeDashArray=[3, 2]))
        d.add(String(ancho / 2, alto / 2, "[Insertar captura]", fontName="Times-Italic", fontSize=9, textAnchor="middle"))
        img = d
    return [img, Paragraph(texto, cap)]


def p(t):
    return Paragraph(t, body)


story = [
    Paragraph("Informe técnico: contenerización y flujo DevOps de Task API", title),
    Paragraph(f"{AUTOR} · {CURSO}", sub),
    Spacer(1, 6),
    Paragraph("1. Introducción", h1),
    p("Se desarrolló una API REST de tareas con Flask y PostgreSQL, ejecutada en contenedores con Docker Compose y "
      f"validada con GitHub Actions. El repositorio está en {REPO_URL}. La lógica es mínima a propósito: el foco es "
      "la infraestructura, la portabilidad y la automatización."),
    Paragraph("2. Arquitectura de contenedores", h1),
    p("Dos servicios comparten la red <i>backend</i>: <b>app</b> (API con Gunicorn) y <b>db</b> (PostgreSQL 16 sobre Alpine). "
      "Solo la API publica un puerto; la base de datos es alcanzable únicamente desde la red interna, donde se resuelve "
      "por el nombre <i>db</i>. Los datos viven en el volumen nombrado <i>pgdata</i>."),
    KeepTogether([diagrama(), Paragraph("Figura 1. Arquitectura de contenedores, red y volumen.", cap), Spacer(1, 4)]),
    Paragraph("3. Decisiones técnicas", h1),
    p("<b>Dockerfile.</b> Se usó un build multi-stage: la primera etapa instala dependencias y la final parte de "
      "<i>python:3.12-slim</i> sin caché de pip, lo que reduce tamaño y superficie de ataque. Se copia primero "
      "<i>requirements.txt</i> para aprovechar la caché de capas, se define un healthcheck sin instalar herramientas extra "
      "y se ejecuta como usuario sin privilegios. Gunicorn reemplaza al servidor de desarrollo de Flask."),
    p("<b>Compose.</b> La app espera a que la base de datos esté saludable (<i>depends_on</i> con <i>service_healthy</i>), "
      "evitando errores de arranque. Las credenciales se inyectan desde un archivo <i>.env</i> excluido de Git; solo se "
      "versiona <i>.env.example</i>. El script <i>init.sql</i> crea el esquema al inicializar el volumen."),
    Paragraph("4. Flujo de GitHub y CI/CD", h1),
    p("Se adoptó GitHub Flow: un Issue por tarea, una rama por cambio y un Pull Request con plantilla que lo cierra al "
      "fusionarse (seis PRs en total). El workflow ejecuta las pruebas con pytest, levanta todo con Compose esperando los "
      "healthchecks y consulta los endpoints; en <i>main</i> y en los tags <i>v*</i> publica la imagen en GitHub Container "
      "Registry con el token integrado, sin secretos manuales. La documentación incluye un README con badges y una Wiki de cinco páginas."),
]
fila = [captura("01_compose.png", "Fig. 2. Servicios healthy"),
        captura("02_api.png", "Fig. 3. API respondiendo"),
        captura("03_actions.png", "Fig. 4. Pipeline en verde")]
t = Table([[c[0] for c in fila], [c[1] for c in fila]], colWidths=[5.6 * cm] * 3)
t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story += [KeepTogether([Paragraph("5. Evidencias", h1), t]), Spacer(1, 4),
          Paragraph("6. Conclusiones", h1),
          p("La contenerización garantiza que la aplicación se comporte igual en el equipo del desarrollador, en el "
            "runner de CI y en un servidor, y el pipeline convierte cada cambio en una verificación automática. "
            "Como mejora futura se proponen migraciones de base de datos y análisis de vulnerabilidades de la imagen.")]

doc = SimpleDocTemplate(SALIDA, pagesize=letter, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                        topMargin=2.5 * cm, bottomMargin=2.2 * cm, title="Informe técnico", author=AUTOR)
doc.build(story)
print("Generado:", SALIDA)

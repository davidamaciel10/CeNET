import os
import sys
import json
import copy
import base64
import tempfile
import webbrowser
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import customtkinter as ctk

# =========================
# CONFIGURACIÓN DE RUTAS
# =========================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_APP_PATH = os.path.join(ASSETS_DIR, "logo_app.png")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")

# =========================
# CONFIGURACIÓN VISUAL
# =========================
COLORS_DARK = {
    "bg_dark":      "#0f1117",
    "bg_card":      "#1a1d27",
    "bg_hover":     "#252836",
    "bg_input":     "#1e2130",
    "border":       "#2a2d3a",
    "text":         "#e4e4e7",
    "text_muted":   "#71717a",
    "accent":       "#6366f1",
    "accent_hover": "#818cf8",
    "success":      "#22c55e",
    "warning":      "#f59e0b",
    "danger":       "#ef4444",
    "info":         "#3b82f6",
    "gold":         "#d4a843",
    "navy":         "#1e2a4a",
    "white":        "#ffffff",
}

COLORS_LIGHT = {
    "bg_dark":      "#f2f2f7",
    "bg_card":      "#ffffff",
    "bg_hover":     "#e5e5ea",
    "bg_input":     "#ffffff",
    "border":       "#d1d1d6",
    "text":         "#1c1c1e",
    "text_muted":   "#8e8e93",
    "accent":       "#007aff",
    "accent_hover": "#0056b3",
    "success":      "#34c759",
    "warning":      "#ff9500",
    "danger":       "#ff3b30",
    "info":         "#5ac8fa",
    "gold":         "#d4a843",
    "navy":         "#1c3d5a",
    "white":        "#ffffff",
}

# Tuplas (light, dark) — CTk las maneja automáticamente
COLORS = {k: (COLORS_LIGHT[k], COLORS_DARK[k]) for k in COLORS_DARK}


def _c(key):
    """Color actual como string (para ttk / style que no aceptan tuplas)."""
    mode = ctk.get_appearance_mode()
    return COLORS_LIGHT[key] if mode == "Light" else COLORS_DARK[key]


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================
# INFO ESTÁTICA INTA
# =========================
_INTA_INFO_HTML = """\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;padding:24px 28px;
     color:#1e2a4a;line-height:1.7;font-size:0.95rem;}
h2{font-size:1.05rem;color:#1e2a4a;border-bottom:2px solid #45658d;
   padding-bottom:8px;margin-bottom:20px;}
dt{font-weight:700;color:#45658d;margin-top:14px;}
dd{margin:4px 0 0 0;color:#374151;}
</style>
</head>
<body>
<h2>Monitoreo ambiental de Agroecosistemas</h2>
<dl>
<dt>Opci\u00f3n pedag\u00f3gica</dt>
<dd>Virtual por la plataforma de INTA</dd>
<dt>Destinatarios</dt>
<dd>Docentes de nivel secundario de escuelas secundarias t\u00e9cnicas agropecuarias del ciclo b\u00e1sico.</dd>
<dt>Carga horaria</dt>
<dd>60 horas reloj distribuidas en 6 semanas. Durante el transcurso de estas semanas se realizar\u00e1n
actividades asincr\u00f3nicas y encuentros sincr\u00f3nicos.</dd>
<dt>S\u00edntesis</dt>
<dd>En este curso abordaremos una introducci\u00f3n al monitoreo ambiental en agroecosistemas desde un
enfoque sist\u00e9mico. Se brindar\u00e1n herramientas para acompa\u00f1ar a los docentes en el desarrollo de un
plan de monitoreo ambiental para la formaci\u00f3n de los t\u00e9cnicos agropecuarios del futuro. Abordaremos
los beneficios que ofrece la biodiversidad a la producci\u00f3n de alimentos y los distintos indicadores
ambientales que se pueden monitorear describiendo t\u00e9cnicas simples de relevamiento de invertebrados
ben\u00e9ficos, anfibios, aves y mam\u00edferos.</dd>
</dl>
</body>
</html>
"""

# =========================
# PRECARGA 2026
# =========================
CURSOS_2026 = [
    # ── Innovación y entornos digitales ──
    {
        "titulo":    "Buenas Prácticas en el uso de la información",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/BUENAS%20PR%C3%81CTICAS.jpeg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=4063",
    },
    {
        "titulo":    "Ciudadanía Digital",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/CIUDADAN%C3%8DA.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6121",
    },
    {
        "titulo":    "Creación de Aulas Virtuales y Aplicación de Simuladores en la Enseñanza Técnica",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/creaci%C3%B3n%20de%20aulas%20virtuales.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19374",
    },
    {
        "titulo":    "Formación Emprendedora en la ETP",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Formaci%C3%B3n%20emprendedora%20en%20la%20ETP%20%283%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=3816",
    },
    {
        "titulo":    "Introducción a la programación con Python",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Introducci%C3%B3n%20a%20la%20programaci%C3%B3n%20con%20Python.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19071",
    },
    {
        "titulo":    "Análisis de datos en la educación técnica profesional: Herramientas y actividades",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51558/mod_page/content/140/An%C3%A1lisis%20de%20datos%20en%20la%20educaci%C3%B3n%20t%C3%A9cnica%C2%A0%20profesional%20Herramientas%20y%20actividades.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19069",
    },
    {
        "titulo":    "Inteligencia artificial generativa y educación",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Inteligencia%20Artificial%20Generativa%20y%20educaci%C3%B3n%20%282%29.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=4102",
    },
    {
        "titulo":    "Proyectos de Machine Learning en la escuela Asociación Chicos.Net",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/MACHINE.jpeg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6127",
    },
    {
        "titulo":    "Educar en tiempos de IA. Alfabetización y ciudadanía digital en la escuela",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/thumbnail_chicosnet%20%281%29%20%281%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=11974",
    },
    {
        "titulo":    "Aprender a comunicarse con la IA. Guía básica para la escritura de prompts",
        "categoria": "Innovación y entornos digitales",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/IA.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=15579",
    },
    {
        "titulo":    "Fundamentos técnicos funcionales de los sistemas embebidos aplicados a internet de las cosas (IoT)",
        "categoria": "Innovación y entornos digitales",
        "img":       "",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=28613",
    },
    {
        "titulo":    "STEM y Robótica en la ETP",
        "categoria": "Innovación y entornos digitales",
        "img":       "",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=30494",
    },
    # ── Estrategias pedagógicas para la ETP ──
    {
        "titulo":    "Inclusión educativa de estudiantes con discapacidad en la ETP",
        "categoria": "Estrategias pedagógicas para la ETP",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/INCLUSI%C3%93N%20%282%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=1217",
    },
    {
        "titulo":    "Convivencia en las instituciones educativas de la ETP",
        "categoria": "Estrategias pedagógicas para la ETP",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Convivencia%20en%20las%20instituciones%20educativas%20de%20la%20ETP.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19065",
    },
    {
        "titulo":    "La comunicación de proyectos en las Escuelas Técnicas",
        "categoria": "Estrategias pedagógicas para la ETP",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/La%20comunicaci%C3%B3n%20de%20proyectos%20en%20las%20Escuelas%20T%C3%A9cnicas%20%281%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19066",
    },
    {
        "titulo":    "El Proyecto Tecnológico",
        "categoria": "Estrategias pedagógicas para la ETP",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/EL%20PROYECTO.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6123",
    },
    {
        "titulo":    "Herramientas metodológicas para la formación emprendedora en la ETP",
        "categoria": "Estrategias pedagógicas para la ETP",
        "img":       "",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=29113",
    },
    # ── Seguridad institucional ──
    {
        "titulo":    "Modelo 5S para la gestión de prevención, higiene y salud en la ETP",
        "categoria": "Seguridad institucional",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/5S%20%283%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=2422",
    },
    {
        "titulo":    "Prevención, higiene y salud laboral en instituciones educativas de la ETP",
        "categoria": "Seguridad institucional",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Prevenci%C3%B3n%2C%20higiene%20y%20salud%20laboral%20en%20instituciones%20de%20ETP%20%283%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=1220",
    },
    {
        "titulo":    "Gestión de riesgos y su prevención en las instituciones de ETP",
        "categoria": "Seguridad institucional",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Gesti%C3%B3n%20de%20riesgos%20y%20su%20prevenci%C3%B3n%20en%20las%20instituciones%20de%20ETP%20%282%29.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19068",
    },
    # ── Diseño, Producción y Especializaciones Técnicas ──
    {
        "titulo":    "Cultivos bajo cubierta: Diversas alternativas de protección",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Cultivos%20bajo%20cubierta%20Diversas%20alternativas%20de%20protecci%C3%B3n%20%282%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19067",
    },
    {
        "titulo":    "Diseño y modelado 3D con software paramétrico (SOLIDEDGE)",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/SolidEdge%20%284%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=4120",
    },
    {
        "titulo":    "Herramientas digitales aplicadas al dibujo técnico (CAD-2D)",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Herramientas%20digitales%20aplicadas%20al%20dibujo%20t%C3%A9cnico%20%28CAD%20-%202D%29%20%283%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=4064",
    },
    {
        "titulo":    "Técnicas sustentables en impresión 3D",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/3D%20a%20%282%29.jpeg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6128",
    },
    {
        "titulo":    "Introducción a la metodología BIM",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/23423/mod_page/content/140/INTRO%20A%20BIM%20%282%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6125",
    },
    {
        "titulo":    "Construcciones sustentables",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/23423/mod_page/content/140/WhatsApp%20Image%202025-04-28%20at%2015.29.37.jpeg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=9344",
    },
    {
        "titulo":    "Introducción a la automatización industrial",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/INTRO%20A%20LA%20AUTOMATIZACION%20%282%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6124",
    },
    {
        "titulo":    "CADe SIMU: Diseño y Simulación de Circuitos Eléctricos para la Enseñanza Técnica",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/CADe%20SIMU%20Dise%C3%B1o%20y%20Simulaci%C3%B3n%20de%20Circuitos%20El%C3%A9ctricos%20para%20la%20Ense%C3%B1anza%20T%C3%A9cnica%20%281%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=19070",
    },
    {
        "titulo":    "Principios de la hidráulica para la formación técnica",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Principios%20de%20la%20hidr%C3%A1ulica%20para%20la%20formaci%C3%B3n%20t%C3%A9cnica.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=8496",
    },
    {
        "titulo":    "Tecnología neumática",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Tecnolog%C3%ADa%20Neum%C3%A1tica%20%283%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=4121",
    },
    {
        "titulo":    "Electroneumática I. Estructura y componentes de circuitos electrónicos",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/23423/mod_page/content/140/Electroneum%C3%A1tica.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=15578",
    },
    {
        "titulo":    "Electroneumática II. Diseño, análisis y resolución de circuitos electroneumáticos",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=28614",
    },
    {
        "titulo":    "Eficiencia energética en el dominio Industrial y Domiciliario",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Eficiencia%20energ%C3%A9tica%20%282%29.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=6122",
    },
    {
        "titulo":    "Diseño avanzado 3D con sólidos paramétricos (Autodesk Inventor)",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51556/mod_page/content/140/Dise%C3%B1o%20avanzado%203D%20con%20solidos%20parametricos%20%28autodesk%20inventor%29%20%281%29.jpg",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=8263",
    },
    {
        "titulo":    "Introducción a la programación CNC para torno en 2 ejes",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/23423/mod_page/content/140/Programaci%C3%B3n%20de%20tornos.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=15580",
    },
    {
        "titulo":    "Instalaciones de paneles solares",
        "categoria": "Diseño, Producción y Especializaciones Técnicas",
        "img":       "https://cenet.inet.edu.ar/pluginfile.php/51558/mod_page/content/153/paneles%20solares.png",
        "info":      "https://cenet.inet.edu.ar/mod/page/view.php?id=24928",
    },
    {
        "titulo":       "Monitoreo ambiental de Agroecosistemas",
        "categoria":    "Diseño, Producción y Especializaciones Técnicas",
        "img":          "",
        "info":         "",
        "info_texto":   _INTA_INFO_HTML,
        "form_externo": "https://formacion.inta.gob.ar/cenet2026-monitoreo/",
    },
]


# =========================
# APLICACIÓN PRINCIPAL
# =========================
class GeneradorMoodle(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Generador de Catálogo CeNET v2.0")

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        ww = max(1200, int(sw * 0.82))
        wh = max(780, int(sh * 0.88))
        self.geometry(f"{ww}x{wh}")
        self.minsize(1100, 720)
        self.configure(fg_color=COLORS["bg_dark"])

        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                pass

        # Estado interno
        self._current_theme      = "dark"
        self._banco_edit_idx     = None
        self._hay_cambios        = False
        self._preview_html_cache = ""
        self._use_htmlframe      = False

        self.banco_cursos = []

        self.categorias_sugeridas = [
            "Innovación y entornos digitales",
            "Estrategias pedagógicas para la ETP",
            "Seguridad institucional",
            "Diseño, Producción y Especializaciones Técnicas",
        ]

        # Variables generales
        self.titulo_oferta_var = tk.StringVar(value="Oferta Formativa CeNET 2026")

        # Cohorte única
        self.cohorte = {"nombre": "2° cohorte", "link": "", "estado": "Inscripción ABIERTA", "cursos": []}
        self.coh_nombre_var = tk.StringVar(value=self.cohorte["nombre"])
        self.coh_estado_var = tk.StringVar(value=self.cohorte["estado"])
        self.coh_link_var   = tk.StringVar(value=self.cohorte["link"])

        # Variables formulario banco
        self.tit_var           = tk.StringVar()
        self.cat_var           = tk.StringVar()
        self.img_var           = tk.StringVar()
        self.desc_var          = tk.StringVar()
        self.inf_var           = tk.StringVar()
        self.ext_var           = tk.StringVar()
        self._cat_nueva_var    = tk.StringVar()
        self._banco_filtro_var = tk.StringVar()

        # Modo de generación HTML
        self._modo_html        = tk.StringVar(value="moodle")

        self._setup_ttk_theme()
        self._build_ui()

        # Auto-guardar cambios del editor de cohorte
        self.coh_nombre_var.trace_add("write", self._save_coh_edit)
        self.coh_estado_var.trace_add("write", self._save_coh_edit)
        self.coh_link_var.trace_add("write",   self._save_coh_edit)

    # ─────────────────────────────────────────
    # INDICADOR DE CAMBIOS
    # ─────────────────────────────────────────
    def _marcar_cambio(self, *_):
        """Marca que hay cambios sin guardar."""
        if not self._hay_cambios:
            self._hay_cambios = True
            self.title("Generador de Catálogo CeNET v2.0 ●")

    def _limpiar_cambio(self):
        """Limpia el indicador de cambios."""
        self._hay_cambios = False
        self.title("Generador de Catálogo CeNET v2.0")

    def _on_close(self):
        if self._hay_cambios:
            if messagebox.askyesno("Cambios sin guardar",
                "Hay cambios sin guardar. ¿Cerrar de todas formas?", parent=self):
                self.destroy()
        else:
            self.destroy()

    # ─────────────────────────────────────────
    # HELPERS DE WIDGETS
    # ─────────────────────────────────────────
    def _btn(self, parent, text, command, color="accent",
             width=None, height=38, **kw):
        color_map = {
            "accent":  (COLORS["accent"],  COLORS["accent_hover"]),
            "success": (COLORS["success"], ("#16a34a", "#15803d")),
            "danger":  (COLORS["danger"],  ("#dc2626", "#b91c1c")),
            "warning": (COLORS["warning"], ("#d97706", "#b45309")),
            "info":    (COLORS["info"],    ("#2563eb", "#1d4ed8")),
            "navy":    (COLORS["navy"],    ("#253560", "#1a2540")),
            "gold":    (COLORS["gold"],    ("#b8922e", "#9a7a26")),
            "ghost":   ("transparent",     COLORS["bg_hover"]),
        }
        fg, hover = color_map.get(color, (COLORS["accent"], COLORS["accent_hover"]))
        text_c = kw.pop("text_color",
                         COLORS["white"] if color != "ghost" else COLORS["text"])
        opts = dict(
            text=text, command=command,
            fg_color=fg, hover_color=hover,
            height=height, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=text_c,
        )
        if width is not None:
            opts["width"] = width
        if color == "ghost":
            opts["border_width"] = 1
            opts["border_color"] = COLORS["border"]
        opts.update(kw)
        return ctk.CTkButton(parent, **opts)

    def _label(self, parent, text="", size=12, bold=False,
               muted=False, **kw):
        font  = ctk.CTkFont(family="Segoe UI", size=size,
                            weight="bold" if bold else "normal")
        color = COLORS["text_muted"] if muted else COLORS["text"]
        return ctk.CTkLabel(
            parent, text=text, font=font,
            text_color=kw.pop("text_color", color), **kw
        )

    def _entry(self, parent, textvariable=None, width=200,
               placeholder="", **kw):
        return ctk.CTkEntry(
            parent, textvariable=textvariable, width=width, height=34,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            placeholder_text=placeholder, **kw
        )

    def _card(self, parent, title=None, title_color=None, **kw):
        frame = ctk.CTkFrame(
            parent, corner_radius=10, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg_card"], **kw
        )
        if title:
            tc = title_color or COLORS["text"]
            self._label(frame, title, size=14, bold=True,
                        text_color=tc).pack(anchor="w", padx=14, pady=(10, 4))
        return frame

    # ─────────────────────────────────────────
    # CONSTRUCCIÓN DE LA UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_body()
        self._build_footer()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self):
        hdr = ctk.CTkFrame(self, height=72, corner_radius=0,
                           fg_color=COLORS["navy"])
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        try:
            if os.path.exists(LOGO_APP_PATH):
                from PIL import Image
                img = Image.open(LOGO_APP_PATH)
                img.thumbnail((380, 56), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(
                    light_image=img, dark_image=img,
                    size=(img.width, img.height)
                )
                ctk.CTkLabel(hdr, image=logo_ctk, text="").pack(
                    side="left", padx=20, pady=8)
            else:
                raise FileNotFoundError
        except Exception:
            ctk.CTkLabel(
                hdr, text="GENERADOR DE CATÁLOGO CeNET",
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color=COLORS["white"]
            ).pack(side="left", padx=20)

        self.btn_theme = ctk.CTkButton(
            hdr, text="☀", width=36, height=36, corner_radius=18,
            fg_color="transparent", hover_color=COLORS["bg_hover"],
            text_color=COLORS["white"], font=ctk.CTkFont(size=16),
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="right", padx=(0, 16))

        ctk.CTkLabel(
            hdr, text="v2.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right", padx=4)

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(8, 4))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(
            body,
            fg_color=COLORS["bg_dark"],
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_card"],
            segmented_button_unselected_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text"],
            corner_radius=10,
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tabview.add("📚  Banco de Cursos")
        self.tabview.add("🗓  Cohortes")
        self.tabview.add("🌐  Vista Previa")
        self.tabview.add("✏️  Editor HTML")

        self._build_tab_banco(self.tabview.tab("📚  Banco de Cursos"))
        self._build_tab_cohortes(self.tabview.tab("🗓  Cohortes"))
        self._build_tab_preview(self.tabview.tab("🌐  Vista Previa"))
        self._build_tab_editor(self.tabview.tab("✏️  Editor HTML"))

    # ─────────────────────────────────────────
    # TAB 1: BANCO DE CURSOS
    # ─────────────────────────────────────────
    def _build_tab_banco(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # Panel izquierdo
        left = ctk.CTkScrollableFrame(
            parent, width=320, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Card: Añadir al Banco
        card_form = self._card(left)
        card_form.pack(fill="x", pady=(0, 10))

        self.lbl_banco_form_title = self._label(
            card_form, "Añadir al Banco", size=14, bold=True)
        self.lbl_banco_form_title.pack(anchor="w", padx=14, pady=(10, 4))

        # Título
        self._label(card_form, "Título *", muted=False).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._entry(card_form, textvariable=self.tit_var, width=0,
                    placeholder="Nombre del curso").pack(
            fill="x", padx=14, pady=(0, 4))

        # Categoría ComboBox
        self._label(card_form, "Categoría *", muted=False).pack(
            anchor="w", padx=14, pady=(6, 1))
        self.cat_combo = ctk.CTkComboBox(
            card_form,
            variable=self.cat_var,
            values=self.categorias_sugeridas,
            width=200, height=34,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_hover"],
            dropdown_text_color=COLORS["text"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.cat_combo.pack(fill="x", padx=14, pady=(0, 4))

        # URL Imagen
        self._label(card_form, "URL Imagen  (solo Moodle/CeNET)", muted=True).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._entry(card_form, textvariable=self.img_var, width=0,
                    placeholder="https://...  (vacío = sin imagen)").pack(
            fill="x", padx=14, pady=(0, 4))

        # Descripción corta (para INET)
        self._label(card_form, "Descripción corta  (para INET)", muted=True).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._entry(card_form, textvariable=self.desc_var, width=0,
                    placeholder="Breve descripción del curso...").pack(
            fill="x", padx=14, pady=(0, 4))

        # URL Más Info
        self._label(card_form, "URL Más Info", muted=True).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._entry(card_form, textvariable=self.inf_var, width=0,
                    placeholder="https://...").pack(
            fill="x", padx=14, pady=(0, 4))

        # Formulario externo
        self._label(card_form, "Formulario externo", muted=True).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._label(
            card_form,
            "Si se completa, el botón Inscribirme usa este enlace en vez del de la cohorte.",
            size=10, muted=True
        ).pack(anchor="w", padx=14)
        self._entry(card_form, textvariable=self.ext_var, width=0,
                    placeholder="https://  (dejar vacío si usa el formulario general)").pack(
            fill="x", padx=14, pady=(2, 4))

        btn_row = ctk.CTkFrame(card_form, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(6, 12))

        self.btn_banco_guardar = self._btn(
            btn_row, "➕  Agregar", self._banco_agregar_o_guardar,
            color="success", height=36
        )
        self.btn_banco_guardar.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_banco_cancelar = self._btn(
            btn_row, "Cancelar", self._banco_cancelar,
            color="ghost", height=36
        )
        self.btn_banco_cancelar.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.btn_banco_cancelar.pack_forget()

        # Card: Categorías Sugeridas
        card_cats = self._card(left, "Categorías Sugeridas")
        card_cats.pack(fill="x", pady=(0, 4))

        add_row = ctk.CTkFrame(card_cats, fg_color="transparent")
        add_row.pack(fill="x", padx=12, pady=(6, 4))
        self._entry(add_row, textvariable=self._cat_nueva_var,
                    width=0, placeholder="Nueva categoría...").pack(
            side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(add_row, "＋", self._add_categoria,
                  color="success", width=38, height=34).pack(side="left")

        self._cats_list_frame = ctk.CTkFrame(card_cats, fg_color="transparent")
        self._cats_list_frame.pack(fill="x")
        self._refresh_cats_panel()

        ctk.CTkFrame(card_cats, height=8, fg_color="transparent").pack()

        # Panel derecho
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Barra de acción
        abar = ctk.CTkFrame(right, fg_color="transparent", height=44)
        abar.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        abar.grid_propagate(False)

        self._label(abar, "Banco de Cursos", size=14, bold=True).pack(
            side="left", padx=4)
        self.lbl_banco_count = self._label(abar, "0 cursos", size=11, muted=True)
        self.lbl_banco_count.pack(side="left", padx=8)

        self._btn(abar, "Eliminar", self._banco_eliminar,
                  color="danger", height=32, width=100).pack(side="right", padx=(4, 0))
        self._btn(abar, "✏  Editar", self._banco_editar,
                  color="warning", height=32, width=110).pack(side="right", padx=4)
        self._btn(abar, "📋", self._banco_duplicar,
                  color="ghost", height=32, width=42).pack(side="right", padx=2)
        self._btn(abar, "▼", self._banco_bajar,
                  color="ghost", height=32, width=42).pack(side="right", padx=2)
        self._btn(abar, "▲", self._banco_subir,
                  color="ghost", height=32, width=42).pack(side="right", padx=2)

        # Barra de búsqueda
        filtro_frame = ctk.CTkFrame(right, fg_color="transparent")
        filtro_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self._entry(filtro_frame, textvariable=self._banco_filtro_var, width=0,
                    placeholder="🔍  Filtrar banco por título o categoría...").pack(fill="x")
        self._banco_filtro_var.trace_add("write", lambda *_: self._refresh_banco_tree())

        # Treeview banco
        tree_frame = ctk.CTkFrame(
            right, fg_color=COLORS["bg_card"],
            corner_radius=10, border_width=1,
            border_color=COLORS["border"]
        )
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("Titulo", "Categoria", "Descripcion", "Imagen", "Info", "Externo")
        self.banco_tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            style="Dark.Treeview", selectmode="browse"
        )
        for col, w, lbl in [
            ("Titulo",      240, "Título"),
            ("Categoria",   160, "Categoría"),
            ("Descripcion", 200, "Descripción"),
            ("Imagen",      140, "URL Imagen"),
            ("Info",        140, "URL Info"),
            ("Externo",     120, "Form. externo"),
        ]:
            self.banco_tree.heading(col, text=lbl)
            self.banco_tree.column(col, width=w, minwidth=60)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.banco_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.banco_tree.xview)
        self.banco_tree.configure(yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set)

        self.banco_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        hsb.grid(row=1, column=0, sticky="ew", padx=6)

        self.banco_tree.bind("<Double-1>", lambda _: self._banco_editar())

    # ─────────────────────────────────────────
    # TAB 2: COHORTES
    # ─────────────────────────────────────────
    def _build_tab_cohortes(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # Panel izquierdo
        left = ctk.CTkScrollableFrame(
            parent, width=260, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Card: Configuración de Cohortes
        card_cfg = self._card(left, "Configuración de Cohortes",
                              title_color=COLORS["gold"])
        card_cfg.pack(fill="x", pady=(0, 10))

        self._label(card_cfg, "Título de la Oferta", muted=True).pack(
            anchor="w", padx=14, pady=(6, 1))
        self._entry(card_cfg, textvariable=self.titulo_oferta_var, width=0,
                    placeholder="Ej: Oferta Formativa CeNET 2026").pack(
            fill="x", padx=14, pady=(0, 8))

        ctk.CTkFrame(card_cfg, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=14, pady=(0, 6))

        for lbl, var, ph in [
            ("Nombre de la cohorte", self.coh_nombre_var, "Ej: 2° cohorte"),
            ("Estado",               self.coh_estado_var, "Ej: Inscripción ABIERTA"),
            ("Link Inscripción",     self.coh_link_var,   "https://forms.office.com/..."),
        ]:
            self._label(card_cfg, lbl, muted=True).pack(
                anchor="w", padx=14, pady=(4, 1))
            self._entry(card_cfg, textvariable=var, width=0,
                        placeholder=ph).pack(fill="x", padx=14, pady=(0, 2))

        ctk.CTkFrame(card_cfg, height=8, fg_color="transparent").pack()

        # Panel derecho: grid con 2 rows
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=3)
        right.grid_rowconfigure(1, weight=2)
        right.grid_columnconfigure(0, weight=1)

        # Top: Cursos en esta cohorte
        top_frame = ctk.CTkFrame(
            right, corner_radius=10, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg_card"]
        )
        top_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        top_frame.grid_rowconfigure(1, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)

        # Barra top
        top_bar = ctk.CTkFrame(top_frame, fg_color="transparent", height=44)
        top_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        top_bar.grid_propagate(False)

        self._label(top_bar, "Cursos en esta cohorte", size=13, bold=True).pack(
            side="left", padx=4)
        self.lbl_coh_count = self._label(top_bar, "0", size=11, muted=True)
        self.lbl_coh_count.pack(side="left", padx=4)

        self._btn(top_bar, "Quitar", self._coh_quitar_curso,
                  color="danger", height=28, width=80).pack(side="right", padx=(2, 4))
        self._btn(top_bar, "▼", self._coh_bajar,
                  color="ghost", height=28, width=36).pack(side="right", padx=2)
        self._btn(top_bar, "▲", self._coh_subir,
                  color="ghost", height=28, width=36).pack(side="right", padx=2)
        self._btn(top_bar, "⭐", lambda: self._coh_set_etiqueta("Destacado"),
                  color="gold", height=28, width=36).pack(side="right", padx=2)
        self._btn(top_bar, "🆕", lambda: self._coh_set_etiqueta("Nuevo"),
                  color="success", height=28, width=36).pack(side="right", padx=2)
        self._btn(top_bar, "—", lambda: self._coh_set_etiqueta(""),
                  color="ghost", height=28, width=36).pack(side="right", padx=2)

        # Treeview cohorte
        coh_tree_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        coh_tree_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        coh_tree_frame.grid_rowconfigure(0, weight=1)
        coh_tree_frame.grid_columnconfigure(0, weight=1)

        coh_cols = ("Titulo", "Categoria", "Etiqueta")
        self.coh_tree = ttk.Treeview(
            coh_tree_frame, columns=coh_cols, show="headings",
            style="Dark.Treeview", selectmode="browse"
        )
        for col, w, lbl in [
            ("Titulo",    300, "Título"),
            ("Categoria", 200, "Categoría"),
            ("Etiqueta",  100, "Etiqueta"),
        ]:
            self.coh_tree.heading(col, text=lbl)
            self.coh_tree.column(col, width=w, minwidth=60)

        coh_vsb = ttk.Scrollbar(coh_tree_frame, orient="vertical",
                                 command=self.coh_tree.yview)
        self.coh_tree.configure(yscrollcommand=coh_vsb.set)
        self.coh_tree.grid(row=0, column=0, sticky="nsew")
        coh_vsb.grid(row=0, column=1, sticky="ns")

        # Bottom: Banco disponible
        bot_frame = ctk.CTkFrame(
            right, corner_radius=10, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg_card"]
        )
        bot_frame.grid(row=1, column=0, sticky="nsew")
        bot_frame.grid_rowconfigure(1, weight=1)
        bot_frame.grid_columnconfigure(0, weight=1)

        bot_header = ctk.CTkFrame(bot_frame, fg_color="transparent", height=38)
        bot_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        bot_header.grid_propagate(False)

        self._label(bot_header, "Banco disponible", size=13, bold=True).pack(
            side="left", padx=4)
        self.lbl_banco_disp_count = self._label(bot_header, "0", size=11, muted=True)
        self.lbl_banco_disp_count.pack(side="left", padx=4)
        self._label(bot_header, "☑ Tildar para agregar", size=11, muted=True).pack(
            side="right", padx=8)

        self._banco_disp_frame = ctk.CTkScrollableFrame(
            bot_frame, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self._banco_disp_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

    # ─────────────────────────────────────────
    # TAB 3: VISTA PREVIA HTML
    # ─────────────────────────────────────────
    def _build_tab_preview(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Barra de herramientas
        toolbar = ctk.CTkFrame(parent, fg_color="transparent", height=52)
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        toolbar.grid_propagate(False)

        self._btn(toolbar, "🔄  Actualizar vista", self._preview_actualizar,
                  color="accent", height=36).pack(side="left", padx=(0, 8))
        self._btn(toolbar, "🌐  Abrir en navegador", self._preview_abrir_navegador,
                  color="ghost", height=36).pack(side="left", padx=(0, 8))

        ctk.CTkFrame(toolbar, width=2, height=28, fg_color=COLORS["border"]).pack(
            side="left", padx=10)
        self._label(toolbar, "Modo:", muted=True).pack(side="left", padx=(0, 4))
        ctk.CTkRadioButton(
            toolbar, text="CeNET (Moodle)", variable=self._modo_html, value="moodle",
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text"], font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkRadioButton(
            toolbar, text="INET", variable=self._modo_html, value="inet",
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text"], font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(side="left", padx=(0, 8))

        self.lbl_preview_status = self._label(
            toolbar, "Presioná «Actualizar vista» para generar la vista previa.", muted=True)
        self.lbl_preview_status.pack(side="left", padx=8)

        # Área de previsualización
        preview_container = ctk.CTkFrame(
            parent, corner_radius=10, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg_card"]
        )
        preview_container.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        try:
            from tkinterweb import HtmlFrame
            self._html_frame = HtmlFrame(preview_container, messages_enabled=False)
            self._html_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
            self._use_htmlframe = True
        except ImportError:
            self._use_htmlframe = False
            ctk.CTkLabel(
                preview_container,
                text=(
                    "Para previsualización integrada instalá:\n"
                    "pip install tkinterweb\n\n"
                    "O usá «Abrir en navegador» para ver el HTML en tu browser."
                ),
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_muted"],
                justify="center",
            ).grid(row=0, column=0)

    # ─────────────────────────────────────────
    # TAB 4: EDITOR DE CÓDIGO HTML
    # ─────────────────────────────────────────
    def _build_tab_editor(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Barra de herramientas
        toolbar = ctk.CTkFrame(parent, fg_color="transparent", height=52)
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        toolbar.grid_propagate(False)

        self._btn(toolbar, "🔄  Regenerar", self._editor_regenerar,
                  color="accent", height=36).pack(side="left", padx=(0, 8))
        self._btn(toolbar, "📋  Copiar", self._editor_copiar,
                  color="ghost", height=36).pack(side="left", padx=(0, 8))
        self._btn(toolbar, "💾  Guardar", self._editor_guardar,
                  color="ghost", height=36).pack(side="left", padx=(0, 8))

        self.lbl_editor_status = self._label(
            toolbar, "Presioná «Regenerar» para cargar el HTML generado.", muted=True)
        self.lbl_editor_status.pack(side="left", padx=8)

        # Marco del editor
        editor_frame = ctk.CTkFrame(
            parent, corner_radius=10, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg_card"]
        )
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(0, weight=1)

        self.editor_text = tk.Text(
            editor_frame,
            wrap="none",
            bg=_c("bg_card"),
            fg=_c("text"),
            insertbackground=_c("text"),
            selectbackground=_c("accent"),
            font=("Consolas", 11),
            borderwidth=0,
            relief="flat",
            padx=12,
            pady=8,
            undo=True,
        )
        vsb = ttk.Scrollbar(editor_frame, orient="vertical",
                            command=self.editor_text.yview)
        hsb = ttk.Scrollbar(editor_frame, orient="horizontal",
                            command=self.editor_text.xview)
        self.editor_text.configure(
            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.editor_text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

    def _build_footer(self):
        footer = ctk.CTkFrame(
            self, height=64, corner_radius=0,
            fg_color=COLORS["bg_card"], border_width=1,
            border_color=COLORS["border"]
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)

        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(expand=True, pady=12)

        self._btn(inner, "⚡  Precargar banco 2026",
                  self._precargar_2026, color="navy", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "📋  Copiar banco → cohorte",
                  self._copiar_banco_a_cohorte, color="ghost", height=38).pack(
            side="left", padx=4)

        sep0 = ctk.CTkFrame(inner, width=2, height=36,
                            fg_color=COLORS["border"])
        sep0.pack(side="left", padx=14)

        self._btn(inner, "💾  Guardar Proyecto",
                  self._guardar_proyecto, color="ghost", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "📂  Cargar Proyecto",
                  self._cargar_proyecto, color="ghost", height=38).pack(
            side="left", padx=6)

        sep1 = ctk.CTkFrame(inner, width=2, height=36,
                            fg_color=COLORS["border"])
        sep1.pack(side="left", padx=14)

        self._btn(inner, "🌐  Moodle/CeNET",
                  lambda: self.exportar_html("moodle"), color="success", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "📋  Copiar CeNET",
                  lambda: self._copiar_html_clipboard("moodle"), color="ghost", height=38).pack(
            side="left", padx=4)

        sep2 = ctk.CTkFrame(inner, width=2, height=36, fg_color=COLORS["border"])
        sep2.pack(side="left", padx=14)

        self._btn(inner, "🏛️  INET",
                  lambda: self.exportar_html("inet"), color="info", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "📋  Copiar INET",
                  lambda: self._copiar_html_clipboard("inet"), color="ghost", height=38).pack(
            side="left", padx=4)

    # ─────────────────────────────────────────
    # CATEGORÍAS DINÁMICAS
    # ─────────────────────────────────────────
    def _refresh_cats_panel(self):
        for w in self._cats_list_frame.winfo_children():
            w.destroy()
        for cat in self.categorias_sugeridas:
            row = ctk.CTkFrame(self._cats_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            self._btn(
                row, cat, lambda c=cat: self.cat_var.set(c),
                color="ghost", height=28,
                font=ctk.CTkFont(family="Segoe UI", size=11)
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))
            self._btn(
                row, "×", lambda c=cat: self._del_categoria(c),
                color="danger", width=28, height=28,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            ).pack(side="left")
        if hasattr(self, "cat_combo"):
            self.cat_combo.configure(values=self.categorias_sugeridas)

    def _add_categoria(self):
        nueva = self._cat_nueva_var.get().strip()
        if not nueva:
            return
        if nueva not in self.categorias_sugeridas:
            self.categorias_sugeridas.append(nueva)
            self._refresh_cats_panel()
        self._cat_nueva_var.set("")

    def _del_categoria(self, cat):
        if cat in self.categorias_sugeridas:
            self.categorias_sugeridas.remove(cat)
            self._refresh_cats_panel()

    # ─────────────────────────────────────────
    # MÉTODOS DEL BANCO (Tab 1)
    # ─────────────────────────────────────────
    def _banco_sel_idx(self):
        """Índice seleccionado en banco_tree, o None."""
        sel = self.banco_tree.selection()
        if not sel:
            return None
        tags = self.banco_tree.item(sel[0], "tags")
        return int(tags[0]) if tags else None

    def _refresh_banco_tree(self):
        """Refresca banco_tree y lbl_banco_count."""
        for item in self.banco_tree.get_children():
            self.banco_tree.delete(item)
        filtro = getattr(self, '_banco_filtro_var', None)
        filtro_txt = filtro.get().lower().strip() if filtro else ""
        for i, c in enumerate(self.banco_cursos):
            if filtro_txt:
                haystack = f"{c.get('titulo','').lower()} {c.get('categoria','').lower()}"
                if filtro_txt not in haystack:
                    continue
            ext = c.get("form_externo", "")
            desc = c.get("descripcion", "")
            self.banco_tree.insert("", "end", tags=(str(i),), values=(
                c.get("titulo", ""),
                c.get("categoria", ""),
                desc[:60] + ("…" if len(desc) > 60 else "") if desc else "",
                c.get("img", ""),
                c.get("info", ""),
                ext if ext else "",
            ))
        n = len(self.banco_cursos)
        self.lbl_banco_count.configure(
            text=f"{n} curso{'s' if n != 1 else ''} en el banco")

    def _banco_agregar_o_guardar(self):
        """Agrega al banco o guarda edición."""
        titulo = self.tit_var.get().strip()
        if not titulo:
            messagebox.showwarning(
                "Atención", "El título es obligatorio.", parent=self)
            return
        ext = self.ext_var.get().strip()
        desc = self.desc_var.get().strip()
        curso = {
            "titulo":    titulo,
            "categoria": self.cat_var.get().strip() or "Sin categoría",
            "img":       self.img_var.get().strip(),
            "descripcion": desc,
            "info":      self.inf_var.get().strip(),
        }
        if ext:
            curso["form_externo"] = ext
        if self._banco_edit_idx is not None:
            # Al editar, actualizar banco_cursos y actualizar referencias en cohortes
            self.banco_cursos[self._banco_edit_idx] = curso
            self._banco_edit_idx = None
            self.lbl_banco_form_title.configure(text="Añadir al Banco")
            self.btn_banco_guardar.configure(
                text="➕  Agregar",
                fg_color=COLORS["success"],
                hover_color=("#16a34a", "#15803d")
            )
            self.btn_banco_cancelar.pack_forget()
        else:
            self.banco_cursos.append(curso)
        self._banco_limpiar_form()
        self._refresh_banco_tree()
        self._marcar_cambio()

    def _banco_editar(self):
        """Carga curso seleccionado al form para editar."""
        idx = self._banco_sel_idx()
        if idx is None:
            messagebox.showinfo("Info", "Seleccioná un curso para editar.", parent=self)
            return
        c = self.banco_cursos[idx]
        self.tit_var.set(c.get("titulo", ""))
        self.cat_var.set(c.get("categoria", ""))
        self.img_var.set(c.get("img", ""))
        self.desc_var.set(c.get("descripcion", ""))
        self.inf_var.set(c.get("info", ""))
        self.ext_var.set(c.get("form_externo", ""))
        self._banco_edit_idx = idx
        titulo_corto = c["titulo"][:28] + ("…" if len(c["titulo"]) > 28 else "")
        self.lbl_banco_form_title.configure(text=f"Editando: {titulo_corto}")
        self.btn_banco_guardar.configure(
            text="💾  Guardar Cambios",
            fg_color=COLORS["warning"],
            hover_color=("#d97706", "#b45309")
        )
        self.btn_banco_cancelar.pack(
            side="left", fill="x", expand=True, padx=(4, 0))

    def _banco_cancelar(self):
        """Cancela edición del banco."""
        self._banco_edit_idx = None
        self.lbl_banco_form_title.configure(text="Añadir al Banco")
        self.btn_banco_guardar.configure(
            text="➕  Agregar",
            fg_color=COLORS["success"],
            hover_color=("#16a34a", "#15803d")
        )
        self.btn_banco_cancelar.pack_forget()
        self._banco_limpiar_form()

    def _banco_eliminar(self):
        """Elimina del banco (con confirmación)."""
        idx = self._banco_sel_idx()
        if idx is None:
            messagebox.showinfo("Info", "Seleccioná un curso para eliminar.", parent=self)
            return
        nombre = self.banco_cursos[idx].get("titulo", "?")
        if not messagebox.askyesno(
                "Confirmar", f"¿Eliminar '{nombre}' del banco?\n"
                "Se eliminará también de las cohortes donde esté asignado.", parent=self):
            return
        del self.banco_cursos[idx]
        nuevos = []
        for entry in self.cohorte.get("cursos", []):
            bidx = entry.get("banco_idx", -1)
            if bidx == idx:
                continue
            if bidx > idx:
                entry = dict(entry)
                entry["banco_idx"] = bidx - 1
            nuevos.append(entry)
        self.cohorte["cursos"] = nuevos
        if self._banco_edit_idx == idx:
            self._banco_cancelar()
        self._refresh_banco_tree()
        self._refresh_cohorte_panel()
        self._marcar_cambio()

    def _banco_duplicar(self):
        """Duplica el curso seleccionado."""
        idx = self._banco_sel_idx()
        if idx is None:
            messagebox.showinfo("Info", "Seleccioná un curso para duplicar.", parent=self)
            return
        nuevo = copy.deepcopy(self.banco_cursos[idx])
        nuevo["titulo"] += " (copia)"
        self.banco_cursos.insert(idx + 1, nuevo)
        for entry in self.cohorte.get("cursos", []):
            if entry.get("banco_idx", -1) > idx:
                entry["banco_idx"] += 1
        self._refresh_banco_tree()
        self._marcar_cambio()
        # Seleccionar la copia
        for child in self.banco_tree.get_children():
            if self.banco_tree.item(child, "tags") == (str(idx + 1),):
                self.banco_tree.selection_set(child)
                break

    def _banco_subir(self):
        """Sube una posición en el banco."""
        idx = self._banco_sel_idx()
        if idx is None:
            return
        children = self.banco_tree.get_children()
        pos = None
        for i, ch in enumerate(children):
            if self.banco_tree.item(ch, "tags") == (str(idx),):
                pos = i
                break
        if pos is None or pos == 0:
            return
        prev_idx = int(self.banco_tree.item(children[pos - 1], "tags")[0])
        self.banco_cursos[idx], self.banco_cursos[prev_idx] = \
            self.banco_cursos[prev_idx], self.banco_cursos[idx]
        for entry in self.cohorte.get("cursos", []):
            bidx = entry.get("banco_idx", -1)
            if bidx == idx:
                entry["banco_idx"] = prev_idx
            elif bidx == prev_idx:
                entry["banco_idx"] = idx
        self._refresh_banco_tree()
        self._marcar_cambio()
        for child in self.banco_tree.get_children():
            if self.banco_tree.item(child, "tags") == (str(prev_idx),):
                self.banco_tree.selection_set(child)
                break

    def _banco_bajar(self):
        """Baja una posición en el banco."""
        idx = self._banco_sel_idx()
        if idx is None:
            return
        children = self.banco_tree.get_children()
        pos = None
        for i, ch in enumerate(children):
            if self.banco_tree.item(ch, "tags") == (str(idx),):
                pos = i
                break
        if pos is None or pos >= len(children) - 1:
            return
        next_idx = int(self.banco_tree.item(children[pos + 1], "tags")[0])
        self.banco_cursos[idx], self.banco_cursos[next_idx] = \
            self.banco_cursos[next_idx], self.banco_cursos[idx]
        for entry in self.cohorte.get("cursos", []):
            bidx = entry.get("banco_idx", -1)
            if bidx == idx:
                entry["banco_idx"] = next_idx
            elif bidx == next_idx:
                entry["banco_idx"] = idx
        self._refresh_banco_tree()
        self._marcar_cambio()
        for child in self.banco_tree.get_children():
            if self.banco_tree.item(child, "tags") == (str(next_idx),):
                self.banco_tree.selection_set(child)
                break

    def _banco_limpiar_form(self):
        """Limpia los campos del formulario del banco."""
        for v in (self.tit_var, self.cat_var, self.img_var, self.desc_var, self.inf_var, self.ext_var):
            v.set("")

    # ─────────────────────────────────────────
    # MÉTODOS DE COHORTE (Tab 2)
    # ─────────────────────────────────────────
    def _save_coh_edit(self, *_):
        self.cohorte["nombre"] = self.coh_nombre_var.get().strip() or self.cohorte["nombre"]
        self.cohorte["estado"] = self.coh_estado_var.get()
        self.cohorte["link"]   = self.coh_link_var.get()

    def _refresh_cohorte_panel(self):
        self._refresh_coh_tree()
        self._refresh_banco_disponible()

    def _refresh_coh_tree(self):
        for item in self.coh_tree.get_children():
            self.coh_tree.delete(item)
        n = 0
        for i, entry in enumerate(self.cohorte.get("cursos", [])):
            bidx = entry.get("banco_idx", -1)
            etiqueta = entry.get("etiqueta", "")
            if 0 <= bidx < len(self.banco_cursos):
                c = self.banco_cursos[bidx]
                self.coh_tree.insert("", "end", tags=(str(i),), values=(
                    c.get("titulo", ""),
                    c.get("categoria", ""),
                    etiqueta if etiqueta else "—",
                ))
                n += 1
        self.lbl_coh_count.configure(text=f"{n} curso{'s' if n != 1 else ''}")

    def _refresh_banco_disponible(self):
        for w in self._banco_disp_frame.winfo_children():
            w.destroy()
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        disponibles = [(bidx, c) for bidx, c in enumerate(self.banco_cursos) if bidx not in ya_en_coh]
        self.lbl_banco_disp_count.configure(
            text=f"{len(disponibles)} disponible{'s' if len(disponibles) != 1 else ''}")
        for bidx, c in disponibles:
            texto = f"{c.get('titulo','')}  [{c.get('categoria','')}]"
            cb = ctk.CTkCheckBox(
                self._banco_disp_frame, text=texto,
                command=lambda b=bidx: self._banco_toggle_add(b),
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                border_color=COLORS["border"], text_color=COLORS["text"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
                checkmark_color=COLORS["white"],
            )
            cb.pack(anchor="w", padx=8, pady=2)

    def _banco_toggle_add(self, banco_idx):
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        if banco_idx not in ya_en_coh:
            self.cohorte["cursos"].append({"banco_idx": banco_idx, "etiqueta": ""})
        self._refresh_cohorte_panel()
        self._marcar_cambio()

    def _coh_quitar_curso(self):
        pos = self._coh_sel_idx()
        if pos is None:
            messagebox.showinfo("Info", "Seleccioná un curso para quitar.", parent=self)
            return
        del self.cohorte["cursos"][pos]
        self._refresh_cohorte_panel()

    def _coh_set_etiqueta(self, etiqueta):
        pos = self._coh_sel_idx()
        if pos is None:
            return
        self.cohorte["cursos"][pos]["etiqueta"] = etiqueta
        self._refresh_coh_tree()

    def _coh_sel_idx(self):
        sel = self.coh_tree.selection()
        if not sel:
            return None
        tags = self.coh_tree.item(sel[0], "tags")
        return int(tags[0]) if tags else None

    def _coh_subir(self):
        pos = self._coh_sel_idx()
        if pos is None or pos == 0:
            return
        cursos = self.cohorte["cursos"]
        cursos[pos], cursos[pos - 1] = cursos[pos - 1], cursos[pos]
        self._refresh_coh_tree()
        for ch in self.coh_tree.get_children():
            if self.coh_tree.item(ch, "tags") == (str(pos - 1),):
                self.coh_tree.selection_set(ch)
                break

    def _coh_bajar(self):
        pos = self._coh_sel_idx()
        if pos is None:
            return
        cursos = self.cohorte["cursos"]
        if pos >= len(cursos) - 1:
            return
        cursos[pos], cursos[pos + 1] = cursos[pos + 1], cursos[pos]
        self._refresh_coh_tree()
        for ch in self.coh_tree.get_children():
            if self.coh_tree.item(ch, "tags") == (str(pos + 1),):
                self.coh_tree.selection_set(ch)
                break

    # ─────────────────────────────────────────
    # PRECARGA Y COPIA
    # ─────────────────────────────────────────
    def _precargar_2026(self):
        """Pregunta si hay cursos en banco y carga CURSOS_2026 al banco."""
        if self.banco_cursos:
            if not messagebox.askyesno(
                "Precarga 2026",
                f"Ya hay {len(self.banco_cursos)} curso(s) en el banco.\n"
                "¿Reemplazar con los 32 cursos de la oferta 2026?",
                parent=self
            ):
                return
        self.banco_cursos = [
            {
                "titulo":    c["titulo"],
                "categoria": c["categoria"],
                "img":       c["img"],
                "info":      c["info"],
            }
            for c in CURSOS_2026
        ]
        self._refresh_banco_tree()
        self._refresh_cohorte_panel()
        messagebox.showinfo(
            "Listo",
            f"32 cursos cargados al banco.",
            parent=self
        )

    def _copiar_banco_a_cohorte(self):
        """Agrega todos los cursos del banco a la cohorte (sin duplicar)."""
        if not self.banco_cursos:
            messagebox.showwarning(
                "Atención", "El banco está vacío. Primero agregá cursos al banco.",
                parent=self)
            return
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        agregados = 0
        for bidx in range(len(self.banco_cursos)):
            if bidx not in ya_en_coh:
                self.cohorte["cursos"].append({"banco_idx": bidx, "etiqueta": ""})
                agregados += 1
        self._refresh_cohorte_panel()
        messagebox.showinfo("Listo", f"Se agregaron {agregados} curso(s).", parent=self)

    # ─────────────────────────────────────────
    # PERSISTENCIA JSON
    # ─────────────────────────────────────────
    def _guardar_proyecto(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar Proyecto CeNET",
            parent=self
        )
        if not archivo:
            return
        self._save_coh_edit()
        data = {
            "titulo_oferta":        self.titulo_oferta_var.get(),
            "banco_cursos":         self.banco_cursos,
            "cohorte":              self.cohorte,
            "categorias_sugeridas": self.categorias_sugeridas,
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Éxito", "Proyecto guardado.", parent=self)

    def _cargar_proyecto(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar Proyecto CeNET",
            parent=self
        )
        if not archivo:
            return
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.titulo_oferta_var.set(
                data.get("titulo_oferta", data.get("cohorte", "")))

            self.banco_cursos = data.get("banco_cursos", [])
            loaded_coh = data.get("cohorte")
            if loaded_coh:
                self.cohorte = loaded_coh
                self.cohorte.setdefault("cursos", [])
                self.cohorte.setdefault("nombre", "")
                self.cohorte.setdefault("estado", "")
                self.cohorte.setdefault("link", "")
            else:
                self.cohorte = {"nombre": "", "link": "", "estado": "", "cursos": []}
            self.coh_nombre_var.set(self.cohorte["nombre"])
            self.coh_estado_var.set(self.cohorte["estado"])
            self.coh_link_var.set(self.cohorte["link"])

            loaded_cats = data.get("categorias_sugeridas")
            if loaded_cats and isinstance(loaded_cats, list):
                self.categorias_sugeridas = loaded_cats
                self._refresh_cats_panel()

            self._refresh_cohorte_panel()
            self._refresh_banco_tree()
            n = len(self.banco_cursos)
            messagebox.showinfo(
                "Éxito",
                f"Proyecto cargado: {n} curso{'s' if n!=1 else ''} en el banco.",
                parent=self)
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar el proyecto:\n{e}", parent=self)

    # ─────────────────────────────────────────
    # GENERACIÓN HTML
    # ─────────────────────────────────────────
    def exportar_html(self, modo="moodle"):
        self._save_coh_edit()
        if not self.banco_cursos:
            messagebox.showerror("Error", "No hay cursos en el banco.", parent=self)
            return
        if not self.cohorte.get("cursos"):
            messagebox.showwarning(
                "Atención",
                "La cohorte no tiene cursos asignados.\n"
                "Usá 'Copiar banco → cohorte' o tildá cursos en el banco disponible.",
                parent=self)
            return
        if not self.cohorte.get("link", "").strip():
            if not messagebox.askyesno(
                "Atención",
                "La cohorte no tiene link de inscripción. ¿Generar el HTML de todas formas?",
                parent=self):
                return
        html = self._generar_html(modo=modo)
        if not html:
            return
        etiqueta = "Moodle/CeNET" if modo == "moodle" else "INET"
        archivo = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            title=f"Guardar HTML para {etiqueta}",
            parent=self
        )
        if not archivo:
            return
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Éxito", f"HTML para {etiqueta} generado correctamente.", parent=self)

    def _copiar_html_clipboard(self, modo="moodle"):
        html = self._generar_html(modo=modo)
        if not html:
            return
        self.clipboard_clear()
        self.clipboard_append(html)
        etiqueta = "Moodle/CeNET" if modo == "moodle" else "INET"
        messagebox.showinfo(
            "Listo",
            f"HTML para {etiqueta} copiado al portapapeles.",
            parent=self
        )

    # ─────────────────────────────────────────
    # MÉTODOS VISTA PREVIA (Tab 3)
    # ─────────────────────────────────────────
    def _preview_actualizar(self):
        """Genera el HTML y lo muestra en la pestaña Vista Previa."""
        html = self._generar_html(modo=self._modo_html.get())
        if not html:
            return
        self._preview_html_cache = html
        if self._use_htmlframe:
            full = (
                "<!DOCTYPE html><html><head>"
                "<meta charset='utf-8'>"
                "<style>body{margin:0;padding:0;}</style>"
                "</head><body>"
                f"{html}"
                "</body></html>"
            )
            self._html_frame.load_html(full)
            self.lbl_preview_status.configure(text="Vista actualizada.")
        else:
            self.lbl_preview_status.configure(
                text=f"HTML generado ({len(html):,} chars). Usá «Abrir en navegador» para previsualizar.")

    def _preview_abrir_navegador(self):
        """Abre el HTML generado en el navegador predeterminado."""
        if not self._preview_html_cache:
            html = self._generar_html(modo=self._modo_html.get())
            if not html:
                return
            self._preview_html_cache = html
        full = (
            "<!DOCTYPE html><html><head>"
            "<meta charset='utf-8'>"
            "</head><body style='margin:0;padding:0;'>"
            f"{self._preview_html_cache}"
            "</body></html>"
        )
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8"
        ) as f:
            f.write(full)
            tmppath = f.name
        webbrowser.open(f"file:///{tmppath.replace(chr(92), '/')}")
        self.lbl_preview_status.configure(text="Abierto en el navegador.")

    # ─────────────────────────────────────────
    # MÉTODOS EDITOR HTML (Tab 4)
    # ─────────────────────────────────────────
    def _editor_regenerar(self):
        """Genera el HTML y lo carga en el editor de código."""
        html = self._generar_html(modo=self._modo_html.get())
        if not html:
            return
        self.editor_text.delete("1.0", "end")
        self.editor_text.insert("1.0", html)
        self.lbl_editor_status.configure(
            text=f"HTML generado — {len(html):,} caracteres.")

    def _editor_copiar(self):
        """Copia el contenido actual del editor al portapapeles."""
        html = self.editor_text.get("1.0", "end-1c")
        if not html.strip():
            messagebox.showinfo(
                "Info", "El editor está vacío. Presioná «Regenerar» primero.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(html)
        self.lbl_editor_status.configure(text="Copiado al portapapeles.")

    def _editor_guardar(self):
        """Guarda el contenido actual del editor como archivo HTML."""
        html = self.editor_text.get("1.0", "end-1c")
        if not html.strip():
            messagebox.showinfo(
                "Info", "El editor está vacío. Presioná «Regenerar» primero.", parent=self)
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            title="Guardar HTML editado",
            parent=self
        )
        if not archivo:
            return
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Éxito", "HTML guardado correctamente.", parent=self)
        self.lbl_editor_status.configure(text="Guardado correctamente.")

    @staticmethod
    def _color_estado(estado: str) -> str:
        el = estado.lower()
        if "abierta" in el or "abierto" in el:
            return "#22c55e"
        if "cerrada" in el or "cerrado" in el:
            return "#ef4444"
        if "próxim" in el or "proximamente" in el:
            return "#f59e0b"
        return "#3b82f6"

    def _generar_html(self, modo="moodle"):
        self._save_coh_edit()
        titulo    = self.titulo_oferta_var.get()
        coh_link  = self.cohorte.get("link", "")
        coh_estado = self.cohorte.get("estado", "")
        ec        = self._color_estado(coh_estado)

        def get_cursos_coh():
            result = []
            for entry in self.cohorte.get("cursos", []):
                bidx = entry.get("banco_idx", -1)
                etiqueta = entry.get("etiqueta", "")
                if 0 <= bidx < len(self.banco_cursos):
                    c = dict(self.banco_cursos[bidx])
                    c["etiqueta"] = etiqueta
                    result.append(c)
            return result

        es_inet = (modo == "inet")

        # ── Helper acordeón para inet (debe definirse antes de usarse) ──
        def _make_acordeon_inet(titulo, descripcion, info_url, ins_url, compacto=False):
            pad = "6px 0" if not compacto else "4px 0"
            partes = []
            if descripcion:
                partes.append(
                    f'<p style="font-size:0.8rem;color:#555;line-height:1.5;margin:0 0 8px 0;">'
                    f'{descripcion}</p>'
                )
            if info_url:
                partes.append(
                    f'<a href="{info_url}" target="_blank" '
                    f'style="font-size:0.8rem;font-weight:600;color:#45658d;'
                    f'text-decoration:none;display:block;margin-bottom:6px;">'
                    f'Ver detalle del curso →</a>'
                )
            if ins_url:
                partes.append(
                    f'<a href="{ins_url}" target="_blank" '
                    f'style="display:block;text-align:center;padding:8px;border-radius:8px;'
                    f'background:#45658d;color:white;font-size:0.82rem;font-weight:700;'
                    f'text-decoration:none;">Inscribirse →</a>'
                )
            if not partes:
                return ""
            contenido = "".join(partes)
            return (
                f'<details style="margin-top:4px;">'
                f'<summary style="cursor:pointer;font-size:0.84rem;font-weight:600;'
                f'color:#45658d;padding:{pad};border-top:1px solid #eee;'
                f'list-style:none;user-select:none;">'
                f'▶ Más información e inscripción</summary>'
                f'<div style="padding:10px 0 4px 0;">{contenido}</div>'
                f'</details>'
            )

        # ── Estilos inline ──
        S_F = (
            "cursor:pointer;padding:7px 16px;border-radius:999px;"
            "border:1.5px solid #45658d;background:white;color:#45658d;"
            "margin:4px;font-size:0.84rem;font-weight:500;font-family:inherit;"
        )
        S_FA = (
            "cursor:pointer;padding:7px 16px;border-radius:999px;"
            "border:1.5px solid #45658d;background:#45658d;color:white;"
            "margin:4px;font-size:0.84rem;font-weight:500;font-family:inherit;"
        )
        # Moodle: botón único "Más información e inscripción"
        S_MAS_INFO_INS = (
            "display:block;width:100%;text-align:center;padding:9px 10px;"
            "border-radius:8px;font-size:0.85rem;font-weight:700;cursor:pointer;"
            "background:#45658d;color:white;border:none;font-family:inherit;"
            "box-sizing:border-box;"
        )
        S_INFO_SM = (
            "text-align:center;padding:5px 8px;border-radius:8px;"
            "text-decoration:none;font-size:0.78rem;font-weight:600;"
            "background:#f0f4ff;color:#45658d;border:1px solid #c7d2e8;"
            "display:inline-block;box-sizing:border-box;"
        )

        def js_str(s):
            """Escapa una cadena para uso en onclick JS con comillas simples."""
            return (s or "").replace("\\", "\\\\").replace("'", "\\'")

        def make_info_uri(texto_html):
            """Convierte HTML estático en un data URI para iframe."""
            if not texto_html:
                return ""
            b64 = base64.b64encode(texto_html.encode("utf-8")).decode("ascii")
            return f"data:text/html;base64,{b64}"

        btn_ins_coh = (
            f'<a href="{coh_link}" target="_blank" style="'
            f'display:inline-block;padding:9px 22px;border-radius:8px;'
            f'background:#45658d;color:white;text-decoration:none;'
            f'font-size:0.9rem;font-weight:600;">Inscribirse ahora →</a>'
            if coh_link else ""
        )

        coh_header = (
            f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;'
            f'background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);'
            f'color:white;padding:18px 24px;border-radius:12px;margin-bottom:22px;">'
            f'<span style="font-size:1.25rem;font-weight:700;">{self.cohorte["nombre"]}</span>'
            f'<span style="display:inline-block;background:{ec};color:white;'
            f'font-size:0.82rem;font-weight:600;padding:4px 14px;border-radius:999px;">'
            f'{coh_estado}</span>'
            f'<span style="margin-left:auto;">{btn_ins_coh}</span>'
            f'</div>'
        )

        cursos_activa = get_cursos_coh()

        # Sección "Nuevos en esta edición"
        nuevos = [c for c in cursos_activa if c.get("etiqueta") == "Nuevo"]
        bloque_nuevos = ""
        if nuevos:
            nuevos_cards = ""
            for c in nuevos:
                tit      = c.get("titulo", "")
                img_url  = c.get("img", "")
                desc_txt = c.get("descripcion", "")
                info_url = c.get("info", "") or make_info_uri(c.get("info_texto", ""))
                ins_url  = c.get("form_externo", "") or coh_link
                search   = f"{tit.lower()} {c.get('categoria','').lower()} nuevo"
                if es_inet:
                    accion_html = _make_acordeon_inet(tit, desc_txt, info_url, ins_url)
                    imagen_html = ""
                else:
                    info_uri = info_url
                    accion_html = (
                        f'<button type="button" '
                        f'onclick="cnetOpenModal(\'{js_str(tit)}\',\'{js_str(img_url)}\',\'{js_str(info_uri)}\',\'{js_str(ins_url)}\')" '
                        f'style="{S_MAS_INFO_INS}">Más información e inscripción</button>'
                    ) if (info_url or ins_url) else ""
                    imagen_html = (
                        f'<div style="width:100%;height:130px;background:#eef2f7;overflow:hidden;">'
                        f'<img src="{img_url}" alt="{tit}" loading="lazy" '
                        f'style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
                    ) if img_url else ""
                nuevos_cards += (
                    f'<div data-search="{search}" style="background:white;border-radius:12px;'
                    f'border:1px solid #e5e7eb;box-shadow:0 2px 8px rgba(0,0,0,.05);'
                    f'overflow:hidden;display:flex;flex-direction:column;">'
                    f'{imagen_html}'
                    f'<div style="padding:12px;flex:1;display:flex;flex-direction:column;gap:6px;">'
                    f'<span style="background:#22c55e;color:white;font-size:0.7rem;'
                    f'font-weight:700;padding:2px 9px;border-radius:999px;'
                    f'display:inline-block;margin-bottom:4px;">🆕 Nuevo</span>'
                    f'<p style="font-size:0.88rem;font-weight:600;color:#1e2a4a;'
                    f'line-height:1.4;margin:0;">{tit}</p>'
                    f'<div style="margin-top:auto;">{accion_html}</div>'
                    f'</div></div>'
                )
            bloque_nuevos = (
                f'<div style="max-width:1200px;margin:0 auto 28px;padding:0 16px;">'
                f'<div style="font-size:1.1rem;font-weight:700;color:#1e2a4a;'
                f'border-bottom:2px solid #22c55e;padding-bottom:8px;margin-bottom:16px;">'
                f'🆕 Nuevos en esta edición</div>'
                f'<div id="secNuevos" class="cnet-grid-nuevos">{nuevos_cards}</div></div>\n'
            )

        # Categorías únicas de la cohorte activa
        cats_activa_orden = []
        cats_activa_vistas = set()
        por_cat_activa = {}
        for c in cursos_activa:
            cat = c.get("categoria", "Sin categoría")
            if cat not in cats_activa_vistas:
                cats_activa_orden.append(cat)
                cats_activa_vistas.add(cat)
                por_cat_activa[cat] = []
            por_cat_activa[cat].append(c)

        btns_cat = "\n".join(
            f'<button type="button" style="{S_F}" '
            f'onclick="cnetFiltro(\'{cat.lower().replace(chr(39), chr(92)+chr(39))}\')">'
            f'{cat}</button>'
            for cat in cats_activa_orden
        )
        if cats_activa_orden:
            btns_cat += f'\n<button type="button" style="{S_FA}" id="btnVerTodos" onclick="cnetFiltro(\'\')">Ver todos</button>'

        # Cards de la cohorte activa agrupadas por categoría
        secs_activa = ""
        for cat_idx, cat in enumerate(cats_activa_orden):
            cards = ""
            for c in por_cat_activa[cat]:
                tit      = c.get("titulo", "")
                img_url  = c.get("img", "")
                desc_txt = c.get("descripcion", "")
                info_url = c.get("info", "") or make_info_uri(c.get("info_texto", ""))
                ins_url  = c.get("form_externo", "") or coh_link
                etiqueta = c.get("etiqueta", "")
                search   = f"{tit.lower()} {cat.lower()} {etiqueta.lower()}"
                if etiqueta == "Destacado":
                    badge_html = (
                        '<span style="background:#d4a843;color:white;font-size:0.7rem;'
                        'font-weight:700;padding:2px 9px;border-radius:999px;'
                        'display:inline-block;margin-bottom:4px;">⭐ Destacado</span>'
                    )
                elif etiqueta == "Nuevo":
                    badge_html = (
                        '<span style="background:#22c55e;color:white;font-size:0.7rem;'
                        'font-weight:700;padding:2px 9px;border-radius:999px;'
                        'display:inline-block;margin-bottom:4px;">🆕 Nuevo</span>'
                    )
                else:
                    badge_html = ""

                if es_inet:
                    accion_html = _make_acordeon_inet(tit, desc_txt, info_url, ins_url)
                    imagen_html = ""
                else:
                    accion_html = (
                        f'<button type="button" '
                        f'onclick="cnetOpenModal(\'{js_str(tit)}\',\'{js_str(img_url)}\',\'{js_str(info_url)}\',\'{js_str(ins_url)}\')" '
                        f'style="{S_MAS_INFO_INS}">Más información e inscripción</button>'
                    ) if (info_url or ins_url) else ""
                    imagen_html = (
                        f'<div style="width:100%;height:148px;background:#eef2f7;overflow:hidden;">'
                        f'<img src="{img_url}" alt="{tit}" loading="lazy" '
                        f'style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
                    ) if img_url else ""

                cards += (
                    f'\n<div data-search="{search}" style="'
                    f'background:white;border-radius:12px;border:1px solid #e5e7eb;'
                    f'box-shadow:0 2px 8px rgba(0,0,0,.05);overflow:hidden;'
                    f'display:flex;flex-direction:column;">'
                    f'{imagen_html}'
                    f'<div style="padding:14px;flex:1;display:flex;flex-direction:column;gap:8px;">'
                    f'{badge_html}'
                    f'<p style="font-size:0.9rem;font-weight:600;color:#1e2a4a;'
                    f'line-height:1.4;margin:0;min-height:38px;">{tit}</p>'
                    f'<div style="margin-top:auto;">{accion_html}</div>'
                    f'</div></div>'
                )
            n_cat = len(por_cat_activa[cat])
            cat_id = f"cat_{cat_idx}"
            secs_activa += (
                f'\n<div id="{cat_id}" style="margin-bottom:36px;">'
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'font-size:1.1rem;font-weight:700;color:#1e2a4a;'
                f'border-bottom:2px solid #45658d;padding-bottom:8px;margin-bottom:16px;">'
                f'{cat}'
                f'<span style="margin-left:auto;font-size:0.76rem;font-weight:500;'
                f'color:#6b7280;background:#e5e7eb;padding:2px 10px;border-radius:999px;">'
                f'{n_cat} curso{"s" if n_cat != 1 else ""}</span></div>'
                f'<div class="cnet-grid">'
                f'{cards}</div></div>'
            )

        # ── Modal de inscripción (solo Moodle/CeNET) ──
        modal_html = "" if es_inet else (
            # Overlay
            '<div id="cnetModal" onclick="if(event.target===this)cnetCloseModal()" '
            'style="display:none;position:fixed;inset:0;z-index:9999;'
            'background:rgba(0,0,0,0.72);align-items:center;justify-content:center;padding:12px;">'
            # Contenedor principal (grande para el iframe)
            '<div style="background:white;border-radius:14px;width:min(920px,95vw);'
            'height:min(680px,90vh);overflow:hidden;box-shadow:0 24px 64px rgba(0,0,0,0.4);'
            'display:flex;flex-direction:column;">'
            # ── Barra superior ──
            '<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;'
            'background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);flex-shrink:0;">'
            '<span id="cnetModalTitulo" style="flex:1;font-size:0.95rem;font-weight:700;'
            'color:white;line-height:1.3;"></span>'
            '<button type="button" onclick="cnetCloseModal()" '
            'style="background:rgba(255,255,255,0.15);color:white;border:none;border-radius:8px;'
            'padding:5px 12px;cursor:pointer;font-size:0.85rem;font-family:inherit;">✕ Cerrar</button>'
            '</div>'
            # ── Área del iframe ──
            '<div style="flex:1;position:relative;background:#f3f4f6;overflow:hidden;">'
            # Indicador de carga
            '<div id="cnetModalLoader" '
            'style="position:absolute;inset:0;display:flex;flex-direction:column;'
            'align-items:center;justify-content:center;gap:12px;background:#f3f4f6;z-index:1;">'
            '<div style="width:36px;height:36px;border:3px solid #e5e7eb;'
            'border-top-color:#45658d;border-radius:50%;'
            'animation:cnetSpin 0.8s linear infinite;"></div>'
            '<span style="font-size:0.85rem;color:#6b7280;">Cargando página del curso...</span>'
            '</div>'
            # iframe (src vacío hasta que se abra el modal)
            '<iframe id="cnetModalFrame" src="" '
            'style="width:100%;height:100%;border:none;display:block;" '
            'onload="document.getElementById(\'cnetModalLoader\').style.display=\'none\';">'
            '</iframe>'
            '</div>'
            # ── Barra inferior ──
            '<div style="display:flex;align-items:center;gap:10px;'
            'padding:12px 16px;background:white;border-top:1px solid #e5e7eb;flex-shrink:0;">'
            '<span style="flex:1;font-size:0.8rem;color:#92400e;font-style:italic;">'
            'Leé atentamente los requisitos antes de inscribirte.</span>'
            '<button type="button" onclick="cnetCloseModal()" '
            'style="padding:8px 18px;border-radius:8px;background:transparent;'
            'border:1px solid #e5e7eb;color:#6b7280;font-size:0.85rem;'
            'cursor:pointer;font-family:inherit;">Cancelar</button>'
            '<a id="cnetModalIns" href="#" target="_blank" '
            'style="padding:8px 22px;border-radius:8px;text-decoration:none;'
            'font-size:0.85rem;font-weight:700;background:#45658d;color:white;'
            'display:inline-flex;align-items:center;gap:6px;">Inscribirme</a>'
            '</div>'
            '</div></div>'
            # Animación del spinner (CSS)
            '<style>'
            '@keyframes cnetSpin{to{transform:rotate(360deg)}}'
            '</style>\n'
        )

        # ── Script JS: búsqueda + filtro categoría solo para cohorte activa ──
        modal_js = "" if es_inet else (
            f'function cnetOpenModal(titulo,img,info,ins){{\n'
            f'  document.getElementById("cnetModalTitulo").textContent=titulo;\n'
            f'  document.getElementById("cnetModalIns").href=ins||"#";\n'
            f'  var loader=document.getElementById("cnetModalLoader");\n'
            f'  if(loader)loader.style.display="flex";\n'
            f'  var fr=document.getElementById("cnetModalFrame");\n'
            f'  if(fr)fr.src=info||"";\n'
            f'  document.getElementById("cnetModal").style.display="flex";\n'
            f'}}\n'
            f'function cnetCloseModal(){{\n'
            f'  var fr=document.getElementById("cnetModalFrame");\n'
            f'  if(fr)fr.src="";\n'
            f'  document.getElementById("cnetModal").style.display="none";\n'
            f'}}\n'
        )
        script = (
            f'<script>\n'
            f'{modal_js}'
            f'function cnetFiltro(val){{\n'
            f'  var inp=document.getElementById("cnetSearch");\n'
            f'  if(inp)inp.value=val;\n'
            f'  cnetAplicar(val);\n'
            f'}}\n'
            f'function cnetDoFiltro(){{\n'
            f'  var inp=document.getElementById("cnetSearch");\n'
            f'  cnetAplicar(inp?inp.value.toLowerCase():"");\n'
            f'}}\n'
            f'function cnetAplicar(val){{\n'
            f'  val=val.toLowerCase();\n'
            f'  var hayVis=false;\n'
            f'  var secs=document.querySelectorAll("#cnetActiva [id^=\'cat_\']");\n'
            f'  for(var i=0;i<secs.length;i++){{\n'
            f'    var vis=0;\n'
            f'    var cards=secs[i].querySelectorAll("[data-search]");\n'
            f'    for(var j=0;j<cards.length;j++){{\n'
            f'      var m=(cards[j].getAttribute("data-search")||"").includes(val);\n'
            f'      cards[j].style.display=m?"":"none";\n'
            f'      if(m)vis++;\n'
            f'    }}\n'
            f'    secs[i].style.display=vis>0?"":"none";\n'
            f'    if(vis>0)hayVis=true;\n'
            f'  }}\n'
            f'  var nuevos=document.getElementById("secNuevos");\n'
            f'  if(nuevos){{\n'
            f'    var nCards=nuevos.querySelectorAll("[data-search]");\n'
            f'    var nVis=0;\n'
            f'    for(var k=0;k<nCards.length;k++){{\n'
            f'      var nm=(nCards[k].getAttribute("data-search")||"").includes(val);\n'
            f'      nCards[k].style.display=nm?"":"none";\n'
            f'      if(nm)nVis++;\n'
            f'    }}\n'
            f'    var secN=document.getElementById("secNuevos");\n'
            f'    if(secN)secN.parentElement.style.display=nVis>0?"":"none";\n'
            f'  }}\n'
            f'  var nr=document.getElementById("cnetNoRes");\n'
            f'  if(nr)nr.style.display=hayVis?"none":"block";\n'
            f'}}\n'
            f'</script>\n'
        )

        # ── Estilos responsive ──
        responsive_css = (
            '<style>\n'
            '.cnet-grid { display:grid; gap:18px; grid-template-columns:repeat(3, 1fr); }\n'
            '.cnet-grid-compacto { display:grid; gap:12px; grid-template-columns:repeat(3, 1fr); }\n'
            '.cnet-grid-nuevos { display:grid; gap:16px; grid-template-columns:repeat(3, 1fr); }\n'
            '@media (max-width: 1024px) {\n'
            '  .cnet-grid, .cnet-grid-nuevos { grid-template-columns:repeat(2, 1fr); }\n'
            '  .cnet-grid-compacto { grid-template-columns:repeat(2, 1fr); }\n'
            '}\n'
            '@media (max-width: 640px) {\n'
            '  .cnet-grid, .cnet-grid-nuevos, .cnet-grid-compacto { grid-template-columns:repeat(2, 1fr); }\n'
            '}\n'
            '</style>\n'
        )

        return (
            f'<div style="font-family:\'Segoe UI\',Arial,sans-serif;color:#333;line-height:1.5;">\n'

            # Estilos responsive
            f'{responsive_css}'

            # Modal de inscripción (overlay fijo, oculto por defecto)
            f'{modal_html}'

            # Hero
            f'<div style="background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);'
            f'color:white;text-align:center;padding:36px 20px 24px;'
            f'border-radius:0 0 20px 20px;margin-bottom:24px;">'
            f'<h2 style="font-size:1.9rem;font-weight:700;color:white;'
            f'letter-spacing:-0.5px;margin:0;">{titulo}</h2>'
            f'</div>\n'

            # Cohorte
            f'<div id="cnetActiva" style="max-width:1200px;margin:0 auto;padding:0 16px;">\n'
            f'{coh_header}'

            # Buscador
            f'<div style="max-width:620px;margin:0 auto 18px;padding:0;">'
            f'<input type="text" id="cnetSearch" onkeyup="cnetDoFiltro()" '
            f'placeholder="Buscar curso por nombre o categoría..." '
            f'style="width:100%;padding:11px 16px;border:1.5px solid #cdd5e0;'
            f'border-radius:12px;font-size:1rem;background:white;'
            f'box-sizing:border-box;font-family:inherit;outline:none;">'
            f'</div>\n'

            # Nuevos en esta edición
            f'{bloque_nuevos}'

            # Filtros por categoría
            f'<div style="text-align:center;padding:0 0 18px;">'
            f'{btns_cat}'
            f'</div>\n'

            # Cursos agrupados por categoría
            f'{secs_activa}'

            f'<p id="cnetNoRes" style="display:none;text-align:center;'
            f'padding:48px;color:#9ca3af;font-size:1rem;">'
            f'No se encontraron cursos que coincidan con la búsqueda.</p>'
            f'</div>\n'

            # Script
            f'{script}'
            f'</div>'
        )

    # ─────────────────────────────────────────
    # TEMA
    # ─────────────────────────────────────────
    def _setup_ttk_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
            background=_c("bg_card"),
            foreground=_c("text"),
            fieldbackground=_c("bg_card"),
            borderwidth=0,
            font=("Segoe UI", 12),
            rowheight=30)
        style.configure("Dark.Treeview.Heading",
            background=_c("bg_hover"),
            foreground=_c("text_muted"),
            font=("Segoe UI", 11, "bold"),
            borderwidth=0, relief="flat",
            padding=(10, 6))
        style.map("Dark.Treeview",
            background=[("selected", _c("accent"))],
            foreground=[("selected", "#ffffff")])

    def _toggle_theme(self):
        if self._current_theme == "dark":
            self._current_theme = "light"
            ctk.set_appearance_mode("light")
            self.btn_theme.configure(text="🌙")
        else:
            self._current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.btn_theme.configure(text="☀")
        self._setup_ttk_theme()


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    app = GeneradorMoodle()
    app.mainloop()

import os
import sys
import json
import copy
import csv
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

BANCO_FILE = os.path.join(BASE_DIR, "cursos_banco.json")

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

# =========================
# TOOLTIP HELPER
# =========================
class _Tooltip:
    """Tooltip que aparece al pasar el mouse sobre un widget."""
    def __init__(self, widget, text):
        self._widget = widget
        self._text   = text
        self._tip    = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)
        widget.bind("<Destroy>", self._hide)

    def _show(self, event=None):
        if self._tip:
            return
        x = self._widget.winfo_rootx() + 24
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            self._tip, text=self._text, justify="left",
            background="#1e2a4a", foreground="#e2e8f0",
            relief="flat", font=("Segoe UI", 9),
            wraplength=280, padx=10, pady=6,
        )
        lbl.pack()

    def _hide(self, event=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None


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
        self._sort_state         = {"col": None, "reverse": False}

        _loaded = self._load_banco_json()
        self.banco_cursos = _loaded.get("cursos", [])

        self.categorias_sugeridas = [
            "Innovación y entornos digitales",
            "Estrategias pedagógicas para la ETP",
            "Seguridad institucional",
            "Diseño, Producción y Especializaciones Técnicas",
        ]

        # Variables generales (restauradas desde JSON si existen)
        _saved_titulo = _loaded.get("titulo_oferta", "Oferta Formativa CeNET 2026")
        self.titulo_oferta_var = tk.StringVar(value=_saved_titulo)

        # Cohorte única (restaurada desde JSON si existe)
        _saved_coh = _loaded.get("cohorte", {})
        self.cohorte = (
            _saved_coh if isinstance(_saved_coh, dict) and _saved_coh
            else {"nombre": "2° cohorte", "link": "", "estado": "Inscripción ABIERTA", "cursos": []}
        )
        self.coh_nombre_var = tk.StringVar(value=self.cohorte.get("nombre", "2° cohorte"))
        self.coh_estado_var = tk.StringVar(value=self.cohorte.get("estado", "Inscripción ABIERTA"))
        self.coh_link_var   = tk.StringVar(value=self.cohorte.get("link", ""))
        _default_msg_req = "Enviar sus datos de DNI, Nombre y Apellido a cursoscenet@educacion.gob.ar para inscribirse"
        self.coh_msg_req_var = tk.StringVar(value=self.cohorte.get("msg_requisito", _default_msg_req))

        # Variables formulario banco
        self.tit_var           = tk.StringVar()
        self.cat_var           = tk.StringVar()
        self.img_var           = tk.StringVar()
        self.ext_var           = tk.StringVar()
        self.familia_var       = tk.StringVar()
        self.nivel_var         = tk.StringVar()
        self.dest_var          = tk.StringVar()
        self.conoc_var          = tk.StringVar()
        self.curso_previo_var   = tk.StringVar()
        self._cat_nueva_var     = tk.StringVar()
        self._banco_filtro_var  = tk.StringVar()
        self._coh_filtro_var    = tk.StringVar()
        self._mutual_exc_guard  = False
        self.sintesis_box      = None  # CTkTextbox; assigned in _build_tab_banco
        self._banco_disp_vars  = {}    # bidx -> BooleanVar para banco disponible

        self._setup_ttk_theme()
        self._build_ui()

        # Abrir en cohorte si ya tiene cursos cargados
        if self.cohorte.get("cursos"):
            self.after(50, lambda: self.tabview.set("🗓  Cohorte"))

        # Auto-guardar cambios del editor de cohorte + titulo al JSON
        self.coh_nombre_var.trace_add("write", self._save_coh_edit)
        self.coh_estado_var.trace_add("write", self._save_coh_edit)
        self.coh_link_var.trace_add("write",   self._save_coh_edit)
        self.coh_msg_req_var.trace_add("write", self._save_coh_edit)
        self.titulo_oferta_var.trace_add("write", lambda *_: self._save_banco_json())

        # Exclusión mutua: curso previo <-> conocimientos previos
        self.curso_previo_var.trace_add("write", self._on_curso_previo_changed)
        self.conoc_var.trace_add("write",        self._on_conoc_changed)

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

    def _field(self, parent, label, var, tooltip=None, placeholder="", required=False,
               widget_cls=None, **kw):
        """Crea un label + entry con tooltip opcional en el ícono '?'."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(6, 1))
        lbl_text = label + (" *" if required else "")
        self._label(row, lbl_text, muted=not required).pack(side="left")
        if tooltip:
            tip_btn = ctk.CTkLabel(
                row, text=" ?",
                text_color=COLORS["accent"],
                font=ctk.CTkFont(family="Segoe UI", size=10),
                cursor="question_arrow",
            )
            tip_btn.pack(side="left")
            _Tooltip(tip_btn, tooltip)
        entry = self._entry(parent, textvariable=var, width=0, placeholder=placeholder, **kw)
        entry.pack(fill="x", padx=14, pady=(0, 4))
        return entry

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
        self.tabview.add("🗓  Cohorte")

        self._build_tab_banco(self.tabview.tab("📚  Banco de Cursos"))
        self._build_tab_cohortes(self.tabview.tab("🗓  Cohorte"))

    # ─────────────────────────────────────────
    # TAB 1: BANCO DE CURSOS
    # ─────────────────────────────────────────
    def _build_tab_banco(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # Barra de acción (row 0)
        abar = ctk.CTkFrame(parent, fg_color="transparent", height=44)
        abar.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        abar.grid_propagate(False)

        self._btn(abar, "➕  Añadir Curso", lambda: self._banco_abrir_form(),
                  color="success", height=32).pack(side="left", padx=(4, 8))
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

        # Barra de búsqueda (row 1)
        filtro_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filtro_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self._entry(filtro_frame, textvariable=self._banco_filtro_var, width=0,
                    placeholder="🔍  Filtrar banco por título o categoría...").pack(fill="x")
        self._banco_filtro_var.trace_add("write", lambda *_: self._refresh_banco_tree())

        # Treeview banco (row 2)
        tree_frame = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"],
            corner_radius=10, border_width=1,
            border_color=COLORS["border"]
        )
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("Titulo", "Categoria", "Familia", "Nivel", "Destinatarios",
                "Conocimientos", "ReqPrevio", "Sintesis", "Externo")
        self.banco_tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            style="Dark.Treeview", selectmode="extended"
        )
        _COL_LABELS = {
            "Titulo":        "Título",
            "Categoria":     "Categoría",
            "Familia":       "Familia prof.",
            "Nivel":         "Nivel",
            "Destinatarios": "Destinatarios",
            "Conocimientos": "Conocimientos prev.",
            "ReqPrevio":     "Req. Curso Previo",
            "Sintesis":      "Síntesis",
            "Externo":       "Form. externo",
        }
        _COL_WIDTHS = {
            "Titulo": 200, "Categoria": 150, "Familia": 150, "Nivel": 120,
            "Destinatarios": 180, "Conocimientos": 150, "ReqPrevio": 160,
            "Sintesis": 220, "Externo": 140,
        }
        self._col_labels = _COL_LABELS
        for col in cols:
            self.banco_tree.heading(
                col, text=_COL_LABELS[col],
                command=lambda c=col: self._banco_sort(c)
            )
            self.banco_tree.column(col, width=_COL_WIDTHS[col], minwidth=60)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.banco_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.banco_tree.xview)
        self.banco_tree.configure(yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set)

        self.banco_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        hsb.grid(row=1, column=0, sticky="ew", padx=6)

        self.banco_tree.tag_configure("en_coh", foreground="#6b7280")
        self.banco_tree.bind("<Double-1>", lambda _: self._banco_abrir_form(self._banco_sel_idx()))

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
        top_frame.grid_rowconfigure(2, weight=1)
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
        self._btn(top_bar, "✏ Editar", self._coh_editar_en_banco,
                  color="warning", height=28, width=90).pack(side="right", padx=2)
        self._btn(top_bar, "▼", self._coh_bajar,
                  color="ghost", height=28, width=36).pack(side="right", padx=2)
        self._btn(top_bar, "▲", self._coh_subir,
                  color="ghost", height=28, width=36).pack(side="right", padx=2)

        # Búsqueda en cohorte
        coh_search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        coh_search_frame.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 2))
        self._entry(coh_search_frame, textvariable=self._coh_filtro_var, width=0,
                    placeholder="🔍  Filtrar por título o categoría...").pack(fill="x")
        self._coh_filtro_var.trace_add("write", lambda *_: self._coh_aplicar_filtro())

        # Treeview cohorte
        coh_tree_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        coh_tree_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        coh_tree_frame.grid_rowconfigure(0, weight=1)
        coh_tree_frame.grid_columnconfigure(0, weight=1)

        coh_cols = ("Titulo", "Categoria", "Familia", "Nivel", "Destinatarios",
                    "Conocimientos", "ReqPrevio", "Sintesis", "Externo", "Etiqueta")
        self.coh_tree = ttk.Treeview(
            coh_tree_frame, columns=coh_cols, show="headings",
            style="Dark.Treeview", selectmode="extended"
        )
        for col, w, lbl in [
            ("Titulo",        200, "Título"),
            ("Categoria",     150, "Categoría"),
            ("Familia",       150, "Familia prof."),
            ("Nivel",         120, "Nivel"),
            ("Destinatarios", 180, "Destinatarios"),
            ("Conocimientos", 150, "Conocimientos prev."),
            ("ReqPrevio",     160, "Req. Curso Previo"),
            ("Sintesis",      220, "Síntesis"),
            ("Externo",       140, "Form. externo"),
            ("Etiqueta",       90, "Etiqueta"),
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
        self._btn(bot_header, "Agregar todos", self._banco_agregar_todos,
                  color="ghost", height=28, width=115).pack(side="right", padx=(2, 4))
        self._btn(bot_header, "Agregar seleccionados", self._banco_agregar_seleccionados,
                  color="accent", height=28, width=175).pack(side="right", padx=2)

        self._banco_disp_frame = ctk.CTkScrollableFrame(
            bot_frame, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self._banco_disp_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

    # ─────────────────────────────────────────
    # TAB 3: VISTA PREVIA HTML
    # ─────────────────────────────────────────
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

        self._btn(inner, "💾  Guardar banco",
                  self._guardar_banco, color="ghost", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "📂  Cargar banco",
                  self._cargar_banco, color="ghost", height=38).pack(
            side="left", padx=6)

        sep1 = ctk.CTkFrame(inner, width=2, height=36, fg_color=COLORS["border"])
        sep1.pack(side="left", padx=14)

        self._btn(inner, "🌐  Abrir Moodle",
                  lambda: self._abrir_en_navegador("moodle"), color="accent", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "💾  HTML Moodle",
                  lambda: self.exportar_html("moodle"), color="success", height=38).pack(
            side="left", padx=4)

        sep2 = ctk.CTkFrame(inner, width=2, height=36, fg_color=COLORS["border"])
        sep2.pack(side="left", padx=14)

        self._btn(inner, "🌐  Abrir INET",
                  lambda: self._abrir_en_navegador("inet"), color="accent", height=38).pack(
            side="left", padx=6)
        self._btn(inner, "💾  HTML INET",
                  lambda: self.exportar_html("inet"), color="info", height=38).pack(
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
        """Primer índice seleccionado en banco_tree, o None."""
        sel = self.banco_tree.selection()
        if not sel:
            return None
        tags = self.banco_tree.item(sel[0], "tags")
        return int(tags[0]) if tags else None

    def _banco_sel_indices(self):
        """Lista de todos los índices seleccionados en banco_tree."""
        indices = []
        for item in self.banco_tree.selection():
            tags = self.banco_tree.item(item, "tags")
            if tags:
                indices.append(int(tags[0]))
        return indices

    def _refresh_banco_tree(self):
        """Refresca banco_tree y lbl_banco_count."""
        for item in self.banco_tree.get_children():
            self.banco_tree.delete(item)
        filtro = getattr(self, '_banco_filtro_var', None)
        filtro_txt = filtro.get().lower().strip() if filtro else ""
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        for i, c in enumerate(self.banco_cursos):
            if filtro_txt:
                haystack = f"{c.get('titulo','').lower()} {c.get('categoria','').lower()}"
                if filtro_txt not in haystack:
                    continue
            ext = c.get("form_externo", "")
            sint = c.get("sintesis", "")
            en_coh = i in ya_en_coh
            titulo_display = ("✓ " + c.get("titulo", "")) if en_coh else c.get("titulo", "")
            tags = (str(i), "en_coh") if en_coh else (str(i),)
            self.banco_tree.insert("", "end", tags=tags, values=(
                titulo_display,
                c.get("categoria", ""),
                sint[:70] + ("…" if len(sint) > 70 else "") if sint else "",
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
        sintesis_txt = self.sintesis_box.get("1.0", "end-1c").strip() if self.sintesis_box else ""
        curso = {
            "titulo":         titulo,
            "categoria":      self.cat_var.get().strip() or "Sin categoría",
            "img":            self.img_var.get().strip(),
            "familia_prof":   self.familia_var.get().strip(),
            "nivel":          self.nivel_var.get().strip(),
            "destinatarios":  self.dest_var.get().strip(),
            "conocimientos":  self.conoc_var.get().strip(),
            "sintesis":        sintesis_txt,
            "curso_previo":    self.curso_previo_var.get().strip(),
        }
        if ext:
            curso["form_externo"] = ext
        fue_edicion = self._banco_edit_idx is not None
        if fue_edicion:
            # Al editar, actualizar banco_cursos y actualizar referencias en cohortes
            self.banco_cursos[self._banco_edit_idx] = curso
            self._banco_edit_idx = None
            self.lbl_banco_form_title.configure(text="➕  Añadir / Editar Curso")
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
        self._save_banco_json()
        self._marcar_cambio()
        tit_corto = titulo[:30] + ("…" if len(titulo) > 30 else "")
        accion = "Actualizado" if fue_edicion else "Agregado"
        self.lbl_banco_status.configure(text=f"✓ {accion}: {tit_corto}")
        self.after(2500, lambda: self.lbl_banco_status.configure(text=""))

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
        self.ext_var.set(c.get("form_externo", ""))
        self.familia_var.set(c.get("familia_prof", ""))
        self.nivel_var.set(c.get("nivel", ""))
        self.dest_var.set(c.get("destinatarios", ""))
        self.conoc_var.set(c.get("conocimientos", ""))
        self.curso_previo_var.set(c.get("curso_previo", "") or c.get("requisito_insc", ""))

        if self.sintesis_box:
            self.sintesis_box.delete("1.0", "end")
            sintesis = c.get("sintesis", "")
            if sintesis:
                self.sintesis_box.insert("1.0", sintesis)
        self._banco_edit_idx = idx
        titulo_corto = c["titulo"][:28] + ("…" if len(c["titulo"]) > 28 else "")
        self.lbl_banco_form_title.configure(text=f"✏  Editando: {titulo_corto}")
        self.btn_banco_guardar.configure(
            text="💾  Guardar Cambios",
            fg_color=COLORS["warning"],
            hover_color=("#d97706", "#b45309")
        )
        self.btn_banco_cancelar.pack(
            side="left", fill="x", expand=True, padx=(4, 0))
        if not self._banco_form_visible:
            self._toggle_banco_form()

    def _toggle_banco_form(self):
        """Muestra u oculta el formulario del banco."""
        if self._banco_form_visible:
            self._form_scroll.grid_forget()
            self._banco_form_visible = False
            self.btn_toggle_form.configure(text="▼ Abrir")
        else:
            self._form_scroll.grid(row=1, column=0, sticky="nsew")
            self._banco_form_visible = True
            self.btn_toggle_form.configure(text="▲ Cerrar")

    def _banco_cancelar(self):
        """Cancela edición del banco."""
        self._banco_edit_idx = None
        self.lbl_banco_form_title.configure(text="➕  Añadir / Editar Curso")
        self.btn_banco_guardar.configure(
            text="➕  Agregar",
            fg_color=COLORS["success"],
            hover_color=("#16a34a", "#15803d")
        )
        self.btn_banco_cancelar.pack_forget()
        self._banco_limpiar_form()

    def _banco_eliminar(self):
        """Elimina del banco los cursos seleccionados (con confirmación)."""
        indices = self._banco_sel_indices()
        if not indices:
            messagebox.showinfo("Info", "Seleccioná uno o más cursos para eliminar.", parent=self)
            return
        if len(indices) == 1:
            msg = f"¿Eliminar '{self.banco_cursos[indices[0]].get('titulo','?')}' del banco?\nSe eliminará también de la cohorte."
        else:
            msg = f"¿Eliminar {len(indices)} cursos del banco?\nSe eliminarán también de la cohorte."
        if not messagebox.askyesno("Confirmar", msg, parent=self):
            return
        # Eliminar de mayor a menor para no invalidar índices
        for idx in sorted(indices, reverse=True):
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
            elif self._banco_edit_idx is not None and self._banco_edit_idx > idx:
                self._banco_edit_idx -= 1
        self._refresh_banco_tree()
        self._refresh_cohorte_panel()
        self._save_banco_json()
        self._marcar_cambio()

    def _banco_duplicar(self):
        """Duplica los cursos seleccionados."""
        indices = sorted(self._banco_sel_indices())
        if not indices:
            messagebox.showinfo("Info", "Seleccioná uno o más cursos para duplicar.", parent=self)
            return
        # Insertar copias de mayor a menor para preservar posiciones relativas
        offset = 0
        for idx in indices:
            insert_at = idx + 1 + offset
            nuevo = copy.deepcopy(self.banco_cursos[idx + offset])
            nuevo["titulo"] += " (copia)"
            self.banco_cursos.insert(insert_at, nuevo)
            for entry in self.cohorte.get("cursos", []):
                if entry.get("banco_idx", -1) >= insert_at:
                    entry["banco_idx"] += 1
            offset += 1
        self._refresh_banco_tree()
        self._save_banco_json()
        self._marcar_cambio()

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
        self._save_banco_json()
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
        self._save_banco_json()
        self._marcar_cambio()
        for child in self.banco_tree.get_children():
            if self.banco_tree.item(child, "tags") == (str(next_idx),):
                self.banco_tree.selection_set(child)
                break

    @staticmethod
    def _load_banco_json():
        """Carga cursos_banco.json. Devuelve dict con 'cursos', 'cohorte', 'titulo_oferta'."""
        if os.path.isfile(BANCO_FILE):
            try:
                with open(BANCO_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return {"cursos": data}
                elif isinstance(data, dict) and "cursos" in data:
                    return data
            except Exception:
                pass
        return {"cursos": []}

    def _save_banco_json(self):
        """Guarda estado completo (cursos + cohorte + título) en cursos_banco.json."""
        data = {
            "cursos": self.banco_cursos,
            "cohorte": self.cohorte,
            "titulo_oferta": self.titulo_oferta_var.get() if hasattr(self, "titulo_oferta_var") else "Oferta Formativa CeNET 2026",
        }
        try:
            with open(BANCO_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudo guardar cursos_banco.json:\n{e}", parent=self)

    def _banco_limpiar_form(self):
        """Limpia los campos del formulario del banco."""
        for v in (self.tit_var, self.cat_var, self.img_var,
                  self.ext_var, self.familia_var, self.nivel_var,
                  self.dest_var, self.conoc_var, self.curso_previo_var):
            v.set("")
        if self.sintesis_box:
            self.sintesis_box.delete("1.0", "end")

    def _on_curso_previo_changed(self, *_):
        if self._mutual_exc_guard:
            return
        if self.curso_previo_var.get().strip():
            self._mutual_exc_guard = True
            self.conoc_var.set("")
            self._mutual_exc_guard = False
            if hasattr(self, "_conoc_entry"):
                self._conoc_entry.configure(state="disabled")
        else:
            if hasattr(self, "_conoc_entry"):
                self._conoc_entry.configure(state="normal")

    def _on_conoc_changed(self, *_):
        if self._mutual_exc_guard:
            return
        if self.conoc_var.get().strip():
            self._mutual_exc_guard = True
            self.curso_previo_var.set("")
            self._mutual_exc_guard = False
            if hasattr(self, "_curso_previo_entry"):
                self._curso_previo_entry.configure(state="disabled")
        else:
            if hasattr(self, "_curso_previo_entry"):
                self._curso_previo_entry.configure(state="normal")

    def _banco_sort(self, col):
        """Ordena banco_cursos por la columna indicada y remapea índices de cohorte."""
        field_map = {
            "Titulo": "titulo", "Categoria": "categoria",
            "Sintesis": "sintesis", "Externo": "form_externo",
        }
        field = field_map.get(col, col.lower())
        if self._sort_state["col"] == col:
            self._sort_state["reverse"] = not self._sort_state["reverse"]
        else:
            self._sort_state["col"] = col
            self._sort_state["reverse"] = False
        reverse = self._sort_state["reverse"]

        # Guardar posición anterior de cada objeto (por identidad) para remap de cohorte
        pre_pos = {id(c): i for i, c in enumerate(self.banco_cursos)}
        self.banco_cursos.sort(key=lambda c: (c.get(field) or "").lower(), reverse=reverse)
        post_pos = {id(c): i for i, c in enumerate(self.banco_cursos)}
        # Invertir pre_pos: old_idx -> object id
        old_idx_to_id = {v: k for k, v in pre_pos.items()}
        for entry in self.cohorte.get("cursos", []):
            oidx = entry.get("banco_idx", -1)
            if oidx >= 0:
                obj_id = old_idx_to_id.get(oidx)
                if obj_id is not None and obj_id in post_pos:
                    entry["banco_idx"] = post_pos[obj_id]

        # Actualizar texto de cabecera con indicador de dirección
        for c, lbl in self._col_labels.items():
            indicator = (" ▲" if not reverse else " ▼") if c == col else ""
            self.banco_tree.heading(c, text=lbl + indicator)

        self._refresh_banco_tree()
        self._save_banco_json()
        self._marcar_cambio()

    def _banco_importar_csv(self):
        """Importa cursos desde un archivo CSV."""
        archivo = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")],
            title="Importar cursos desde CSV",
            parent=self
        )
        if not archivo:
            return
        try:
            with open(archivo, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                filas = list(reader)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el CSV:\n{e}", parent=self)
            return
        if not filas:
            messagebox.showwarning("CSV vacío", "El archivo no contiene filas.", parent=self)
            return

        # Normalizar nombres de columnas (minúsculas, sin espacios)
        def _norm(k): return k.lower().strip().replace(" ", "_")
        filas_norm = [{_norm(k): v for k, v in row.items()} for row in filas]

        _CAMPO = {
            "titulo": "titulo", "title": "titulo",
            "categoria": "categoria", "category": "categoria",
            "img": "img", "imagen": "img", "image": "img", "url_imagen": "img",
            "form_externo": "form_externo", "formulario_externo": "form_externo",
            "familia_prof": "familia_prof", "familia": "familia_prof",
            "nivel": "nivel",
            "destinatarios": "destinatarios",
            "conocimientos": "conocimientos", "conocimientos_previos": "conocimientos",
            "sintesis": "sintesis", "síntesis": "sintesis",
        }

        importados = 0
        omitidos = 0
        for fila in filas_norm:
            curso = {}
            for csv_key, val in fila.items():
                campo = _CAMPO.get(csv_key)
                if campo:
                    curso[campo] = (val or "").strip()
            if not curso.get("titulo"):
                omitidos += 1
                continue
            if "categoria" not in curso:
                curso["categoria"] = "Sin categoría"
            self.banco_cursos.append(curso)
            importados += 1

        if importados == 0:
            messagebox.showwarning(
                "Sin resultados",
                f"No se importó ningún curso (columna 'titulo' requerida).\n"
                f"Filas omitidas: {omitidos}",
                parent=self
            )
            return

        self._refresh_banco_tree()
        self._save_banco_json()
        self._marcar_cambio()
        msg = f"Importados: {importados} cursos."
        if omitidos:
            msg += f"\nOmitidas {omitidos} filas sin título."
        messagebox.showinfo("CSV importado", msg, parent=self)

    # ─────────────────────────────────────────
    # MÉTODOS DE COHORTE (Tab 2)
    # ─────────────────────────────────────────
    def _save_coh_edit(self, *_):
        self.cohorte["nombre"] = self.coh_nombre_var.get().strip() or self.cohorte.get("nombre", "2° cohorte")
        self.cohorte["estado"] = self.coh_estado_var.get()
        self.cohorte["link"]   = self.coh_link_var.get()
        self._save_banco_json()

    def _refresh_cohorte_panel(self):
        self._refresh_coh_tree()
        self._refresh_banco_disponible()
        self._refresh_banco_tree()

    def _refresh_coh_tree(self):
        for item in self.coh_tree.get_children():
            self.coh_tree.delete(item)
        n = 0
        for i, entry in enumerate(self.cohorte.get("cursos", [])):
            bidx = entry.get("banco_idx", -1)
            etiqueta = entry.get("etiqueta", "")
            if 0 <= bidx < len(self.banco_cursos):
                c = self.banco_cursos[bidx]
                tiene_previo = bool(c.get("curso_previo", "") or c.get("requisito_insc", ""))
                if tiene_previo:
                    etiq_display = f"◆ {etiqueta}" if etiqueta else "◆ Previo"
                else:
                    etiq_display = etiqueta if etiqueta else "—"
                self.coh_tree.insert("", "end", tags=(str(i),), values=(
                    c.get("titulo", ""),
                    c.get("categoria", ""),
                    etiq_display,
                ))
                n += 1
        self.lbl_coh_count.configure(text=f"{n} curso{'s' if n != 1 else ''}")

    def _coh_aplicar_filtro(self):
        """Filtra el árbol de cohorte por título o categoría sin perder los datos."""
        filtro = self._coh_filtro_var.get().lower().strip()
        for item in self.coh_tree.get_children():
            vals = self.coh_tree.item(item, "values")
            haystack = f"{vals[0].lower()} {vals[1].lower()}" if vals else ""
            visible = not filtro or filtro in haystack
            self.coh_tree.detach(item) if not visible else self.coh_tree.reattach(item, "", "end")

    def _refresh_banco_disponible(self):
        for w in self._banco_disp_frame.winfo_children():
            w.destroy()
        self._banco_disp_vars = {}
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        disponibles = [(bidx, c) for bidx, c in enumerate(self.banco_cursos) if bidx not in ya_en_coh]
        self.lbl_banco_disp_count.configure(
            text=f"{len(disponibles)} disponible{'s' if len(disponibles) != 1 else ''}")
        for bidx, c in disponibles:
            var = tk.BooleanVar(value=False)
            self._banco_disp_vars[bidx] = var
            texto = f"{c.get('titulo','')}  [{c.get('categoria','')}]"
            cb = ctk.CTkCheckBox(
                self._banco_disp_frame, text=texto,
                variable=var,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                border_color=COLORS["border"], text_color=COLORS["text"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
                checkmark_color=COLORS["white"],
            )
            cb.pack(anchor="w", padx=8, pady=2)

    def _banco_agregar_seleccionados(self):
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        agregados = 0
        for bidx, var in self._banco_disp_vars.items():
            if var.get() and bidx not in ya_en_coh:
                self.cohorte["cursos"].append({"banco_idx": bidx, "etiqueta": ""})
                agregados += 1
        if agregados:
            self._refresh_cohorte_panel()
            self._marcar_cambio()

    def _coh_quitar_curso(self):
        selected = self.coh_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Seleccioná uno o más cursos para quitar.", parent=self)
            return
        indices = sorted(
            [int(self.coh_tree.item(item, "tags")[0]) for item in selected],
            reverse=True
        )
        for pos in indices:
            del self.cohorte["cursos"][pos]
        self._refresh_cohorte_panel()
        self._marcar_cambio()

    def _coh_set_etiqueta(self, etiqueta):
        pos = self._coh_sel_idx()
        if pos is None:
            return
        self.cohorte["cursos"][pos]["etiqueta"] = etiqueta
        self._refresh_coh_tree()

    def _coh_editar_en_banco(self):
        """Salta al banco tab y abre el form de edición del curso seleccionado en la cohorte."""
        pos = self._coh_sel_idx()
        if pos is None:
            messagebox.showinfo("Info", "Seleccioná un curso para editar.", parent=self)
            return
        bidx = self.cohorte["cursos"][pos].get("banco_idx", -1)
        if bidx < 0 or bidx >= len(self.banco_cursos):
            return
        # Ir a la pestaña banco
        self.tabview.set("📚  Banco de Cursos")
        # Seleccionar la fila correspondiente en banco_tree
        for child in self.banco_tree.get_children():
            if self.banco_tree.item(child, "tags") == (str(bidx),):
                self.banco_tree.selection_set(child)
                self.banco_tree.see(child)
                break
        # Abrir el formulario de edición
        self._banco_editar()

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

    def _banco_agregar_todos(self):
        """Agrega todos los cursos disponibles del banco a la cohorte."""
        ya_en_coh = {entry.get("banco_idx") for entry in self.cohorte.get("cursos", [])}
        disponibles = [bidx for bidx in range(len(self.banco_cursos)) if bidx not in ya_en_coh]
        if not disponibles:
            return
        for bidx in disponibles:
            self.cohorte["cursos"].append({"banco_idx": bidx, "etiqueta": ""})
        self._refresh_cohorte_panel()
        self._marcar_cambio()

    # ─────────────────────────────────────────
    # PERSISTENCIA JSON
    # ─────────────────────────────────────────
    def _guardar_banco(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar banco de cursos",
            parent=self
        )
        if not archivo:
            return
        self._save_coh_edit()
        data = {
            "cursos": self.banco_cursos,
            "cohorte": self.cohorte,
            "titulo_oferta": self.titulo_oferta_var.get(),
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Éxito", "Banco guardado.", parent=self)

    def _cargar_banco(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar banco de cursos",
            parent=self
        )
        if not archivo:
            return
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                self.banco_cursos = raw
            elif isinstance(raw, dict) and "cursos" in raw:
                self.banco_cursos = raw["cursos"]
                if isinstance(raw.get("cohorte"), dict) and raw["cohorte"]:
                    self.cohorte = raw["cohorte"]
                    self.coh_nombre_var.set(self.cohorte.get("nombre", ""))
                    self.coh_estado_var.set(self.cohorte.get("estado", ""))
                    self.coh_link_var.set(self.cohorte.get("link", ""))
                if raw.get("titulo_oferta"):
                    self.titulo_oferta_var.set(raw["titulo_oferta"])
            else:
                raise ValueError("Formato de archivo no reconocido.")
            self._save_banco_json()
            self._refresh_banco_tree()
            self._refresh_cohorte_panel()
            n = len(self.banco_cursos)
            messagebox.showinfo(
                "Éxito",
                f"Banco cargado: {n} curso{'s' if n!=1 else ''}.",
                parent=self)
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar el banco:\n{e}", parent=self)

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
    # ABRIR EN NAVEGADOR
    # ─────────────────────────────────────────
    def _abrir_en_navegador(self, modo="moodle"):
        html = self._generar_html(modo=modo)
        if not html:
            return
        full = (
            "<!DOCTYPE html><html><head>"
            "<meta charset='utf-8'>"
            "</head><body style='margin:0;padding:0;'>"
            f"{html}"
            "</body></html>"
        )
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8"
        ) as f:
            f.write(full)
            tmppath = f.name
        webbrowser.open(f"file:///{tmppath.replace(chr(92), '/')}")

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

        # Colores por categoría para INET (franja superior de la card)
        _CAT_COLORS = {
            "innovación y entornos digitales":                  "#45658d",
            "estrategias pedagógicas para la etp":              "#308a3c",
            "seguridad institucional":                          "#E84118",
            "diseño, producción y especializaciones técnicas":  "#9B91C8",
            "programación":                                     "#242c4f",
            "marketing":                                        "#E84118",
            "agroalimentos":                                    "#2e7d32",
        }

        def _cat_color(cat):
            return _CAT_COLORS.get(cat.lower().strip(), "#45658d")

        # ── Helpers de contenido ──

        def _make_info_page_html(titulo, familia, nivel, destinatarios, conocimientos, sintesis, ins_url):
            """Genera HTML completo para el iframe del modal CeNET."""
            rows = ""
            _S_TH = "text-align:left;padding:7px 12px;font-size:0.82rem;font-weight:600;color:#4b5563;white-space:nowrap;vertical-align:top;width:38%;"
            _S_TD = "padding:7px 12px;font-size:0.82rem;color:#1e2a4a;vertical-align:top;"
            for label, val in (
                ("Familia profesional", familia),
                ("Nivel", nivel),
                ("Destinatarios", destinatarios),
                ("Conocimientos previos", conocimientos),
            ):
                if val:
                    rows += f'<tr><th style="{_S_TH}">{label}</th><td style="{_S_TD}">{val}</td></tr>'
            tabla = (
                f'<table style="width:100%;border-collapse:collapse;'
                f'background:#f8fafc;border-radius:8px;overflow:hidden;'
                f'border:1px solid #e5e7eb;margin-bottom:14px;">{rows}</table>'
            ) if rows else ""
            sintesis_html = (
                f'<p style="font-size:0.88rem;color:#374151;line-height:1.65;margin:0 0 14px;">{sintesis}</p>'
            ) if sintesis else ""
            btn_ins = (
                f'<a href="{ins_url}" target="_blank" '
                f'style="display:inline-block;padding:10px 24px;border-radius:8px;'
                f'background:#45658d;color:white;text-decoration:none;'
                f'font-size:0.88rem;font-weight:700;">Inscribirse →</a>'
            ) if ins_url else ""
            return (
                '<!DOCTYPE html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<style>body{font-family:"Segoe UI",Arial,sans-serif;margin:0;padding:16px;color:#1e2a4a;}</style>'
                '</head><body>'
                f'<h3 style="font-size:1rem;font-weight:700;color:#1e2a4a;'
                f'border-bottom:2px solid #45658d;padding-bottom:8px;margin:0 0 14px;">{titulo}</h3>'
                f'{tabla}{sintesis_html}'
                f'<div style="margin-top:8px;">{btn_ins}</div>'
                '</body></html>'
            )

        def _attr(s):
            return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

        def _make_popup_btn(titulo, sintesis, ins_url,
                            familia="", nivel="", destinatarios="", conocimientos="",
                            curso_previo=""):
            return (
                f'<button type="button" onclick="cnetPop(this)" '
                f'data-t="{_attr(titulo)}" '
                f'data-f="{_attr(familia)}" '
                f'data-n="{_attr(nivel)}" '
                f'data-d="{_attr(destinatarios)}" '
                f'data-c="{_attr(conocimientos)}" '
                f'data-s="{_attr(sintesis)}" '
                f'data-i="{_attr(ins_url)}" '
                f'data-r="{_attr(curso_previo)}" '
                f'style="display:block;width:100%;text-align:center;padding:9px 10px;'
                f'border-radius:8px;font-size:0.92rem;font-weight:700;cursor:pointer;'
                f'background:#45658d;color:white;border:none;font-family:inherit;'
                f'box-sizing:border-box;">Más información e inscripción</button>'
            )

        # ── Estilos inline ──
        S_F = (
            "cursor:pointer;padding:7px 16px;border-radius:999px;"
            "border:1.5px solid #45658d;background:white;color:#45658d;"
            "margin:4px;font-size:0.92rem;font-weight:500;font-family:inherit;"
        )
        S_FA = (
            "cursor:pointer;padding:7px 16px;border-radius:999px;"
            "border:1.5px solid #45658d;background:#45658d;color:white;"
            "margin:4px;font-size:0.92rem;font-weight:500;font-family:inherit;"
        )

        coh_header = (
            f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;'
            f'background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);'
            f'color:white;padding:18px 24px;border-radius:12px;margin-bottom:22px;">'
            f'<span style="font-size:1.25rem;font-weight:700;">{self.cohorte["nombre"]}</span>'
            f'<span style="display:inline-block;background:{ec};color:white;'
            f'font-size:0.82rem;font-weight:600;padding:4px 14px;border-radius:999px;">'
            f'{coh_estado}</span>'
            f'</div>'
        )

        cursos_activa = get_cursos_coh()

        # Sección "Nuevos en esta edición"
        nuevos = [c for c in cursos_activa if c.get("etiqueta") == "Nuevo"]
        bloque_nuevos = ""
        if nuevos:
            nuevos_cards = ""
            for c in nuevos:
                tit           = c.get("titulo", "")
                img_url       = c.get("img", "")
                ins_url       = c.get("form_externo", "") or coh_link
                cat_n         = c.get("categoria", "")
                familia       = c.get("familia_prof", "")
                nivel         = c.get("nivel", "")
                destinatarios = c.get("destinatarios", "")
                conocimientos  = c.get("conocimientos", "")
                sintesis       = c.get("sintesis", "")
                curso_previo = c.get("curso_previo", "") or c.get("requisito_insc", "")
                search         = f"{tit.lower()} {cat_n.lower()} nuevo"
                accion_html = _make_popup_btn(
                    tit, sintesis, ins_url,
                    familia, nivel, destinatarios, conocimientos,
                    curso_previo=curso_previo,
                )
                cc = _cat_color(cat_n)
                if img_url:
                    imagen_html = (
                        f'<div style="width:100%;height:130px;background:#eef2f7;overflow:hidden;">'
                        f'<img src="{img_url}" alt="{tit}" loading="lazy" '
                        f'style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
                    )
                else:
                    imagen_html = f'<div style="height:8px;background:{cc};flex-shrink:0;"></div>'
                nuevos_cards += (
                    f'<div data-search="{search}" style="background:white;border-radius:12px;'
                    f'border:1px solid #e5e7eb;box-shadow:0 2px 8px rgba(0,0,0,.05);'
                    f'overflow:hidden;display:flex;flex-direction:column;">'
                    f'{imagen_html}'
                    f'<div style="padding:12px;flex:1;display:flex;flex-direction:column;gap:6px;">'
                    f'<p style="font-size:1rem;font-weight:600;color:#1e2a4a;'
                    f'line-height:1.4;margin:0;">{tit}</p>'
                    f'<div style="margin-top:auto;">{accion_html}</div>'
                    f'</div></div>'
                )
            bloque_nuevos = (
                f'<div style="max-width:1200px;margin:0 auto 28px;padding:0 16px;">'
                f'<div style="font-size:1.1rem;font-weight:700;color:#1e2a4a;'
                f'border-bottom:2px solid #45658d;padding-bottom:8px;margin-bottom:16px;">'
                f'Nuevos en esta edición</div>'
                f'<div id="secNuevos" style="display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));">{nuevos_cards}</div></div>\n'
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
            # Destacados primero dentro de la categoría
            cursos_cat = sorted(
                por_cat_activa[cat],
                key=lambda x: 0 if x.get("etiqueta") == "Destacado" else 1
            )
            for c in cursos_cat:
                tit           = c.get("titulo", "")
                img_url       = c.get("img", "")
                ins_url       = c.get("form_externo", "") or coh_link
                etiqueta      = c.get("etiqueta", "")
                familia       = c.get("familia_prof", "")
                nivel         = c.get("nivel", "")
                destinatarios = c.get("destinatarios", "")
                conocimientos  = c.get("conocimientos", "")
                sintesis       = c.get("sintesis", "")
                curso_previo = c.get("curso_previo", "") or c.get("requisito_insc", "")
                search         = f"{tit.lower()} {cat.lower()} {etiqueta.lower()}"

                accion_html = _make_popup_btn(
                    tit, sintesis, ins_url,
                    familia, nivel, destinatarios, conocimientos,
                    curso_previo=curso_previo,
                )
                cc = _cat_color(cat)
                if img_url:
                    imagen_html = (
                        f'<div style="width:100%;height:148px;background:#eef2f7;overflow:hidden;">'
                        f'<img src="{img_url}" alt="{tit}" loading="lazy" '
                        f'style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
                    )
                else:
                    imagen_html = f'<div style="height:8px;background:{cc};flex-shrink:0;"></div>'

                cards += (
                    f'\n<div data-search="{search}" style="'
                    f'background:white;border-radius:12px;border:1px solid #e5e7eb;'
                    f'box-shadow:0 2px 8px rgba(0,0,0,.05);overflow:hidden;'
                    f'display:flex;flex-direction:column;">'
                    f'{imagen_html}'
                    f'<div style="padding:14px;flex:1;display:flex;flex-direction:column;gap:8px;">'
                    f'<p style="font-size:1rem;font-weight:600;color:#1e2a4a;'
                    f'line-height:1.4;margin:0;min-height:38px;">{tit}</p>'
                    f'<div style="margin-top:auto;">{accion_html}</div>'
                    f'</div></div>'
                )
            n_cat = len(por_cat_activa[cat])
            cat_id = f"cat_{cat_idx}"
            sec_color = _cat_color(cat) if es_inet else "#45658d"
            secs_activa += (
                f'\n<div id="{cat_id}" style="margin-bottom:36px;">'
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'font-size:1.1rem;font-weight:700;color:#1e2a4a;'
                f'border-bottom:2px solid {sec_color};padding-bottom:8px;margin-bottom:16px;">'
                f'{cat}'
                f'<span style="margin-left:auto;font-size:0.85rem;font-weight:500;'
                f'color:#6b7280;background:#e5e7eb;padding:2px 10px;border-radius:999px;">'
                f'{n_cat} curso{"s" if n_cat != 1 else ""}</span></div>'
                f'<div style="display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));">'
                f'{cards}</div></div>'
            )

        popup_html = (
            '<div id="cnetPop" onclick="if(event.target===this)cnetClose()" '
            'style="display:none;position:fixed;inset:0;z-index:9999;'
            'background:rgba(0,0,0,.65);align-items:center;justify-content:center;padding:16px;">'
            '<div style="background:#fff;border-radius:14px;width:min(580px,95vw);'
            'max-height:85vh;overflow-y:auto;box-shadow:0 24px 64px rgba(0,0,0,.4);'
            'display:flex;flex-direction:column;">'
            # Cabecera
            '<div style="display:flex;align-items:center;gap:12px;padding:14px 18px;'
            'background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);'
            'border-radius:14px 14px 0 0;flex-shrink:0;">'
            '<span id="cnetPopT" style="flex:1;font-size:1rem;font-weight:700;'
            'color:white;line-height:1.3;"></span>'
            '<button onclick="cnetClose()" type="button" '
            'style="background:rgba(255,255,255,.15);color:white;border:none;'
            'border-radius:8px;padding:5px 12px;cursor:pointer;font-size:0.9rem;'
            'font-family:inherit;">✕ Cerrar</button>'
            '</div>'
            # Cuerpo
            '<div id="cnetPopB" style="padding:20px 22px;flex:1;"></div>'
            # Pie
            '<div id="cnetPopF" style="padding:12px 22px 16px;border-top:1px solid #e5e7eb;'
            'flex-shrink:0;"></div>'
            '</div></div>\n'
        )

        script = (
            f'<script>\n'
            f'function cnetEsc(s){{return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}}\n'
            f'function cnetPop(b){{\n'
            f'  var d=b.dataset;\n'
            f'  document.getElementById("cnetPopT").textContent=d.t||"";\n'
            f'  var lbl="font-size:0.82rem;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.04em;margin:0 0 2px;";\n'
            f'  var val="font-size:0.9rem;color:#1e2a4a;margin:0 0 12px;";\n'
            f'  var h="";\n'
            f'  if(d.r)h+=\'<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 14px;margin-bottom:14px;">\'+\'<p style="font-size:0.8rem;font-weight:700;color:#c2410c;text-transform:uppercase;letter-spacing:.04em;margin:0 0 4px;">⚠ Requisito de curso previo</p>\'+\'<p style="font-size:0.88rem;color:#7c2d12;margin:0;">\'+cnetEsc(d.r)+\'</p></div>\';\n'
            f'  if(d.f)h+=\'<p style="\'+lbl+\'">Familia profesional</p><p style="\'+val+\'">\'+cnetEsc(d.f)+\'</p>\';\n'
            f'  if(d.n)h+=\'<p style="\'+lbl+\'">Nivel</p><p style="\'+val+\'">\'+cnetEsc(d.n)+\'</p>\';\n'
            f'  if(d.d)h+=\'<p style="\'+lbl+\'">Destinatarios</p><p style="\'+val+\'">\'+cnetEsc(d.d)+\'</p>\';\n'
            f'  if(!d.r&&d.c)h+=\'<p style="\'+lbl+\'">Conocimientos previos</p><p style="\'+val+\'">\'+cnetEsc(d.c)+\'</p>\';\n'
            f'  if(d.s)h+=\'<p style="font-size:0.9rem;color:#374151;line-height:1.65;margin:0;">\'+cnetEsc(d.s)+\'</p>\';\n'
            f'  if(!h)h=\'<p style="color:#9ca3af;">Sin información adicional.</p>\';\n'
            f'  document.getElementById("cnetPopB").innerHTML=h;\n'
            f'  var fp=document.getElementById("cnetPopF");\n'
            f'  if(d.i){{var is_mail=d.i.indexOf("mailto:")===0;var def_mail="Para inscribirse mandar NOMBRE, APELLIDO y CURSO por mail a "+d.i.substring(7);var btn_txt=is_mail?def_mail:"Inscribirse →";fp.innerHTML=\'<a href="\'+d.i+\'" style="display:block;text-align:center;padding:10px 14px;border-radius:8px;background:#45658d;color:white;font-size:0.92rem;font-weight:700;text-decoration:none;word-break:break-all;line-height:1.5;">\'+btn_txt+\'</a>\';fp.style.display="";}}\n'
            f'  else{{fp.innerHTML="";fp.style.display="none";}}\n'
            f'  document.getElementById("cnetPop").style.display="flex";\n'
            f'  document.body.style.overflow="hidden";\n'
            f'}}\n'
            f'function cnetClose(){{\n'
            f'  document.getElementById("cnetPop").style.display="none";\n'
            f'  document.body.style.overflow="";\n'
            f'}}\n'
            f'document.addEventListener("keydown",function(e){{if(e.key==="Escape")cnetClose();}})\n'
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

        if not es_inet:
            _hero_html = (
                '<div style="background:linear-gradient(135deg,#1e2a4a 0%,#45658d 100%);'
                'color:white;text-align:center;padding:36px 20px 24px;'
                'border-radius:0 0 20px 20px;margin-bottom:24px;">'
                f'<h2 style="font-size:1.9rem;font-weight:700;color:white;'
                f'letter-spacing:-0.5px;margin:0;">{titulo}</h2>'
                '</div>\n'
            )
        else:
            _hero_html = ""

        _coh_header = "" if es_inet else coh_header

        return (
            f'<div style="font-family:\'Segoe UI\',Arial,sans-serif;color:#333;line-height:1.5;">\n'

            # Popup de información (oculto por defecto, compartido por todas las cards)
            f'{popup_html}'

            # Hero y header de cohorte (solo CeNET; INET los omite, WordPress ya tiene su propio header)
            f'{_hero_html}'

            # Contenedor principal
            f'<div id="cnetActiva" style="max-width:1200px;margin:0 auto;padding:0 16px;">\n'
            f'{_coh_header}'

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

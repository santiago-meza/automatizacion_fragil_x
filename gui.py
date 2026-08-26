import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from config import TEMPLATE
from extractor import extract_data
from text_builder import build_context
from generator import generate_report


class App:

    # =========================================================
    # COLORES
    # =========================================================

    BG = "#F6F2FA"           # Fondo general
    CARD = "#FFFFFF"         # Tarjeta
    PRIMARY = "#8E6BBE"      # Lila principal
    PRIMARY_DARK = "#73539F" # Lila oscuro
    PRIMARY_LIGHT = "#EDE5F7"
    TEXT = "#342A3D"         # Texto principal
    TEXT_SECONDARY = "#756A7D"
    BORDER = "#DDD3E8"
    SUCCESS = "#6C9A7B"

    def __init__(self, root):

        self.root = root

        self.root.title("Generador de informes FMR1")
        self.root.geometry("720x500")
        self.root.resizable(False, False)

        self.root.configure(bg=self.BG)

        self.reports_folder = None
        self.output_folder = None

        self.setup_styles()
        self.create_widgets()

    # =========================================================
    # ESTILOS
    # =========================================================

    def setup_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        # Entry
        style.configure(
            "Custom.TEntry",
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=8,
            font=("Segoe UI", 10)
        )

        # Botón secundario
        style.configure(
            "Secondary.TButton",
            background=self.PRIMARY_LIGHT,
            foreground=self.PRIMARY_DARK,
            borderwidth=0,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", "#DFD1EE"),
                ("pressed", "#D5C5E5")
            ]
        )

        # Botón principal
        style.configure(
            "Primary.TButton",
            background=self.PRIMARY,
            foreground="white",
            borderwidth=0,
            padding=(22, 12),
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", self.PRIMARY_DARK),
                ("pressed", self.PRIMARY_DARK),
                ("disabled", "#C9BCD7")
            ]
        )

    # =========================================================
    # WIDGETS
    # =========================================================

    def create_widgets(self):

        # -----------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # -----------------------------------------------------

        main = tk.Frame(
            self.root,
            bg=self.BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        # -----------------------------------------------------
        # ENCABEZADO
        # -----------------------------------------------------

        header = tk.Frame(
            main,
            bg=self.BG
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        # Ícono decorativo
        icon = tk.Label(
            header,
            text="✦",
            font=("Segoe UI", 24),
            fg=self.PRIMARY,
            bg=self.BG
        )

        icon.pack()

        title = tk.Label(
            header,
            text="Generador de informes FMR1",
            font=("Segoe UI", 21, "bold"),
            fg=self.TEXT,
            bg=self.BG
        )

        title.pack()

        subtitle = tk.Label(
            header,
            text="Seleccioná las carpetas para generar los informes automáticamente",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG
        )

        subtitle.pack(pady=(5, 0))

        # -----------------------------------------------------
        # TARJETA
        # -----------------------------------------------------

        card = tk.Frame(
            main,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="x",
            padx=5
        )

        content = tk.Frame(
            card,
            bg=self.CARD
        )

        content.pack(
            fill="x",
            padx=25,
            pady=22
        )

        # -----------------------------------------------------
        # CARPETA DE REPORTES
        # -----------------------------------------------------

        self.create_folder_selector(
            parent=content,
            title="Carpeta de informes",
            description="Seleccioná la carpeta donde están los archivos PDF.",
            button_command=self.select_reports_folder,
            entry_name="reports_entry"
        )

        # Separador
        separator1 = tk.Frame(
            content,
            bg=self.BORDER,
            height=1
        )

        separator1.pack(
            fill="x",
            pady=18
        )

        # -----------------------------------------------------
        # CARPETA DE SALIDA
        # -----------------------------------------------------

        self.create_folder_selector(
            parent=content,
            title="Carpeta de salida",
            description="Seleccioná dónde querés guardar los informes generados.",
            button_command=self.select_output_folder,
            entry_name="output_entry"
        )

        # -----------------------------------------------------
        # BOTÓN GENERAR
        # -----------------------------------------------------

        self.generate_button = ttk.Button(
            main,
            text="✦  Generar informes",
            command=self.generate_reports,
            style="Primary.TButton"
        )

        self.generate_button.pack(
            pady=(22, 12)
        )

        # -----------------------------------------------------
        # ESTADO
        # -----------------------------------------------------

        status_frame = tk.Frame(
            main,
            bg=self.PRIMARY_LIGHT
        )

        status_frame.pack(
            fill="x",
            padx=5
        )

        self.status_label = tk.Label(
            status_frame,
            text="●  Listo para comenzar",
            font=("Segoe UI", 9),
            fg=self.PRIMARY_DARK,
            bg=self.PRIMARY_LIGHT,
            anchor="w"
        )

        self.status_label.pack(
            padx=12,
            pady=8
        )

    # =========================================================
    # SELECTOR DE CARPETAS
    # =========================================================

    def create_folder_selector(
        self,
        parent,
        title,
        description,
        button_command,
        entry_name
    ):

        section = tk.Frame(
            parent,
            bg=self.CARD
        )

        section.pack(
            fill="x"
        )

        # Título
        title_label = tk.Label(
            section,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT,
            bg=self.CARD,
            anchor="w"
        )

        title_label.pack(
            anchor="w"
        )

        # Descripción
        description_label = tk.Label(
            section,
            text=description,
            font=("Segoe UI", 9),
            fg=self.TEXT_SECONDARY,
            bg=self.CARD,
            anchor="w"
        )

        description_label.pack(
            anchor="w",
            pady=(2, 8)
        )

        # Fila
        row = tk.Frame(
            section,
            bg=self.CARD
        )

        row.pack(
            fill="x"
        )

        entry = ttk.Entry(
            row,
            style="Custom.TEntry"
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        button = ttk.Button(
            row,
            text="Buscar",
            command=button_command,
            style="Secondary.TButton"
        )

        button.pack(
            side="right",
            padx=(10, 0)
        )

        setattr(
            self,
            entry_name,
            entry
        )

    # =========================================================
    # SELECCIONAR CARPETAS
    # =========================================================

    def select_reports_folder(self):

        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de informes"
        )

        if folder:

            self.reports_folder = Path(folder)

            self.reports_entry.delete(
                0,
                tk.END
            )

            self.reports_entry.insert(
                0,
                str(self.reports_folder)
            )

            self.status_label.config(
                text="●  Carpeta de informes seleccionada"
            )

    def select_output_folder(self):

        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de salida"
        )

        if folder:

            self.output_folder = Path(folder)

            self.output_entry.delete(
                0,
                tk.END
            )

            self.output_entry.insert(
                0,
                str(self.output_folder)
            )

            self.status_label.config(
                text="●  Carpeta de salida seleccionada"
            )

    # =========================================================
    # GENERAR INFORMES
    # =========================================================

    def generate_reports(self):

        if not self.reports_folder:

            messagebox.showwarning(
                "Falta seleccionar carpeta",
                "Seleccioná la carpeta donde se encuentran los informes PDF."
            )

            return

        if not self.output_folder:

            messagebox.showwarning(
                "Falta seleccionar carpeta",
                "Seleccioná la carpeta donde se guardarán los informes."
            )

            return

        if not TEMPLATE.exists():

            messagebox.showerror(
                "Error",
                "No se encontró el template de informes."
            )

            return

        pdfs = sorted(
            self.reports_folder.glob("*.pdf")
        )

        if not pdfs:

            messagebox.showwarning(
                "Sin informes",
                "No se encontraron archivos PDF en la carpeta seleccionada."
            )

            return

        self.generate_button.config(
            state="disabled"
        )

        try:

            generated = 0

            for pdf in pdfs:

                self.status_label.config(
                    text=f"●  Procesando: {pdf.name}"
                )

                self.root.update_idletasks()

                data = extract_data(pdf)

                context = build_context(data)

                output_file = (
                    self.output_folder /
                    f"{context['PROTOCOLO']} {context['PACIENTE']}.docx"
                )

                generate_report(
                    TEMPLATE,
                    output_file,
                    context
                )

                generated += 1

            self.status_label.config(
                text=f"●  ¡Listo! {generated} informes generados"
            )

            messagebox.showinfo(
                "Proceso finalizado",
                f"Se generaron {generated} informes correctamente."
            )

        except Exception as e:

            self.status_label.config(
                text="●  Ocurrió un error"
            )

            messagebox.showerror(
                "Error",
                f"Ocurrió un error durante el procesamiento:\n\n{e}"
            )

        finally:

            self.generate_button.config(
                state="normal"
            )


def run_app():

    root = tk.Tk()

    app = App(root)

    root.mainloop()
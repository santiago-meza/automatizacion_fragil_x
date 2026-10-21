import json
import os
import queue
import re
import threading
import tkinter as tk

from pathlib import Path

import customtkinter as ctk

from config import TEMPLATE
from extractor import extract_data
from generator import generate_report
from genda_ui import (
    COLORS,
    FolderPicker,
    GendaApp,
    StatusLog,
    card,
    font,
    primary_button,
    secondary_button,
    section_label
)
from pdf_exporter import WordConverter
from text_builder import build_context


# ============================================================
# Settings
# ============================================================

def get_settings_file():

    app_data = os.getenv("LOCALAPPDATA")

    if app_data:

        settings_dir = (
            Path(app_data) /
            "FragilX"
        )

    else:

        settings_dir = (
            Path.home() /
            ".fragil_x"
        )

    settings_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return settings_dir / "settings.json"


SETTINGS_FILE = get_settings_file()


def load_settings():

    if not SETTINGS_FILE.exists():
        return {}

    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return {}


def save_settings(
    input_folder,
    output_folder
):

    settings = {
        "input_folder": input_folder,
        "output_folder": output_folder
    }

    try:

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                settings,
                file,
                indent=4
            )

    except OSError:

        pass


def safe_filename(name):

    # Quita caracteres que Windows no admite en nombres de archivo
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()


# ============================================================
# Report generation
# ============================================================

def generate_reports(
    input_folder,
    output_folder,
    on_progress
):
    """
    Genera el informe (Word y PDF) de cada PDF de la carpeta.
    Un PDF con problemas no detiene el resto del lote.

    on_progress recibe (actual, total, nombre, error o None).
    Devuelve (generados, [(nombre, error), ...]).
    """

    pdfs = sorted(
        Path(input_folder).glob("*.pdf")
    )

    output_folder = Path(output_folder)

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    generated = 0
    failed = []

    # Una sola instancia de Word para todo el lote
    with WordConverter() as converter:

        for index, pdf in enumerate(pdfs, start=1):

            try:

                data = extract_data(pdf)

                context = build_context(data)

                output_file = (
                    output_folder /
                    safe_filename(
                        f"{context['PROTOCOLO']} {context['PACIENTE']} GENDA.docx"
                    )
                )

                generate_report(
                    TEMPLATE,
                    output_file,
                    context
                )

                converter.convert(output_file)

                generated += 1

                error = None

            except Exception as e:

                error = str(e) or type(e).__name__

                failed.append((pdf.name, error))

            on_progress(
                index,
                len(pdfs),
                pdf.name,
                error
            )

    return generated, failed


# ============================================================
# Application
# ============================================================

class ReportApp(GendaApp):

    def __init__(self):

        super().__init__(
            "FRAGIL X",
            subtitle="Generación de informes",
            size=(820, 780),
            resizable=True,
            app_id="GENDA.FragilX"
        )

        self.messages = queue.Queue()

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()

        self.load_saved_folders()

        self.create_widgets()

        self.after(
            100,
            self.poll_messages
        )

    # ========================================================
    # Settings
    # ========================================================

    def load_saved_folders(self):

        settings = load_settings()

        input_folder = settings.get(
            "input_folder",
            ""
        )

        output_folder = settings.get(
            "output_folder",
            ""
        )

        if (
            input_folder and
            Path(input_folder).is_dir()
        ):

            self.input_folder.set(
                input_folder
            )

        if (
            output_folder and
            Path(output_folder).is_dir()
        ):

            self.output_folder.set(
                output_folder
            )

    def save_folders(self):

        save_settings(
            self.input_folder.get(),
            self.output_folder.get()
        )

    # ========================================================
    # Widgets
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # Folders
        # ----------------------------------------------------

        folders = card(self.body)

        folders.pack(
            fill="x"
        )

        FolderPicker(
            folders,
            "Carpeta de informes PDF",
            self.input_folder,
            dialog_title="Seleccionar carpeta de informes PDF",
            on_change=self.save_folders
        ).pack(
            fill="x",
            padx=20,
            pady=(16, 12)
        )

        FolderPicker(
            folders,
            "Carpeta de salida",
            self.output_folder,
            dialog_title="Seleccionar carpeta de salida",
            on_change=self.save_folders
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # Generate button
        # ----------------------------------------------------

        self.generate_button = primary_button(
            self.body,
            "Generar informes",
            self.start_generation,
            width=240
        )

        self.generate_button.pack(
            pady=(20, 14)
        )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        self.progress = ctk.CTkProgressBar(
            self.body,
            height=10
        )

        self.progress.pack(
            fill="x",
            pady=(0, 6)
        )

        self.progress.set(0)

        self.progress_label = ctk.CTkLabel(
            self.body,
            text="Listo",
            font=font(12),
            text_color=COLORS["muted"]
        )

        self.progress_label.pack(
            pady=(0, 12)
        )

        # ----------------------------------------------------
        # Open output button
        # (packed before the status box so it always stays
        # visible at the bottom)
        # ----------------------------------------------------

        self.open_output_button = secondary_button(
            self.body,
            "Abrir carpeta de salida",
            self.open_output_folder,
            width=220,
            state="disabled"
        )

        self.open_output_button.pack(
            side="bottom",
            pady=(16, 0)
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = card(self.body)

        status.pack(
            fill="both",
            expand=True
        )

        section_label(
            status,
            "Estado"
        ).pack(
            anchor="w",
            padx=20,
            pady=(14, 4)
        )

        self.status_box = StatusLog(
            status
        )

        self.status_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 16)
        )

    # ========================================================
    # Open output folder
    # ========================================================

    def open_output_folder(self):

        folder = self.output_folder.get()

        if folder and Path(folder).is_dir():

            os.startfile(folder)

    # ========================================================
    # Start generation
    # ========================================================

    def start_generation(self):

        # Se leen los campos de texto: así también sirve una ruta
        # escrita o pegada a mano, no solo la elegida con "Examinar"
        input_folder = self.input_folder.get().strip()
        output_folder = self.output_folder.get().strip()

        if not input_folder:

            self.show_status(
                "Seleccione una carpeta de informes PDF.",
                "warning"
            )

            return

        if not output_folder:

            self.show_status(
                "Seleccione una carpeta de salida.",
                "warning"
            )

            return

        if not Path(input_folder).is_dir():

            self.show_status(
                "La carpeta de informes PDF no existe.",
                "error"
            )

            return

        if not TEMPLATE.exists():

            self.show_status(
                "No se encontró el template de informes.",
                "error"
            )

            return

        if not any(Path(input_folder).glob("*.pdf")):

            self.show_status(
                "No se encontraron archivos PDF en la carpeta seleccionada.",
                "warning"
            )

            return

        self.save_folders()

        self.status_box.clear()

        self.open_output_button.configure(
            state="disabled"
        )

        self.generate_button.configure(
            state="disabled",
            text="Generando…"
        )

        self.progress.set(0)

        self.progress_label.configure(
            text="Iniciando…"
        )

        thread = threading.Thread(
            target=self.generate_reports_thread,
            args=(
                input_folder,
                output_folder
            ),
            daemon=True
        )

        thread.start()

    # ========================================================
    # Report generation
    # (runs in another thread: it only talks to the window
    # through the queue)
    # ========================================================

    def generate_reports_thread(
        self,
        input_folder,
        output_folder
    ):

        try:

            generated, failed = generate_reports(
                input_folder,
                output_folder,
                on_progress=lambda *args: self.messages.put(
                    ("progress", args)
                )
            )

        except Exception as error:

            # Solo llega acá si no se pudo abrir Word
            self.messages.put((
                "fatal",
                "No se pudo usar Microsoft Word para generar los PDF: "
                f"{error}"
            ))

            return

        self.messages.put(
            ("done", (generated, failed))
        )

    def poll_messages(self):

        try:

            while True:

                kind, value = self.messages.get_nowait()

                if kind == "progress":

                    self.update_progress(*value)

                elif kind == "done":

                    self.generation_finished(*value)

                elif kind == "fatal":

                    self.generation_failed(value)

        except queue.Empty:

            pass

        self.after(
            100,
            self.poll_messages
        )

    # ========================================================
    # Progress
    # ========================================================

    def update_progress(
        self,
        current,
        total,
        filename,
        error
    ):

        self.progress.set(
            current / total
        )

        self.progress_label.configure(
            text=(
                f"Procesado {current} de "
                f"{total}: {filename}"
            )
        )

        if error is None:

            self.show_status(
                f"✓ {filename}",
                "success"
            )

        else:

            self.show_status(
                f"✗ {filename}",
                "error"
            )

    # ========================================================
    # Generation finished
    # ========================================================

    def generation_finished(
        self,
        generated,
        failed
    ):

        self.progress.set(1)

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        self.show_status("")
        self.show_status(
            "==============================",
            "muted"
        )

        if not failed:

            self.show_status(
                "✓ GENERACIÓN COMPLETA",
                "success"
            )

        else:

            self.show_status(
                "⚠ GENERACIÓN COMPLETA CON ERRORES",
                "error"
            )

        self.show_status(
            f"Informes procesados: {generated + len(failed)}"
        )

        self.show_status(
            f"Generados (Word y PDF): {generated}"
        )

        self.show_status(
            f"Errores: {len(failed)}"
        )

        self.show_status(
            "==============================",
            "muted"
        )

        # ----------------------------------------------------
        # Detailed errors
        # ----------------------------------------------------

        if failed:

            self.show_status(
                "Estos PDF no se procesaron y hay que hacerlos a mano:",
                "warning"
            )

        for name, reason in failed:

            self.show_status(
                f"✗ {name}\n"
                f"  Error: {reason}",
                "error"
            )

        # ----------------------------------------------------
        # Final state
        # ----------------------------------------------------

        if not failed:

            self.progress_label.configure(
                text=(
                    f"Completado — "
                    f"{generated} informes generados"
                )
            )

        else:

            self.progress_label.configure(
                text=(
                    f"Completado con errores — "
                    f"{generated} generados, "
                    f"{len(failed)} con error"
                )
            )

        self.reset_buttons(generated)

    def generation_failed(self, message):

        self.progress.set(0)

        self.progress_label.configure(
            text="Ocurrió un error"
        )

        self.show_status(
            f"✗ {message}",
            "error"
        )

        self.reset_buttons(0)

    def reset_buttons(self, generated):

        self.generate_button.configure(
            state="normal",
            text="Generar informes"
        )

        if generated > 0:

            self.open_output_button.configure(
                state="normal"
            )

    # ========================================================
    # Status
    # ========================================================

    def show_status(self, message, kind=None):

        self.status_box.write(
            message,
            kind
        )


# ============================================================
# Run application
# ============================================================

def run_app():

    app = ReportApp()

    app.mainloop()

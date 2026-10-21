from pathlib import Path


WD_FORMAT_PDF = 17


class WordConverter:
    """
    Convierte .docx a .pdf con Microsoft Word.

    Abre una única instancia de Word para todo el lote.
    DispatchEx siempre crea una instancia nueva, así no toca
    los documentos que el usuario tenga abiertos en Word.
    """

    def __enter__(self):

        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()

        try:
            self.word = win32com.client.DispatchEx("Word.Application")
        except Exception:
            pythoncom.CoUninitialize()
            raise

        self.word.Visible = False
        self.word.DisplayAlerts = 0

        return self

    def convert(self, docx_path):

        docx_path = Path(docx_path).resolve()
        pdf_path = docx_path.with_suffix(".pdf")

        doc = self.word.Documents.Open(
            str(docx_path),
            ReadOnly=True
        )

        try:
            doc.SaveAs2(
                str(pdf_path),
                FileFormat=WD_FORMAT_PDF
            )
        finally:
            doc.Close(False)

        return pdf_path

    def __exit__(self, *exc):

        import pythoncom

        try:
            self.word.Quit()
        finally:
            pythoncom.CoUninitialize()

        return False

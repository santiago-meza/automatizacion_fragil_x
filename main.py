from config import REPORTS, OUTPUT, TEMPLATE

from extractor import extract_data
from text_builder import build_context
from generator import generate_report


def main():

    pdfs = sorted(REPORTS.glob("*.pdf"))

    for pdf in pdfs:

        print(f"Procesando {pdf.name}")

        data = extract_data(pdf)

        context = build_context(data)

        output_file = (
            OUTPUT /
            f"{context['PROTOCOLO']} {context['PACIENTE']}.docx"
        )

        generate_report(
            TEMPLATE,
            output_file,
            context
        )

        print(f"Generado: {output_file.name}")


if __name__ == "__main__":
    main()
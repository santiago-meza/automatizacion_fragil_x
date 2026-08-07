from pathlib import Path
import pdfplumber
import re

INPUT = Path("input")


def extract_debug(pdf_path: Path):

    print(f"\nAbriendo: {pdf_path.name}\n")

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start=1):

            print("=" * 80)
            print(f"PAGE {page_num}")
            print("=" * 80)

            tables = page.extract_tables()

            if not tables:
                print("No se encontraron tablas.")
                continue

            for table_num, table in enumerate(tables, start=1):

                print(f"\nTABLE {table_num}\n")

                for row_num, row in enumerate(table, start=1):

                    row = [cell if cell else "" for cell in row]

                    print(f"Row {row_num}:")
                    print(row)

                    text = " | ".join(row)

                    # ---------------------------------------------------
                    # NAME
                    # ---------------------------------------------------

                    if "Name:" in text:

                        print("\n>>> ENCONTRE NAME <<<")
                        print(text)

                        m = re.search(r"Name:\s*(.+?)\s*\|", text)

                        if m:
                            print("Regex OK")
                            print("Paciente:", repr(m.group(1)))
                        else:
                            print("Regex FAILED")

                    # ---------------------------------------------------
                    # CLINIC NO
                    # ---------------------------------------------------

                    if "Clinic No.:" in text:

                        print("\n>>> ENCONTRE CLINIC NO <<<")
                        print(text)

                        m = re.search(
                            r"Clinic No\.\:\s*([A-Z]\d+)",
                            text
                        )

                        if m:
                            print("Regex OK")
                            print("Protocolo:", m.group(1))
                        else:
                            print("Regex FAILED")

                    # ---------------------------------------------------
                    # ALLELES
                    # ---------------------------------------------------

                    if len(row) > 3:

                        if row[0] == "Allele1":

                            print("\n>>> ALLELE1 <<<")
                            print("Repeticiones:", repr(row[2]))
                            print("Tipo:", repr(row[3]))

                        elif row[0] == "Allele2":

                            print("\n>>> ALLELE2 <<<")
                            print("Repeticiones:", repr(row[2]))
                            print("Tipo:", repr(row[3]))

    print("\nFIN\n")


if __name__ == "__main__":

    pdf = INPUT / "prueba.pdf"

    extract_debug(pdf)
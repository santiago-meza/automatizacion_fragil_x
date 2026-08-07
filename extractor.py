from datetime import datetime
import re

import pdfplumber


def parse_patient(name):

    # elimina saltos de línea y espacios múltiples
    name = re.sub(r"\s+", " ", name).strip()

    if "," in name:
        apellido, nombre = name.split(",", 1)
        return f"{apellido.strip()}, {nombre.strip()}"

    return name


def clean_cell(cell):

    if not cell:
        return ""

    return re.sub(r"\s+", " ", cell).strip()


def extract_data(pdf_path):

    data = {
        "PACIENTE": "",
        "PROTOCOLO": "",
        "FECHA": datetime.now().strftime("%d/%m/%Y"),
        "SEXO": "",
        "ALLELES": []
    }

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                for row in table:

                    if not row:
                        continue

                    # limpiar todas las celdas
                    row = [
                        clean_cell(c)
                        for c in row
                    ]

                    text = " | ".join(row)


                    # =========================
                    # PACIENTE
                    # =========================

                    if "Name:" in text:

                        # buscamos dentro de la celda exacta
                        for cell in row:

                            if "Name:" in cell:

                                name = cell.split(
                                    "Name:",
                                    1
                                )[1]

                                data["PACIENTE"] = parse_patient(
                                    name
                                )

                                break


                    # =========================
                    # PROTOCOLO
                    # =========================

                    if "Clinic No.:" in text:

                        m = re.search(
                            r"Clinic No\.:\s*([A-Z]\d+)",
                            text
                        )

                        if m:
                            data["PROTOCOLO"] = m.group(1)


                    # =========================
                    # ALELOS
                    # =========================

                    if row[0] in (
                        "Allele1",
                        "Allele2"
                    ):

                        try:

                            repeat = int(
                                row[2]
                            )

                        except (
                            ValueError,
                            IndexError
                        ):

                            continue


                        allele_type = ""

                        if len(row) > 3:
                            allele_type = row[3]


                        data["ALLELES"].append(
                            {
                                "repeat": repeat,
                                "type": allele_type
                            }
                        )


    # =========================
    # SEXO
    # =========================

    if len(data["ALLELES"]) == 1:

        data["SEXO"] = "Male"

    elif len(data["ALLELES"]) >= 2:

        data["SEXO"] = "Female"

    else:

        data["SEXO"] = ""


    return data
from datetime import datetime
import re
import unicodedata

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

    # NFKC convierte caracteres de ancho completo (p. ej. "＞200") en ">200"
    cell = unicodedata.normalize("NFKC", cell)

    return re.sub(r"\s+", " ", cell).strip()


def parse_repeat(allele, value):
    """
    Devuelve (repeticiones, texto, exacto).

    "32"   -> (32, "32", True)
    ">200" -> (201, ">200", False)
    """

    m = re.fullmatch(r"([<>]?)\s*(\d+)", value)

    if not m:
        raise ValueError(
            f"No se pudo leer el número de repeticiones del {allele}: '{value}'."
        )

    sign, number = m.group(1), int(m.group(2))

    if sign == ">":
        return number + 1, f">{number}", False

    if sign == "<":
        return number - 1, f"<{number}", False

    return number, str(number), True


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
                    # SEXO (informado en el PDF)
                    # =========================

                    m = re.search(
                        r"Gender:\s*(Male|Female)",
                        text,
                        re.IGNORECASE
                    )

                    if m:
                        data["SEXO"] = m.group(1).capitalize()


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

                        if len(row) < 3:
                            raise ValueError(
                                f"No se pudo leer la fila del {row[0]}."
                            )

                        repeat, label, exact = parse_repeat(
                            row[0],
                            row[2]
                        )


                        allele_type = ""

                        if len(row) > 3:
                            allele_type = row[3]


                        data["ALLELES"].append(
                            {
                                "repeat": repeat,
                                "label": label,
                                "exact": exact,
                                "type": allele_type
                            }
                        )


    # =========================
    # SEXO
    # =========================
    # Si el PDF no lo informa, se deduce de la cantidad de alelos.

    if not data["SEXO"]:

        if len(data["ALLELES"]) == 1:
            data["SEXO"] = "Male"

        elif len(data["ALLELES"]) == 2:
            data["SEXO"] = "Female"


    validate(data)

    return data


ALLELE_TYPES = (
    "Normal",
    "Intermediate",
    "Premutation",
    "Full mutation"
)


def validate(data):
    """
    Ante cualquier dato dudoso se rechaza el PDF:
    es preferible armar el informe a mano que emitir uno incorrecto.
    """

    # Import local para evitar import circular
    from text_builder import get_type

    if not data["PACIENTE"]:
        raise ValueError("No se encontró el nombre del paciente.")

    if not data["PROTOCOLO"]:
        raise ValueError("No se encontró el protocolo (Clinic No.).")

    alleles = data["ALLELES"]

    if not alleles:
        raise ValueError("No se encontraron alelos en el PDF.")

    expected = {"Male": 1, "Female": 2}.get(data["SEXO"])

    if expected != len(alleles):
        raise ValueError(
            f"Se encontraron {len(alleles)} alelo(s) para sexo "
            f"'{data['SEXO'] or 'desconocido'}'."
        )

    for number, allele in enumerate(alleles, start=1):

        if allele["type"] not in ALLELE_TYPES:
            raise ValueError(
                f"Tipo de alelo no reconocido en el alelo {number}: "
                f"'{allele['type']}'."
            )

        if get_type(allele["repeat"]) != allele["type"]:
            raise ValueError(
                f"El alelo {number} ({allele['label']} repeticiones) figura como "
                f"'{allele['type']}', que no coincide con los rangos de referencia."
            )

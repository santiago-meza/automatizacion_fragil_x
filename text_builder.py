TYPE_TEXT = {
    "Normal": "dentro del rango normal de repeticiones",
    "Intermediate": "dentro de la zona gris de repeticiones",
    "Premutation": "dentro del rango de repeticiones de alelos pre-mutados",
    "Full mutation": "dentro del rango full mutado de repeticiones"
}


def build_phrase_1(alleles):

    if len(alleles) == 1:

        return (
            f"se detectó un alelo "
            f"{TYPE_TEXT[alleles[0]['type']]}"
        )

    t1 = alleles[0]["type"]
    t2 = alleles[1]["type"]

    if t1 == t2:

        mapping = {

            "Normal":
            "se detectaron dos alelos dentro del rango normal de repeticiones",

            "Intermediate":
            "se detectaron dos alelos dentro de la zona gris de repeticiones",

            "Premutation":
            "se detectaron dos alelos dentro del rango de repeticiones de alelos pre-mutados",

            "Full mutation":
            "se detectaron dos alelos dentro del rango full mutado de repeticiones"
        }

        return mapping[t1]

    return (
        f"se detectó un alelo {TYPE_TEXT[t1]} "
        f"y un alelo {TYPE_TEXT[t2]}"
    )


def build_phrase_2(alleles):

    if len(alleles) != 2:
        return ""

    if alleles[0]["repeat"] == alleles[1]["repeat"]:

        return (
            "Mediante el Kit Amplidex FMR1 PCR, "
            "se descartó la presencia de los alelos "
            "en el rango expandido"
        )

    return ""


def build_context(data):

    data["REPETICIONES"] = ", ".join(
        str(a["repeat"])
        for a in data["ALLELES"]
    )

    data["RESULTADO"] = "/".join(
        a["type"]
        for a in data["ALLELES"]
    )

    data["FRASE_1"] = build_phrase_1(
        data["ALLELES"]
    )

    data["FRASE_2"] = build_phrase_2(
        data["ALLELES"]
    )

    return data
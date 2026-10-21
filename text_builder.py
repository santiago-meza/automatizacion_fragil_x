TYPE_TEXT = {
    "Normal": "dentro del rango normal de repeticiones",
    "Intermediate": "dentro del rango normal, correspondiente a la zona gris de repeticiones",
    "Premutation": "dentro del rango de repeticiones de alelos pre-mutados",
    "Full mutation": "dentro del rango full mutado de repeticiones"
}


def get_type(repeat):
    """
    Clasificación de los alelos según el número de repeticiones:

    Normal:
        6-44

    Intermediate / zona gris:
        45-54
        Sigue considerándose un resultado normal,
        pero se encuentra próximo al límite.

    Premutation:
        55-200

    Full mutation:
        201 en adelante
    """

    if 6 <= repeat < 45:
        return "Normal"

    elif 45 <= repeat < 55:
        return "Intermediate"

    elif 55 <= repeat <= 200:
        return "Premutation"

    elif repeat >= 201:
        return "Full mutation"

    return None


def build_phrase_1(alleles):

    # =====================================================
    # UN SOLO ALELO
    # =====================================================

    if len(alleles) == 1:

        allele_type = alleles[0]["type"]

        if allele_type == "Normal":
            return (
                "se detectó un alelo "
                "dentro del rango normal de repeticiones"
            )

        if allele_type == "Intermediate":
            return (
                "se detectó un alelo dentro del rango normal, "
                "correspondiente a la zona gris de repeticiones"
            )

        if allele_type == "Premutation":
            return (
                "se detectó un alelo "
                "dentro del rango de repeticiones de alelos pre-mutados"
            )

        if allele_type == "Full mutation":
            return (
                "se detectó un alelo "
                "dentro del rango full mutado de repeticiones"
            )

        return ""

    # =====================================================
    # DOS ALELOS
    # =====================================================

    if len(alleles) == 2:

        types = {
            alleles[0]["type"],
            alleles[1]["type"]
        }

        # -------------------------------------------------
        # NORMAL + NORMAL
        # -------------------------------------------------

        if types == {"Normal"}:
            return (
                "se detectaron dos alelos "
                "dentro del rango normal de repeticiones"
            )

        # -------------------------------------------------
        # NORMAL + INTERMEDIATE
        #
        # Ambos siguen siendo normales.
        # Uno de ellos está en la zona gris.
        # -------------------------------------------------

        if types == {"Normal", "Intermediate"}:
            return (
                "se detectaron dos alelos dentro del rango normal, "
                "uno de ellos correspondiente a la zona gris, "
                "de repeticiones"
            )

        # -------------------------------------------------
        # INTERMEDIATE + INTERMEDIATE
        #
        # Ambos siguen siendo normales,
        # pero ambos están dentro de la zona gris.
        # -------------------------------------------------

        if types == {"Intermediate"}:
            return (
                "se detectaron dos alelos dentro del rango normal, "
                "correspondientes a la zona gris, de repeticiones"
            )

        # -------------------------------------------------
        # NORMAL + PREMUTATION
        # -------------------------------------------------

        if types == {"Normal", "Premutation"}:
            return (
                "se detectaron dos alelos, "
                "uno dentro del rango normal y otro dentro del "
                "rango de pre-mutación de repeticiones"
            )

        # -------------------------------------------------
        # NORMAL + FULL MUTATION
        # -------------------------------------------------

        if types == {"Normal", "Full mutation"}:
            return (
                "se detectaron dos alelos, "
                "uno dentro del rango normal y otro dentro del "
                "rango full mutado de repeticiones"
            )

        # -------------------------------------------------
        # INTERMEDIATE + PREMUTATION
        #
        # Intermediate sigue siendo normal,
        # pero se especifica que está en zona gris.
        # -------------------------------------------------

        if types == {"Intermediate", "Premutation"}:
            return (
                "se detectaron dos alelos, "
                "uno dentro del rango normal, correspondiente a la "
                "zona gris, y otro dentro del rango de pre-mutación "
                "de repeticiones"
            )

        # -------------------------------------------------
        # INTERMEDIATE + FULL MUTATION
        # -------------------------------------------------

        if types == {"Intermediate", "Full mutation"}:
            return (
                "se detectaron dos alelos, "
                "uno dentro del rango normal, correspondiente a la "
                "zona gris, y otro dentro del rango full mutado "
                "de repeticiones"
            )

        # -------------------------------------------------
        # PREMUTATION + PREMUTATION
        # -------------------------------------------------

        if types == {"Premutation"}:
            return (
                "se detectaron dos alelos "
                "dentro del rango de repeticiones de alelos pre-mutados"
            )

        # -------------------------------------------------
        # PREMUTATION + FULL MUTATION
        # -------------------------------------------------

        if types == {"Premutation", "Full mutation"}:
            return (
                "se detectaron dos alelos, "
                "uno dentro del rango de pre-mutación y otro "
                "dentro del rango full mutado de repeticiones"
            )

        # -------------------------------------------------
        # FULL MUTATION + FULL MUTATION
        # -------------------------------------------------

        if types == {"Full mutation"}:
            return (
                "se detectaron dos alelos "
                "dentro del rango full mutado de repeticiones"
            )

        # -------------------------------------------------
        # COMBINACIÓN NO CONTEMPLADA
        # -------------------------------------------------

        return (
            f"se detectó un alelo {TYPE_TEXT[alleles[0]['type']]} "
            f"y un alelo {TYPE_TEXT[alleles[1]['type']]}"
        )

    return ""


def build_phrase_2(alleles):

    if len(alleles) != 2:
        return ""

    # Solo con valores exactos: ">200" / ">200" no indica homocigosis
    if (
        alleles[0]["exact"]
        and alleles[1]["exact"]
        and alleles[0]["repeat"] == alleles[1]["repeat"]
    ):
        return (
            "Mediante el Kit Amplidex FMR1 PCR, "
            "se descartó la presencia de los alelos "
            "en el rango expandido"
        )

    return ""


def build_context(data):

    data["REPETICIONES"] = ", ".join(
        a["label"]
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
import re
import unicodedata

PALABRAS_BASE = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiuno": 21, "veintiun": 21, "veintidos": 22,
    "veintitres": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90,
    "cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300,
    "cuatrocientos": 400, "quinientos": 500, "seiscientos": 600,
    "setecientos": 700, "ochocientos": 800, "novecientos": 900,
}

MULTIPLICADORES = {"mil": 1000}

PALABRAS_IGNORADAS = {"y", "de", "el", "la", "puntaje", "puntos", "punto"}


def normalizarTexto(texto):
    """Pasa a minusculas y elimina tildes para poder comparar palabras."""
    textoMinuscula = texto.lower().strip()
    textoDescompuesto = unicodedata.normalize("NFD", textoMinuscula)
    textoSinTildes = "".join(
        caracter for caracter in textoDescompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return textoSinTildes


def textoANumero(texto):
    """Retorna el entero contenido en el texto o None si no se puede interpretar.

    Acepta tanto digitos ("45") como palabras ("cuarenta y cinco").
    """
    if not texto:
        return None

    textoNormalizado = normalizarTexto(texto)

    coincidenciaDigitos = re.search(r"-?\d+", textoNormalizado)
    if coincidenciaDigitos:
        return int(coincidenciaDigitos.group())

    total = 0
    parcial = 0
    seEncontroNumero = False

    for palabra in textoNormalizado.split():
        if palabra in PALABRAS_IGNORADAS:
            continue

        if palabra in PALABRAS_BASE:
            parcial += PALABRAS_BASE[palabra]
            seEncontroNumero = True
        elif palabra in MULTIPLICADORES:
            parcial = (parcial if parcial > 0 else 1) * MULTIPLICADORES[palabra]
            total += parcial
            parcial = 0
            seEncontroNumero = True
        else:
            return None

    if not seEncontroNumero:
        return None

    return total + parcial

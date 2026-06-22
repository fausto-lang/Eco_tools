import re
from collections import Counter
import unicodedata
from .ia import inicializar, generar_respuesta


def esta_vacio(texto):
    return len(texto.strip()) == 0


def tiene_numeros(texto):
    return bool(re.search(r"\d", texto))


def tiene_caracteres_especiales(texto):
    return bool(re.search(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", texto))


def es_solo_letras(texto):
    return bool(re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+", texto))


def tiene_mayusculas(texto):
    return bool(re.search(r"[A-ZÁÉÍÓÚÑ]", texto))


def tiene_minusculas(texto):
    return bool(re.search(r"[a-záéíóúñ]", texto))


def contar_palabras(texto):
    return len(texto.split())


def contar_oraciones(texto):
    return len(re.findall(r"[.!?]+", texto))


def contar_caracteres(texto):
    return len(texto)


def empieza_en_mayuscula(texto):
    texto = texto.strip()
    return texto[0].isupper() if texto else False


def termina_con_puntuacion(texto):
    return bool(re.search(r"[.!?]$", texto.strip()))


def doble_espaciado(texto):
    return "  " in texto


def palabras_repetidas(texto):
    return bool(re.search(r"\b(\w+)\s+\1\b", texto, re.IGNORECASE))


def verificar_estructura_basica(texto):
    errors = []

    if not empieza_en_mayuscula(texto):
        errors.append("El textoo no comienza con mayúscula")

    if not termina_con_puntuacion(texto):
        errors.append("El textoo no termina con puntuación")

    if doble_espaciado(texto):
        errors.append("El textoo tiene espacios dobles")

    if palabras_repetidas(texto):
        errors.append("El textoo tiene palabras repetidas")

    return {
        "valido": len(errors) == 0,
        "errores": errors
    }


def buscar_email(texto):
    return re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", texto)


def buscar_url(texto):
    return re.findall(r"https?://[^\s]+", texto)


def buscar_numero_celular(texto):
    return re.findall(r"\+?\d[\d\s-]{7,}\d", texto)


def buscar_fechas(texto):
    return re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", texto)


def remover_espacios_extra(texto):
    return re.sub(r"\s+", " ", texto).strip()


def remover_caracteres_especiales(texto):
    return re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", texto)


def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = remover_espacios_extra(texto)

    return texto


def tokenizar_palabras(texto):
    return re.findall(r"\b\w+\b", texto)


def tokenizar_oraciones(texto):
    return re.split(r"(?<=[.!?])\s+", texto.strip())


def obtener_palabras_mas_comunes(texto, top=5):
    palabras = tokenizar_palabras(normalizar_texto(texto))

    contador = Counter(palabras)

    return contador.most_common(top)


def riqueza_lexica(texto):
    palabras = tokenizar_palabras(normalizar_texto(texto))

    if not palabras:
        return 0

    palabras_unicas = set(palabras)

    return len(palabras_unicas) / len(palabras)


def puntaje_legibilidad(texto):
    palabras = contar_palabras(texto)
    oraciones = contar_oraciones(texto)

    if oraciones == 0:
        return 0

    return palabras / oraciones


def validar(texto, reglas):
    errors = []

    for regla in reglas:
        resultado = regla(texto)

        if resultado is False:
            errors.append(regla.__name__)

    return {
        "valido": len(errors) == 0,
        "errores": errors
    }


def extraer(texto, reglas):
    resultados = []

    for regla in reglas:
        resultados.extend(regla(texto))

    return resultados


def extraer_ia(texto, instruccion):
    cliente, modelo = inicializar()

    prompt = f"""
    Extrae del siguiente texto únicamente:
    {instruccion}

    Texto:
    {texto}

    Devuelve los resultados separados con un espacio
    """

    respuesta = generar_respuesta(cliente, modelo, prompt)

    return respuesta["texto"]


def coincide_regla(texto, patron):
    return bool(re.search(patron, texto))

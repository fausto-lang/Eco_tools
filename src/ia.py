import os
from io import BytesIO
import requests
import magic
import PIL.Image
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


def inicializar():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY en el .env")

    cliente = genai.Client(api_key=api_key)

    models = list(cliente.models.list())
    modelo = next(
        (m.name for m in models if "flash" in m.name.lower()),
        models[0].name
    )

    return cliente, modelo


def obtener_recurso(ruta_o_url):
    try:
        if ruta_o_url.startswith(("http://", "https://")):
            res = requests.get(
                ruta_o_url,
                timeout=10,
                headers={"User-Agent": "pimble/1.0"}
            )
            res.raise_for_status()
            datos = res.content
            mime = magic.from_buffer(datos, mime=True)
        else:
            if not os.path.exists(ruta_o_url):
                raise FileNotFoundError(f"No existe: {ruta_o_url}")

            with open(ruta_o_url, "rb") as f:
                datos = f.read()

            mime = magic.from_file(ruta_o_url, mime=True)

        return datos, mime

    except Exception as e:
        raise RuntimeError(f"Error obteniendo recurso: {e}")


def generar_respuesta(cliente, modelo, prompt, archivos=None):
    contenido = [prompt]
    errores = []

    if archivos:
        for ruta in archivos:
            try:
                datos, mime = obtener_recurso(ruta)

                if mime.startswith("image"):
                    try:
                        img = PIL.Image.open(BytesIO(datos))
                        contenido.append(img)
                    except Exception:
                        errores.append(f"Imagen inválida: {ruta}")

                elif mime.startswith("audio"):
                    contenido.append(
                        types.Part.from_bytes(data=datos, mime_type=mime)
                    )

                else:
                    errores.append(f"Formato no soportado: {mime}")

            except Exception as e:
                errores.append(str(e))

    try:
        res = cliente.models.generate_content(
            model=modelo,
            contents=contenido
        )

        return {
            "texto": res.text,
            "tokens": res.usage_metadata.total_token_count,
            "estado": "success",
            "errores": errores
        }

    except errors.ClientError:
        return {
            "texto": "Error de cuota o API",
            "estado": "error",
            "errores": errores
        }

    except Exception as e:
        return {
            "texto": f"Error crítico: {e}",
            "estado": "error",
            "errores": errores
        }

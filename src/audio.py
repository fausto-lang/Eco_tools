import os
import pyttsx3
import sounddevice as sd
import soundfile as sf
import numpy as np
import speech_recognition as sr
from pydub import AudioSegment

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "spanish" in voice.name.lower() or "es-ES" in voice.id:
        engine.setProperty('voice', voice.id)
        break


def hablar(texto):
    try:
        engine.setProperty('rate', 150)
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR TTS]: {e}")


def hay_microfono():
    try:
        dispositivos = sd.query_devices()

        for d in dispositivos:
            if d["max_input_channels"] > 0:
                return True

        return False

    except Exception:
        return False


def reconocer():
    if not hay_microfono():
        return "No hay micrófono conectado"

    frecuencia = 44100
    canales = 1

    frames = []

    try:

        def callback(indata, frames_count, time, status):
            if status:
                print(status)

            frames.append(indata.copy())

        print("Habla ahora...")
        print("Presiona ENTER para finalizar\n")

        with sd.InputStream(
            samplerate=frecuencia,
            channels=canales,
            dtype='int16',
            callback=callback
        ):

            input()

        if not frames:
            return "No se capturó audio"

        grabacion = np.concatenate(frames, axis=0)

        archivo_temp = "temp_audio.wav"

        sf.write(
            archivo_temp,
            grabacion,
            frecuencia
        )

        reconocedor = sr.Recognizer()

        with sr.AudioFile(archivo_temp) as source:
            audio = reconocedor.record(source)

        texto = reconocedor.recognize_google(
            audio,
            language="es-ES"
        )

        os.remove(archivo_temp)

        return texto

    except sr.UnknownValueError:
        return "No se entendió el audio"

    except sr.RequestError:
        return "Error con el servicio de reconocimiento"

    except Exception as e:
        return f"Error: {e}"


def grabar(nombre_archivo):
    if not hay_microfono():
        print("No hay micrófono conectado")
        return

    frecuencia = 44100
    canales = 1

    print("Grabando...")
    print("Presiona Ctrl+C para finalizar")

    frames = []

    try:

        stream = sd.InputStream(
            samplerate=frecuencia,
            channels=canales,
            dtype='int16'
        )

        stream.start()

        while True:

            data, overflowed = stream.read(1024)

            if overflowed:
                print("Overflow detectado")

            frames.append(data)

    except KeyboardInterrupt:
        print("\nFinalizando grabación...")

    except Exception as e:
        print(f"Error grabando: {e}")
        return

    finally:
        try:
            stream.stop()
            stream.close()
        except:
            pass

    if not frames:
        print("No se grabó audio")
        return

    try:

        grabacion = np.concatenate(frames, axis=0)

        archivo_wav = nombre_archivo + ".wav"

        sf.write(
            archivo_wav,
            grabacion,
            frecuencia
        )

        audio_segment = AudioSegment.from_wav(
            archivo_wav
        )

        archivo_mp3 = nombre_archivo + ".mp3"

        audio_segment.export(
            archivo_mp3,
            format="mp3"
        )

        os.remove(archivo_wav)

        print("Grabación terminada")

    except Exception as e:
        print(f"Error procesando audio: {e}")

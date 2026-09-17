import speech_recognition as sr

IDIOMA_RECONOCIMIENTO = "es-ES"
SEGUNDOS_ESPERA_INICIO = 6
SEGUNDOS_MAXIMO_FRASE = 6
SEGUNDOS_CALIBRACION = 0.4
UMBRAL_PAUSA = 0.8


class errorVoz(Exception):
    """Error controlado del proceso de reconocimiento de voz."""


class servicioVoz:

    def __init__(self):
        self.reconocedor = sr.Recognizer()
        self.reconocedor.pause_threshold = UMBRAL_PAUSA
        self.reconocedor.dynamic_energy_threshold = True

    def escucharTexto(self):
        """Escucha el microfono y devuelve el texto reconocido."""
        try:
            with sr.Microphone() as fuenteAudio:
                self.reconocedor.adjust_for_ambient_noise(
                    fuenteAudio, duration=SEGUNDOS_CALIBRACION
                )
                audioCapturado = self.reconocedor.listen(
                    fuenteAudio,
                    timeout=SEGUNDOS_ESPERA_INICIO,
                    phrase_time_limit=SEGUNDOS_MAXIMO_FRASE,
                )
        except OSError as error:
            raise errorVoz(
                "No se pudo acceder al microfono. Verifique que este conectado "
                "y habilitado en Windows."
            ) from error
        except sr.WaitTimeoutError as error:
            raise errorVoz("No se detecto audio. Intente nuevamente.") from error

        try:
            textoReconocido = self.reconocedor.recognize_google(
                audioCapturado, language=IDIOMA_RECONOCIMIENTO
            )
        except sr.UnknownValueError as error:
            raise errorVoz("No se entendio lo dictado. Intente nuevamente.") from error
        except sr.RequestError as error:
            raise errorVoz(
                "Sin conexion con el servicio de reconocimiento de voz."
            ) from error

        return textoReconocido.strip()

import os

import firebase_admin
from firebase_admin import credentials, db

NOMBRE_ARCHIVO_CREDENCIALES = "claveCuentaServicio.json"
VARIABLE_ENTORNO_CREDENCIALES = "FIREBASE_CREDENCIALES"
VARIABLE_ENTORNO_URL = "FIREBASE_URL_BASE_DATOS"

URL_BASE_DATOS = "https://verduras-app-76b8a-default-rtdb.firebaseio.com/"

URL_NO_CONFIGURADA = "NOMBRE-DEL-PROYECTO"


def obtenerRutaCredenciales():
    rutaPersonalizada = os.getenv(VARIABLE_ENTORNO_CREDENCIALES)
    if rutaPersonalizada:
        return rutaPersonalizada

    carpetaProyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpetaProyecto, NOMBRE_ARCHIVO_CREDENCIALES)


def obtenerUrlBaseDatos():
    urlPersonalizada = os.getenv(VARIABLE_ENTORNO_URL)
    if urlPersonalizada:
        return urlPersonalizada

    return URL_BASE_DATOS


def inicializarFirebase():
    if not firebase_admin._apps:
        rutaCredenciales = obtenerRutaCredenciales()
        urlBaseDatos = obtenerUrlBaseDatos()

        if not os.path.exists(rutaCredenciales):
            raise FileNotFoundError(
                "No se encontro el archivo de credenciales en: "
                f"{rutaCredenciales}\n\n"
                "Descargue la clave privada desde la consola de Firebase "
                "(Configuracion del proyecto -> Cuentas de servicio) y guardela "
                f"con el nombre {NOMBRE_ARCHIVO_CREDENCIALES}."
            )

        if URL_NO_CONFIGURADA in urlBaseDatos:
            raise ValueError(
                "La URL de la Realtime Database no esta configurada. "
                "Edite URL_BASE_DATOS en configuracion/configuracionFirebase.py "
                "o defina la variable de entorno "
                f"{VARIABLE_ENTORNO_URL}."
            )

        credencial = credentials.Certificate(rutaCredenciales)
        firebase_admin.initialize_app(credencial, {"databaseURL": urlBaseDatos})

    return db.reference("/")

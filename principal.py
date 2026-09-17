import tkinter as tk
from tkinter import messagebox

from configuracion.configuracionFirebase import inicializarFirebase
from interfaz.ventanaPrincipal import ventanaPrincipal
from servicios.servicioVerduras import servicioVerduras
from servicios.servicioVoz import servicioVoz


def mostrarErrorInicio(mensajeError):
    ventanaError = tk.Tk()
    ventanaError.withdraw()
    messagebox.showerror("Error de conexion", mensajeError)
    ventanaError.destroy()


def ejecutarAplicacion():
    try:
        referenciaRaiz = inicializarFirebase()
    except Exception as error:
        mostrarErrorInicio(str(error))
        return

    servicioVerdurasInstancia = servicioVerduras(referenciaRaiz)
    servicioVozInstancia = servicioVoz()

    aplicacion = ventanaPrincipal(servicioVerdurasInstancia, servicioVozInstancia)
    aplicacion.iniciar()


if __name__ == "__main__":
    ejecutarAplicacion()

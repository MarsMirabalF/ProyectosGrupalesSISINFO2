import threading
import tkinter as tk
from tkinter import messagebox, ttk

from servicios.servicioVoz import errorVoz
from utilidades.conversorNumeros import textoANumero

TITULO_VENTANA = "Tabla Verdura"
ANCHO_VENTANA = 640
ALTO_VENTANA = 440
ANCHO_MINIMO = 560
ALTO_MINIMO = 380

ESPACIADO_BASE = 8
ESPACIADO_DOBLE = 16

COLOR_FONDO = "#FFFFFF"
COLOR_TEXTO = "#1A1A1A"
COLOR_TEXTO_SECUNDARIO = "#6B6B6B"
COLOR_SELECCION = "#D9D9D9"

FUENTE_TABLA = ("Segoe UI", 10)
FUENTE_ENCABEZADO = ("Segoe UI", 10, "bold")
FUENTE_ESTADO = ("Segoe UI", 9)

INTENTOS_MAXIMOS_PUNTAJE = 2
FILAS_VISIBLES_TABLA = 12
ALTURA_FILA = 28


class ventanaPrincipal:

    def __init__(self, servicioVerdurasInstancia, servicioVozInstancia):
        self.servicioVerduras = servicioVerdurasInstancia
        self.servicioVoz = servicioVozInstancia
        self.capturaEnCurso = False

        self.ventana = tk.Tk()
        self.ventana.title(TITULO_VENTANA)
        self.ventana.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.ventana.minsize(ANCHO_MINIMO, ALTO_MINIMO)
        self.ventana.configure(bg=COLOR_FONDO)

        self.construirEstilos()
        self.construirInterfaz()
        self.actualizarTabla()

    def construirEstilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TButton", font=FUENTE_TABLA, padding=ESPACIADO_BASE)
        estilo.configure(
            "Treeview",
            font=FUENTE_TABLA,
            rowheight=ALTURA_FILA,
            background=COLOR_FONDO,
            fieldbackground=COLOR_FONDO,
            foreground=COLOR_TEXTO,
            borderwidth=0,
        )
        estilo.configure(
            "Treeview.Heading", font=FUENTE_ENCABEZADO, padding=ESPACIADO_BASE
        )
        estilo.map(
            "Treeview",
            background=[("selected", COLOR_SELECCION)],
            foreground=[("selected", COLOR_TEXTO)],
        )

    def construirInterfaz(self):
        marcoPrincipal = ttk.Frame(self.ventana, padding=ESPACIADO_DOBLE)
        marcoPrincipal.pack(fill="both", expand=True)
        marcoPrincipal.columnconfigure(0, weight=1)
        marcoPrincipal.rowconfigure(0, weight=1)

        self.construirTabla(marcoPrincipal)
        self.construirBotones(marcoPrincipal)
        self.construirEstado(marcoPrincipal)

    def construirTabla(self, contenedor):
        marcoTabla = ttk.Frame(contenedor)
        marcoTabla.grid(row=0, column=0, sticky="nsew")
        marcoTabla.columnconfigure(0, weight=1)
        marcoTabla.rowconfigure(0, weight=1)

        columnasTabla = ("posicion", "nombre", "puntaje")
        self.tablaVerduras = ttk.Treeview(
            marcoTabla,
            columns=columnasTabla,
            show="headings",
            height=FILAS_VISIBLES_TABLA,
            selectmode="browse",
        )

        self.tablaVerduras.heading("posicion", text="Posicion")
        self.tablaVerduras.heading("nombre", text="Nombre")
        self.tablaVerduras.heading("puntaje", text="Puntaje")

        self.tablaVerduras.column("posicion", width=96, anchor="center", stretch=False)
        self.tablaVerduras.column("nombre", width=320, anchor="w")
        self.tablaVerduras.column("puntaje", width=96, anchor="center", stretch=False)

        barraDesplazamiento = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self.tablaVerduras.yview
        )
        self.tablaVerduras.configure(yscrollcommand=barraDesplazamiento.set)

        self.tablaVerduras.grid(row=0, column=0, sticky="nsew")
        barraDesplazamiento.grid(row=0, column=1, sticky="ns")

    def construirBotones(self, contenedor):
        marcoBotones = ttk.Frame(contenedor)
        marcoBotones.grid(row=1, column=0, sticky="ew", pady=(ESPACIADO_DOBLE, 0))
        marcoBotones.columnconfigure(0, weight=1)
        marcoBotones.columnconfigure(1, weight=1)
        marcoBotones.columnconfigure(2, weight=1)

        self.botonAgregarVoz = ttk.Button(
            marcoBotones,
            text="Agregar por voz",
            command=self.iniciarCapturaVoz,
        )
        self.botonAgregarVoz.grid(row=0, column=0, sticky="ew", padx=(0, ESPACIADO_BASE))

        self.botonEliminar = ttk.Button(
            marcoBotones,
            text="Eliminar seleccionado",
            command=self.eliminarSeleccionado,
        )
        self.botonEliminar.grid(row=0, column=1, sticky="ew", padx=ESPACIADO_BASE)

        self.botonRecargar = ttk.Button(
            marcoBotones,
            text="Recargar",
            command=self.actualizarTabla,
        )
        self.botonRecargar.grid(row=0, column=2, sticky="ew", padx=(ESPACIADO_BASE, 0))

    def construirEstado(self, contenedor):
        self.textoEstado = tk.StringVar(value="Listo.")
        self.etiquetaEstado = ttk.Label(
            contenedor,
            textvariable=self.textoEstado,
            font=FUENTE_ESTADO,
            foreground=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
        )
        self.etiquetaEstado.grid(row=2, column=0, sticky="ew", pady=(ESPACIADO_BASE, 0))

    # ------------------------------------------------------------------
    # Tabla
    # ------------------------------------------------------------------
    def actualizarTabla(self):
        for filaExistente in self.tablaVerduras.get_children():
            self.tablaVerduras.delete(filaExistente)

        try:
            listaVerduras = self.servicioVerduras.listarVerduras()
        except Exception as error:
            self.mostrarEstado(f"Error al leer los datos: {error}")
            return

        for verdura in listaVerduras:
            self.tablaVerduras.insert(
                "",
                "end",
                iid=verdura["clave"],
                values=(verdura["posicion"], verdura["nombre"], verdura["puntaje"]),
            )

        self.mostrarEstado(f"{len(listaVerduras)} registro(s) en la tabla.")

    def iniciarCapturaVoz(self):
        if self.capturaEnCurso:
            return

        self.capturaEnCurso = True
        self.cambiarEstadoBotones("disabled")

        hiloCaptura = threading.Thread(target=self.capturarDatosPorVoz, daemon=True)
        hiloCaptura.start()

    def capturarDatosPorVoz(self):
        try:
            self.mostrarEstado("Escuchando... diga el NOMBRE de la verdura.")
            nombreDictado = self.servicioVoz.escucharTexto()

            if not nombreDictado:
                self.mostrarEstado("No se capturo ningun nombre.")
                return

            nombreVerdura = nombreDictado.capitalize()
            puntajeVerdura = None

            for numeroIntento in range(1, INTENTOS_MAXIMOS_PUNTAJE + 1):
                self.mostrarEstado(f"Nombre: {nombreVerdura}. Ahora diga el PUNTAJE.")
                textoPuntaje = self.servicioVoz.escucharTexto()
                puntajeVerdura = textoANumero(textoPuntaje)

                if puntajeVerdura is not None:
                    break

                if numeroIntento < INTENTOS_MAXIMOS_PUNTAJE:
                    self.mostrarEstado("No se entendio el puntaje, repitalo por favor.")

            if puntajeVerdura is None:
                self.mostrarEstado("No se pudo interpretar el puntaje dictado.")
                return

            self.ventana.after(0, self.confirmarYGuardar, nombreVerdura, puntajeVerdura)
        except errorVoz as error:
            self.mostrarEstado(str(error))
        except Exception as error:
            self.mostrarEstado(f"Error inesperado: {error}")
        finally:
            self.ventana.after(0, self.finalizarCapturaVoz)

    def confirmarYGuardar(self, nombreVerdura, puntajeVerdura):
        seConfirma = messagebox.askyesno(
            "Confirmar registro",
            f"Nombre: {nombreVerdura}\nPuntaje: {puntajeVerdura}\n\nDesea guardarlo?",
        )

        if not seConfirma:
            self.mostrarEstado("Registro cancelado.")
            return

        try:
            self.servicioVerduras.agregarVerdura(nombreVerdura, puntajeVerdura)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo guardar el registro:\n{error}")
            return

        self.actualizarTabla()
        self.mostrarEstado(f"Registro guardado: {nombreVerdura} ({puntajeVerdura}).")

    def finalizarCapturaVoz(self):
        self.capturaEnCurso = False
        self.cambiarEstadoBotones("normal")

    def eliminarSeleccionado(self):
        seleccion = self.tablaVerduras.selection()

        if not seleccion:
            self.mostrarEstado("Seleccione una fila de la tabla para eliminarla.")
            return

        claveVerdura = seleccion[0]
        valoresFila = self.tablaVerduras.item(claveVerdura, "values")
        nombreVerdura = valoresFila[1]

        seConfirma = messagebox.askyesno(
            "Confirmar eliminacion",
            f"Desea eliminar el registro '{nombreVerdura}'?",
        )

        if not seConfirma:
            return

        try:
            self.servicioVerduras.eliminarVerdura(claveVerdura)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo eliminar el registro:\n{error}")
            return

        self.actualizarTabla()
        self.mostrarEstado(f"Registro '{nombreVerdura}' eliminado.")
        
    def cambiarEstadoBotones(self, estadoBoton):
        self.botonAgregarVoz.configure(state=estadoBoton)
        self.botonEliminar.configure(state=estadoBoton)
        self.botonRecargar.configure(state=estadoBoton)

    def mostrarEstado(self, mensaje):
        """Actualiza la etiqueta de estado de forma segura desde cualquier hilo."""
        self.ventana.after(0, self.textoEstado.set, mensaje)

    def iniciar(self):
        self.ventana.mainloop()

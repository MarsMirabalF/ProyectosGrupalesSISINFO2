import threading
import tkinter as tk
from tkinter import messagebox, ttk

from servicios.servicioVoz import errorVoz
from utilidades.conversorNumeros import textoANumero

TITULO_VENTANA = "Tabla Verdura"
SUBTITULO_VENTANA = "Registro de verduras por voz"
ANCHO_VENTANA = 720
ALTO_VENTANA = 520
ANCHO_MINIMO = 620
ALTO_MINIMO = 440

ESPACIADO_MINIMO = 4
ESPACIADO_BASE = 8
ESPACIADO_DOBLE = 16
ESPACIADO_TRIPLE = 24

# Tipografía: Cambria para títulos y encabezados de tabla; Segoe UI para texto normal; Segoe UI Semibold para botones
# Tamaños de fuente: títulos 20px, subtítulos 11px, texto normal 11px, texto pequeño 9px
FUENTE_TITULO = ("Cambria", 20, "bold")
FUENTE_SUBTITULO = ("Cambria", 11)
FUENTE_ENCABEZADO_TABLA = ("Cambria", 11, "bold")
FUENTE_TEXTO = ("Segoe UI", 11)
FUENTE_TEXTO_PEQUENO = ("Segoe UI", 9)
FUENTE_BOTON = ("Segoe UI Semibold", 10)

# Paleta de colores: 5 colores base
# #2C3B2E (verde bosque oscuro): header, botones principales, texto general y mensajes de éxito
# #F7F3E9 (crema marfil): fondo principal de la ventana y texto sobre el header oscuro
# #6B7C6E (verde grisáceo): textos secundarios y mensajes de estado neutros
# #A9BBA0 (verde salvia): bordes, fila seleccionada y acentos interactivos
# #B3541E (terracota): mensajes de error
COLOR_PRIMARIO = "#2C3B2E"
COLOR_FONDO = "#F7F3E9"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"

INTENTOS_MAXIMOS_PUNTAJE = 2
FILAS_VISIBLES_TABLA = 12
ALTURA_FILA = 30
GROSOR_BORDE = 1


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
        estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_PRIMARIO)

        estilo.configure(
            "TButton",
            font=FUENTE_BOTON,
            padding=(ESPACIADO_DOBLE, ESPACIADO_BASE),
            background=COLOR_PRIMARIO,
            foreground=COLOR_FONDO,
            borderwidth=0,
            relief="flat",
            focuscolor=COLOR_ACENTO,
        )
        estilo.map(
            "TButton",
            background=[("active", COLOR_ACENTO), ("disabled", COLOR_FONDO)],
            foreground=[("active", COLOR_PRIMARIO), ("disabled", COLOR_SECUNDARIO)],
        )

        estilo.configure(
            "Secundario.TButton",
            font=FUENTE_BOTON,
            padding=(ESPACIADO_DOBLE, ESPACIADO_BASE),
            background=COLOR_FONDO,
            foreground=COLOR_PRIMARIO,
            borderwidth=GROSOR_BORDE,
            relief="solid",
            bordercolor=COLOR_ACENTO,
            focuscolor=COLOR_ACENTO,
        )
        estilo.map(
            "Secundario.TButton",
            background=[("active", COLOR_ACENTO), ("disabled", COLOR_FONDO)],
            foreground=[("disabled", COLOR_SECUNDARIO)],
        )

        estilo.configure(
            "Dictado.TButton",
            font=FUENTE_TEXTO_PEQUENO,
            padding=(ESPACIADO_BASE, ESPACIADO_MINIMO),
            background=COLOR_FONDO,
            foreground=COLOR_PRIMARIO,
            borderwidth=GROSOR_BORDE,
            relief="solid",
            bordercolor=COLOR_ACENTO,
            focuscolor=COLOR_ACENTO,
        )
        estilo.map(
            "Dictado.TButton",
            background=[("active", COLOR_ACENTO), ("disabled", COLOR_FONDO)],
            foreground=[("disabled", COLOR_SECUNDARIO)],
        )

        estilo.configure(
            "Treeview",
            font=FUENTE_TEXTO,
            rowheight=ALTURA_FILA,
            background=COLOR_FONDO,
            fieldbackground=COLOR_FONDO,
            foreground=COLOR_PRIMARIO,
            borderwidth=0,
        )
        estilo.configure(
            "Treeview.Heading",
            font=FUENTE_ENCABEZADO_TABLA,
            padding=ESPACIADO_BASE,
            background=COLOR_PRIMARIO,
            foreground=COLOR_FONDO,
            relief="flat",
        )
        estilo.map("Treeview.Heading", background=[("active", COLOR_PRIMARIO)])
        estilo.map(
            "Treeview",
            background=[("selected", COLOR_ACENTO)],
            foreground=[("selected", COLOR_PRIMARIO)],
        )

    def construirInterfaz(self):
        self.construirEncabezado()

        marcoPrincipal = ttk.Frame(self.ventana, padding=ESPACIADO_TRIPLE)
        marcoPrincipal.pack(fill="both", expand=True)
        marcoPrincipal.columnconfigure(0, weight=1)
        marcoPrincipal.rowconfigure(0, weight=1)

        self.construirTabla(marcoPrincipal)
        self.construirBotones(marcoPrincipal)
        self.construirEstado(marcoPrincipal)

    def construirEncabezado(self):
        marcoEncabezado = tk.Frame(self.ventana, bg=COLOR_PRIMARIO)
        marcoEncabezado.pack(fill="x")

        contenedorTextos = tk.Frame(marcoEncabezado, bg=COLOR_PRIMARIO)
        contenedorTextos.pack(
            fill="x", padx=ESPACIADO_TRIPLE, pady=(ESPACIADO_DOBLE, ESPACIADO_BASE)
        )

        etiquetaTitulo = tk.Label(
            contenedorTextos,
            text=TITULO_VENTANA,
            font=FUENTE_TITULO,
            bg=COLOR_PRIMARIO,
            fg=COLOR_FONDO,
            anchor="w",
        )
        etiquetaTitulo.pack(fill="x")

        etiquetaSubtitulo = tk.Label(
            contenedorTextos,
            text=SUBTITULO_VENTANA,
            font=FUENTE_SUBTITULO,
            bg=COLOR_PRIMARIO,
            fg=COLOR_ACENTO,
            anchor="w",
        )
        etiquetaSubtitulo.pack(fill="x", pady=(0, ESPACIADO_MINIMO))

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

        self.tablaVerduras.column("posicion", width=100, anchor="center", stretch=False)
        self.tablaVerduras.column("nombre", width=340, anchor="w")
        self.tablaVerduras.column("puntaje", width=100, anchor="center", stretch=False)

        barraDesplazamiento = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self.tablaVerduras.yview
        )
        self.tablaVerduras.configure(yscrollcommand=barraDesplazamiento.set)

        self.tablaVerduras.grid(row=0, column=0, sticky="nsew")
        barraDesplazamiento.grid(row=0, column=1, sticky="ns")

        self.tablaVerduras.bind("<Double-1>", self.abrirEdicionAlDobleClic)

    def construirBotones(self, contenedor):
        marcoBotones = ttk.Frame(contenedor)
        marcoBotones.grid(row=1, column=0, sticky="ew", pady=(ESPACIADO_DOBLE, 0))
        for indiceColumna in range(4):
            marcoBotones.columnconfigure(indiceColumna, weight=1)

        self.botonAgregarVoz = ttk.Button(
            marcoBotones,
            text="Agregar por voz",
            command=self.iniciarCapturaVoz,
        )
        self.botonAgregarVoz.grid(row=0, column=0, sticky="ew", padx=(0, ESPACIADO_BASE))

        self.botonEditar = ttk.Button(
            marcoBotones,
            text="Editar seleccionado",
            style="Secundario.TButton",
            command=self.editarSeleccionado,
        )
        self.botonEditar.grid(row=0, column=1, sticky="ew", padx=ESPACIADO_BASE)

        self.botonEliminar = ttk.Button(
            marcoBotones,
            text="Eliminar seleccionado",
            style="Secundario.TButton",
            command=self.eliminarSeleccionado,
        )
        self.botonEliminar.grid(row=0, column=2, sticky="ew", padx=ESPACIADO_BASE)

        self.botonRecargar = ttk.Button(
            marcoBotones,
            text="Recargar",
            style="Secundario.TButton",
            command=self.actualizarTabla,
        )
        self.botonRecargar.grid(row=0, column=3, sticky="ew", padx=(ESPACIADO_BASE, 0))

    def construirEstado(self, contenedor):
        self.textoEstado = tk.StringVar(value="Listo.")
        self.etiquetaEstado = tk.Label(
            contenedor,
            textvariable=self.textoEstado,
            font=FUENTE_TEXTO_PEQUENO,
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            anchor="w",
        )
        self.etiquetaEstado.grid(row=2, column=0, sticky="ew", pady=(ESPACIADO_BASE, 0))

    def actualizarTabla(self):
        for filaExistente in self.tablaVerduras.get_children():
            self.tablaVerduras.delete(filaExistente)

        try:
            listaVerduras = self.servicioVerduras.listarVerduras()
        except Exception as error:
            self.mostrarEstado(f"Error al leer los datos: {error}", tipo="error")
            return

        for verdura in listaVerduras:
            self.tablaVerduras.insert(
                "",
                "end",
                iid=verdura["clave"],
                values=(verdura["posicion"], verdura["nombre"], verdura["puntaje"]),
            )

        self.mostrarEstado(f"{len(listaVerduras)} registro(s) en la tabla.")

    def obtenerSeleccion(self):
        seleccion = self.tablaVerduras.selection()
        if not seleccion:
            return None

        claveVerdura = seleccion[0]
        valoresFila = self.tablaVerduras.item(claveVerdura, "values")
        return claveVerdura, valoresFila[1], valoresFila[2]

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
                self.mostrarEstado("No se capturo ningun nombre.", tipo="error")
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
                self.mostrarEstado("No se pudo interpretar el puntaje dictado.", tipo="error")
                return

            self.ventana.after(0, self.confirmarYGuardar, nombreVerdura, puntajeVerdura)
        except errorVoz as error:
            self.mostrarEstado(str(error), tipo="error")
        except Exception as error:
            self.mostrarEstado(f"Error inesperado: {error}", tipo="error")
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
        self.mostrarEstado(f"Registro guardado: {nombreVerdura} ({puntajeVerdura}).", tipo="exito")

    def finalizarCapturaVoz(self):
        self.capturaEnCurso = False
        self.cambiarEstadoBotones("normal")

    def abrirEdicionAlDobleClic(self, evento):
        self.editarSeleccionado()

    def editarSeleccionado(self):
        seleccionActual = self.obtenerSeleccion()

        if not seleccionActual:
            self.mostrarEstado("Seleccione una fila de la tabla para editarla.")
            return

        claveVerdura, nombreActual, puntajeActual = seleccionActual
        self.abrirDialogoEdicion(claveVerdura, nombreActual, puntajeActual)

    def abrirDialogoEdicion(self, claveVerdura, nombreActual, puntajeActual):
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Editar verdura")
        dialogo.configure(bg=COLOR_FONDO)
        dialogo.resizable(False, False)
        dialogo.transient(self.ventana)
        dialogo.grab_set()

        marco = ttk.Frame(dialogo, padding=ESPACIADO_TRIPLE)
        marco.pack(fill="both", expand=True)

        tk.Label(
            marco, text="Editar verdura", font=FUENTE_TITULO,
            bg=COLOR_FONDO, fg=COLOR_PRIMARIO, anchor="w",
        ).pack(fill="x", pady=(0, ESPACIADO_DOBLE))

        ttk.Label(marco, text="Nombre", font=FUENTE_TEXTO).pack(fill="x")

        subMarcoNombre = tk.Frame(marco, bg=COLOR_FONDO)
        subMarcoNombre.pack(fill="x", pady=(ESPACIADO_MINIMO, ESPACIADO_DOBLE))

        variableNombre = tk.StringVar(value=nombreActual)
        entradaNombre = tk.Entry(
            subMarcoNombre, textvariable=variableNombre, font=FUENTE_TEXTO,
            bg="white", fg=COLOR_PRIMARIO, relief="solid",
            highlightthickness=GROSOR_BORDE, highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_PRIMARIO, bd=0,
        )
        entradaNombre.pack(side="left", fill="x", expand=True, ipady=ESPACIADO_BASE)

        ttk.Label(marco, text="Puntaje", font=FUENTE_TEXTO).pack(fill="x")

        subMarcoPuntaje = tk.Frame(marco, bg=COLOR_FONDO)
        subMarcoPuntaje.pack(fill="x", pady=(ESPACIADO_MINIMO, ESPACIADO_BASE))

        variablePuntaje = tk.StringVar(value=str(puntajeActual))
        entradaPuntaje = tk.Entry(
            subMarcoPuntaje, textvariable=variablePuntaje, font=FUENTE_TEXTO,
            bg="white", fg=COLOR_PRIMARIO, relief="solid",
            highlightthickness=GROSOR_BORDE, highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_PRIMARIO, bd=0,
        )
        entradaPuntaje.pack(side="left", fill="x", expand=True, ipady=ESPACIADO_BASE)

        tk.Label(
            marco,
            text="La posicion se calcula sola segun el puntaje y no se puede editar.",
            font=FUENTE_TEXTO_PEQUENO, bg=COLOR_FONDO, fg=COLOR_SECUNDARIO,
            anchor="w", wraplength=380, justify="left",
        ).pack(fill="x", pady=(0, ESPACIADO_DOBLE))

        etiquetaEstadoDialogo = tk.Label(
            marco, text="", font=FUENTE_TEXTO_PEQUENO, bg=COLOR_FONDO, fg=COLOR_SECUNDARIO,
            anchor="w",
        )
        etiquetaEstadoDialogo.pack(fill="x")

        marcoBotonesDialogo = ttk.Frame(marco)
        marcoBotonesDialogo.pack(fill="x", pady=(ESPACIADO_DOBLE, 0))
        marcoBotonesDialogo.columnconfigure(0, weight=1)
        marcoBotonesDialogo.columnconfigure(1, weight=1)

        botonesDialogo = []

        def guardarCambios():
            nuevoNombre = variableNombre.get().strip()
            nuevoPuntaje = textoANumero(variablePuntaje.get())

            if not nuevoNombre:
                etiquetaEstadoDialogo.configure(text="El nombre no puede quedar vacio.", fg=COLOR_ERROR)
                return

            if nuevoPuntaje is None:
                etiquetaEstadoDialogo.configure(text="El puntaje debe ser un numero.", fg=COLOR_ERROR)
                return

            try:
                self.servicioVerduras.actualizarVerdura(claveVerdura, nuevoNombre, nuevoPuntaje)
            except Exception as error:
                etiquetaEstadoDialogo.configure(text=f"No se pudo guardar: {error}", fg=COLOR_ERROR)
                return

            dialogo.destroy()
            self.actualizarTabla()
            self.mostrarEstado(f"Registro actualizado: {nuevoNombre} ({nuevoPuntaje}).", tipo="exito")

        botonDictarNombre = ttk.Button(
            subMarcoNombre, text="Dictar", style="Dictado.TButton",
            command=lambda: self.iniciarDictadoCampo(
                dialogo, variableNombre, etiquetaEstadoDialogo, esNumero=False, botones=botonesDialogo
            ),
        )
        botonDictarNombre.pack(side="left", padx=(ESPACIADO_BASE, 0))

        botonDictarPuntaje = ttk.Button(
            subMarcoPuntaje, text="Dictar", style="Dictado.TButton",
            command=lambda: self.iniciarDictadoCampo(
                dialogo, variablePuntaje, etiquetaEstadoDialogo, esNumero=True, botones=botonesDialogo
            ),
        )
        botonDictarPuntaje.pack(side="left", padx=(ESPACIADO_BASE, 0))

        botonCancelar = ttk.Button(
            marcoBotonesDialogo, text="Cancelar", style="Secundario.TButton",
            command=dialogo.destroy,
        )
        botonCancelar.grid(row=0, column=0, sticky="ew", padx=(0, ESPACIADO_BASE))

        botonGuardar = ttk.Button(
            marcoBotonesDialogo, text="Guardar", command=guardarCambios,
        )
        botonGuardar.grid(row=0, column=1, sticky="ew", padx=(ESPACIADO_BASE, 0))

        botonesDialogo.extend([
            botonDictarNombre, botonDictarPuntaje, botonCancelar, botonGuardar
        ])

        entradaNombre.focus_set()
        dialogo.bind("<Return>", lambda evento: guardarCambios())

    def iniciarDictadoCampo(self, dialogo, variableDestino, etiquetaEstadoDialogo, esNumero, botones):
        if self.capturaEnCurso:
            return

        self.capturaEnCurso = True
        for boton in botones:
            boton.configure(state="disabled")

        etiquetaEstadoDialogo.configure(
            text="Escuchando... diga el nuevo puntaje." if esNumero else "Escuchando... diga el nuevo nombre.",
            fg=COLOR_SECUNDARIO,
        )

        hiloCaptura = threading.Thread(
            target=self.capturarCampoPorVoz,
            args=(dialogo, variableDestino, etiquetaEstadoDialogo, esNumero, botones),
            daemon=True,
        )
        hiloCaptura.start()

    def capturarCampoPorVoz(self, dialogo, variableDestino, etiquetaEstadoDialogo, esNumero, botones):
        try:
            textoDictado = self.servicioVoz.escucharTexto()

            if esNumero:
                numeroCapturado = textoANumero(textoDictado)
                if numeroCapturado is None:
                    self.actualizarEtiquetaDialogo(
                        dialogo, etiquetaEstadoDialogo, "No se entendio el puntaje, intente de nuevo.", COLOR_ERROR
                    )
                else:
                    self.actualizarVariableDialogo(dialogo, variableDestino, str(numeroCapturado))
                    self.actualizarEtiquetaDialogo(dialogo, etiquetaEstadoDialogo, "Puntaje capturado.", COLOR_PRIMARIO)
            else:
                if not textoDictado:
                    self.actualizarEtiquetaDialogo(
                        dialogo, etiquetaEstadoDialogo, "No se capturo ningun nombre.", COLOR_ERROR
                    )
                else:
                    nombreCapturado = textoDictado.strip().capitalize()
                    self.actualizarVariableDialogo(dialogo, variableDestino, nombreCapturado)
                    self.actualizarEtiquetaDialogo(dialogo, etiquetaEstadoDialogo, "Nombre capturado.", COLOR_PRIMARIO)
        except errorVoz as error:
            self.actualizarEtiquetaDialogo(dialogo, etiquetaEstadoDialogo, str(error), COLOR_ERROR)
        except Exception as error:
            self.actualizarEtiquetaDialogo(dialogo, etiquetaEstadoDialogo, f"Error inesperado: {error}", COLOR_ERROR)
        finally:
            self.capturaEnCurso = False
            self.reactivarBotonesDialogo(dialogo, botones)

    def actualizarVariableDialogo(self, dialogo, variableDestino, valorNuevo):
        if dialogo.winfo_exists():
            dialogo.after(0, variableDestino.set, valorNuevo)

    def actualizarEtiquetaDialogo(self, dialogo, etiqueta, mensaje, color):
        if dialogo.winfo_exists():
            dialogo.after(0, lambda: etiqueta.configure(text=mensaje, fg=color))

    def reactivarBotonesDialogo(self, dialogo, botones):
        if dialogo.winfo_exists():
            dialogo.after(0, lambda: [boton.configure(state="normal") for boton in botones])

    def eliminarSeleccionado(self):
        seleccionActual = self.obtenerSeleccion()

        if not seleccionActual:
            self.mostrarEstado("Seleccione una fila de la tabla para eliminarla.")
            return

        claveVerdura, nombreVerdura, _ = seleccionActual

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
        self.mostrarEstado(f"Registro '{nombreVerdura}' eliminado.", tipo="exito")

    def cambiarEstadoBotones(self, estadoBoton):
        self.botonAgregarVoz.configure(state=estadoBoton)
        self.botonEditar.configure(state=estadoBoton)
        self.botonEliminar.configure(state=estadoBoton)
        self.botonRecargar.configure(state=estadoBoton)

    def mostrarEstado(self, mensaje, tipo="info"):
        colorPorTipo = {
            "info": COLOR_SECUNDARIO,
            "exito": COLOR_PRIMARIO,
            "error": COLOR_ERROR,
        }
        colorTexto = colorPorTipo.get(tipo, COLOR_SECUNDARIO)

        self.ventana.after(0, self.textoEstado.set, mensaje)
        self.ventana.after(0, lambda: self.etiquetaEstado.configure(fg=colorTexto))

    def iniciar(self):
        self.ventana.mainloop()
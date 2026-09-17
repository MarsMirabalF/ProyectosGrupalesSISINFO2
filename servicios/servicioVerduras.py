NOMBRE_NODO = "verduras"
CAMPO_NOMBRE = "nombre"
CAMPO_PUNTAJE = "puntaje"


class servicioVerduras:

    def __init__(self, referenciaRaiz):
        self.referenciaVerduras = referenciaRaiz.child(NOMBRE_NODO)

    def agregarVerdura(self, nombre, puntaje):
        registro = {
            CAMPO_NOMBRE: nombre.strip(),
            CAMPO_PUNTAJE: int(puntaje),
        }
        referenciaNueva = self.referenciaVerduras.push(registro)
        return referenciaNueva.key

    def listarVerduras(self):
        datosCrudos = self.referenciaVerduras.get()

        if not datosCrudos:
            return []

        listaVerduras = []
        for claveRegistro, registro in datosCrudos.items():
            if not isinstance(registro, dict):
                continue

            listaVerduras.append({
                "clave": claveRegistro,
                "nombre": registro.get(CAMPO_NOMBRE, ""),
                "puntaje": int(registro.get(CAMPO_PUNTAJE, 0)),
            })

        listaVerduras.sort(key=lambda verdura: verdura["puntaje"])

        for indice, verdura in enumerate(listaVerduras, start=1):
            verdura["posicion"] = indice

        return listaVerduras

    def eliminarVerdura(self, claveVerdura):
        """Elimina el registro indicado por su clave."""
        self.referenciaVerduras.child(claveVerdura).delete()

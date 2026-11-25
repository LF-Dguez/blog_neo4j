"""
Componentes de interfaz que comparten todas las pestanas.

PestanaCRUD es la base de cada pestana de administracion (Usuarios,
Articulos, Comentarios, Tags y Categorias). Arma la misma distribucion:

    +-----------------------------+----------------------+
    | tabla con los registros     | formulario           |
    | (se elige uno con un clic)  | [Nuevo] [Guardar]    |
    |                             | [Eliminar]           |
    +-----------------------------+----------------------+

Cada pestana hereda de PestanaCRUD y define:
    titulo, columnas, campos            -> que se muestra
    listar(), crear(), actualizar(),    -> el Cypher de cada operacion
    eliminar()
y, si necesita controles extra (por ejemplo, elegir el autor de un
articulo), sobrescribe crear_extras(), cargar_extras(), leer_extras() y
limpiar_extras().
"""
import re
import tkinter as tk
from tkinter import messagebox, ttk

FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Selector(ttk.Combobox):
    """Combobox que muestra un texto y guarda el id del nodo elegido."""

    def __init__(self, padre, **kw):
        super().__init__(padre, state="readonly", **kw)
        self._ids = []

    def cargar(self, opciones):
        """opciones: lista de (id, texto)."""
        self._ids = [i for i, _ in opciones]
        self["values"] = [t for _, t in opciones]
        self.set("")

    def elegir(self, id_):
        self.current(self._ids.index(id_)) if id_ in self._ids else self.set("")

    def id_elegido(self):
        i = self.current()
        return self._ids[i] if i >= 0 else None


class ListaMultiple(ttk.Frame):
    """Lista con seleccion multiple que guarda los ids elegidos."""

    def __init__(self, padre, alto=5):
        super().__init__(padre)
        self.lista = tk.Listbox(self, selectmode="multiple", height=alto,
                                exportselection=False)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self._ids = []

    def cargar(self, opciones):
        self._ids = [i for i, _ in opciones]
        self.lista.delete(0, "end")
        for _, texto in opciones:
            self.lista.insert("end", texto)

    def elegir(self, ids):
        self.lista.selection_clear(0, "end")
        for i, id_ in enumerate(self._ids):
            if id_ in (ids or []):
                self.lista.selection_set(i)

    def ids_elegidos(self):
        return [self._ids[i] for i in self.lista.curselection()]


class PestanaCRUD(ttk.Frame):
    """Base de una pestana de administracion de un tipo de nodo."""

    titulo = ""
    # (clave del resultado, encabezado, ancho en pixeles)
    columnas = []
    # (clave, etiqueta, tipo) con tipo "texto", "fecha" o "parrafo"
    campos = []

    def __init__(self, padre, bd):
        super().__init__(padre, padding=10)
        self.bd = bd
        self.filas = {}          # id -> fila completa de listar()
        self.id_actual = None    # id del registro elegido (None = nuevo)
        self._armar()
        self.refrescar()

    # ------------------------------------------------------------------
    # Metodos que define cada pestana
    # ------------------------------------------------------------------
    def listar(self):
        """Regresa una lista de diccionarios; cada uno debe tener 'id'."""
        raise NotImplementedError

    def crear(self, datos):
        raise NotImplementedError

    def actualizar(self, id_, datos):
        raise NotImplementedError

    def eliminar(self, id_):
        raise NotImplementedError

    def crear_extras(self, marco, fila):
        """Agrega controles extra al formulario a partir de la fila 'fila'.
        Regresa la siguiente fila libre del grid."""
        return fila

    def cargar_extras(self, registro):
        pass

    def leer_extras(self, datos):
        """Agrega a 'datos' los valores de los controles extra."""
        pass

    def limpiar_extras(self):
        pass

    def actualizar_opciones(self):
        """Recarga los combos/listas que dependen de otros nodos."""
        pass

    # ------------------------------------------------------------------
    # Interfaz
    # ------------------------------------------------------------------
    def _armar(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text=self.titulo, style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Tabla
        marco_tabla = ttk.Frame(self)
        marco_tabla.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        marco_tabla.rowconfigure(0, weight=1)
        marco_tabla.columnconfigure(0, weight=1)
        self.tabla = ttk.Treeview(marco_tabla, show="headings", selectmode="browse",
                                  columns=[c for c, _, _ in self.columnas])
        for clave, encabezado, ancho in self.columnas:
            self.tabla.heading(clave, text=encabezado)
            self.tabla.column(clave, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.bind("<<TreeviewSelect>>", self._al_elegir)
        self.total = ttk.Label(marco_tabla, text="")
        self.total.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Formulario
        marco = ttk.LabelFrame(self, text="Datos", padding=10)
        marco.grid(row=1, column=1, sticky="nsew")
        marco.columnconfigure(1, weight=1)
        self.entradas = {}
        fila = 0
        for clave, etiqueta, tipo in self.campos:
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="nw",
                                                 pady=3, padx=(0, 6))
            if tipo == "parrafo":
                control = tk.Text(marco, height=6, width=34, wrap="word")
            else:
                control = ttk.Entry(marco, width=36)
            control.grid(row=fila, column=1, sticky="ew", pady=3)
            self.entradas[clave] = (control, tipo)
            fila += 1
        fila = self.crear_extras(marco, fila)

        botones = ttk.Frame(marco)
        botones.grid(row=fila, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        ttk.Button(botones, text="Nuevo", command=self.limpiar).pack(side="left")
        ttk.Button(botones, text="Guardar", command=self._guardar).pack(
            side="left", padx=6)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).pack(side="left")
        self.aviso = ttk.Label(marco, text="", foreground="#371E49")
        self.aviso.grid(row=fila + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------------
    # Comportamiento comun
    # ------------------------------------------------------------------
    def refrescar(self, elegir=None):
        """Vuelve a leer los registros de Neo4j y redibuja la tabla."""
        self.actualizar_opciones()
        self.tabla.delete(*self.tabla.get_children())
        self.filas = {}
        for registro in self.listar():
            self.filas[registro["id"]] = registro
            valores = []
            for clave, _, _ in self.columnas:
                valor = registro.get(clave, "")
                if isinstance(valor, list):
                    valor = ", ".join(str(v) for v in valor)
                valores.append("" if valor is None else valor)
            self.tabla.insert("", "end", iid=registro["id"], values=valores)
        self.total.configure(text=f"{len(self.filas)} registros")
        if elegir in self.filas:
            self.tabla.selection_set(elegir)
            self.tabla.see(elegir)
        else:
            self.limpiar()

    def limpiar(self):
        self.id_actual = None
        self.tabla.selection_remove(self.tabla.selection())
        for control, tipo in self.entradas.values():
            if tipo == "parrafo":
                control.delete("1.0", "end")
            else:
                control.delete(0, "end")
        self.limpiar_extras()
        self.aviso.configure(text="Nuevo registro")

    def _al_elegir(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.id_actual = seleccion[0]
        registro = self.filas[self.id_actual]
        for clave, (control, tipo) in self.entradas.items():
            valor = registro.get(clave) or ""
            if tipo == "parrafo":
                control.delete("1.0", "end")
                control.insert("1.0", valor)
            else:
                control.delete(0, "end")
                control.insert(0, valor)
        self.cargar_extras(registro)
        self.aviso.configure(text="Editando el registro elegido")

    def _leer(self):
        datos = {}
        for clave, (control, tipo) in self.entradas.items():
            valor = (control.get("1.0", "end") if tipo == "parrafo"
                     else control.get()).strip()
            if not valor:
                raise ValueError(f"Falta el campo '{clave}'.")
            if tipo == "fecha" and not FECHA.match(valor):
                raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
            datos[clave] = valor
        self.leer_extras(datos)
        return datos

    def _avisar(self, texto):
        """Muestra un aviso despues de que la tabla termina de actualizarse."""
        self.after(100, lambda: self.aviso.configure(text=texto))

    def _guardar(self):
        try:
            datos = self._leer()
            if self.id_actual is None:
                nuevo = self.crear(datos)
                self.refrescar(elegir=nuevo)
                self._avisar("Registro creado")
            else:
                id_ = self.id_actual
                self.actualizar(id_, datos)
                self.refrescar(elegir=id_)
                self._avisar("Registro actualizado")
        except ValueError as e:
            messagebox.showwarning(self.titulo, str(e))
        except Exception as e:  # errores de Neo4j, por ejemplo un email repetido
            messagebox.showerror(self.titulo, f"No se pudo guardar:\n{e}")

    def _eliminar(self):
        if self.id_actual is None:
            messagebox.showinfo(self.titulo, "Elige un registro de la tabla.")
            return
        if not messagebox.askyesno(self.titulo, "¿Eliminar el registro elegido?"):
            return
        try:
            self.eliminar(self.id_actual)
            self.refrescar()
            self._avisar("Registro eliminado")
        except ValueError as e:
            messagebox.showwarning(self.titulo, str(e))
        except Exception as e:
            messagebox.showerror(self.titulo, f"No se pudo eliminar:\n{e}")

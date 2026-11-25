"""
Aplicacion para administrar un blog guardado en Neo4j.

Ejecutar desde la raiz del repositorio:
    python app/main.py

Abre una ventana con una pestana por cada tipo de nodo del blog y una de
consultas. Cada pestana vive en su propio modulo; si un modulo todavia no
existe, su pestana simplemente no aparece.
"""
import importlib
import tkinter as tk
from tkinter import messagebox, ttk

from conexion import BaseDatos

# (modulo, clase, texto de la pestana)
PESTANAS = [
    ("usuarios", "PestanaUsuarios", "Usuarios"),
    ("articulos", "PestanaArticulos", "Artículos"),
    ("comentarios", "PestanaComentarios", "Comentarios"),
    ("tags", "PestanaTags", "Tags"),
    ("categorias", "PestanaCategorias", "Categorías"),
    ("consultas", "PestanaConsultas", "Consultas"),
]

MORADO = "#371E49"


class Aplicacion(tk.Tk):
    def __init__(self, bd, version):
        super().__init__()
        self.bd = bd
        self.title("Blog en Neo4j")
        self.geometry("1250x680")
        self.minsize(1000, 560)
        self._estilos()

        encabezado = tk.Frame(self, bg=MORADO)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="Blog en Neo4j", bg=MORADO, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=14, pady=8)
        datos = f"Conectado a {version}  |  {bd.uri}  |  base '{bd.database}'"
        tk.Label(encabezado, text=datos, bg=MORADO, fg="#E5DDEC").pack(
            side="right", padx=14)

        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=8, pady=8)
        for modulo, clase, texto in PESTANAS:
            try:
                pestana = getattr(importlib.import_module(modulo), clase)
            except ModuleNotFoundError as e:
                if e.name == modulo:      # la pestana aun no existe
                    continue
                raise
            self.cuaderno.add(pestana(self.cuaderno, bd), text=texto)

        # Al cambiar de pestana se recargan sus datos, porque otra pestana
        # pudo haber creado o borrado nodos relacionados.
        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"),
                         foreground=MORADO)
        estilo.configure("Treeview", rowheight=24)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _al_cambiar(self, _evento):
        pestana = self.nametowidget(self.cuaderno.select())
        if hasattr(pestana, "refrescar"):
            pestana.refrescar()

    def _cerrar(self):
        self.bd.cerrar()
        self.destroy()


def main():
    try:
        bd = BaseDatos()
        version = bd.verificar()
    except Exception as e:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Blog en Neo4j",
                             f"No se pudo conectar con Neo4j:\n\n{e}\n\n"
                             "Revisa que la base este iniciada en Neo4j Desktop "
                             "y los datos de config.ini.")
        raiz.destroy()
        return
    Aplicacion(bd, version).mainloop()


if __name__ == "__main__":
    main()

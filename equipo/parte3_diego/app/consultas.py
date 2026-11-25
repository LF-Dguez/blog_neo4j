"""
Pestana Consultas: consultas de solo lectura que recorren el grafo.

Cada consulta tiene un nombre, una descripcion, su Cypher y, si lo
necesita, un parametro que se elige en la interfaz (un tag o un articulo).
El resultado se muestra en una tabla cuyas columnas son las del RETURN.
Las mismas consultas estan en cypher/06_consultas.cypher para ejecutarlas
en Neo4j Browser.
"""
import tkinter as tk
from tkinter import messagebox, ttk

from ui_comun import Selector

# Opciones para los parametros: (Cypher que regresa id y texto, etiqueta)
PARAMETROS = {
    "tag": ("MATCH (t:Tag) RETURN t.id AS id, t.name AS texto ORDER BY texto",
            "Tag"),
    "articulo": ("MATCH (a:Article) RETURN a.id AS id, a.title AS texto "
                 "ORDER BY texto", "Artículo"),
}

CONSULTAS = [
    {
        "nombre": "1. Artículos por categoría",
        "descripcion": "Cuántos artículos tiene cada categoría.",
        "parametro": None,
        "cypher": """MATCH (c:Category)
OPTIONAL MATCH (a:Article)-[:IN_CATEGORY]->(c)
RETURN c.name AS categoria, count(a) AS articulos
ORDER BY articulos DESC, categoria""",
    },
    {
        "nombre": "2. Tags más usados",
        "descripcion": "En cuántos artículos aparece cada tag.",
        "parametro": None,
        "cypher": """MATCH (t:Tag)
RETURN t.name AS tag, COUNT { (:Article)-[:TAGGED_WITH]->(t) } AS articulos
ORDER BY articulos DESC, tag""",
    },
    {
        "nombre": "3. Artículos más comentados",
        "descripcion": "Cada artículo con su autor y su número de comentarios.",
        "parametro": None,
        "cypher": """MATCH (u:User)-[:WROTE]->(a:Article)
RETURN a.title AS articulo, u.name AS autor,
       COUNT { (a)-[:HAS_COMMENT]->(:Comment) } AS comentarios
ORDER BY comentarios DESC, articulo""",
    },
    {
        "nombre": "4. Actividad de cada usuario",
        "descripcion": "Artículos escritos y comentarios publicados por usuario.",
        "parametro": None,
        "cypher": """MATCH (u:User)
RETURN u.name AS usuario,
       COUNT { (u)-[:WROTE]->(:Article) } AS articulos,
       COUNT { (u)-[:POSTED]->(:Comment) } AS comentarios
ORDER BY articulos + comentarios DESC, usuario""",
    },
    {
        "nombre": "5. Artículos de un tag",
        "descripcion": "Los artículos que tienen el tag elegido, con su autor.",
        "parametro": "tag",
        "cypher": """MATCH (t:Tag {id: $parametro})<-[:TAGGED_WITH]-(a:Article)
MATCH (u:User)-[:WROTE]->(a)
RETURN a.title AS articulo, u.name AS autor, a.date AS fecha
ORDER BY fecha DESC""",
    },
    {
        "nombre": "6. Artículos relacionados",
        "descripcion": "Artículos que comparten tags con el artículo elegido.",
        "parametro": "articulo",
        "cypher": """MATCH (a:Article {id: $parametro})-[:TAGGED_WITH]->(t:Tag)
      <-[:TAGGED_WITH]-(otro:Article)
RETURN otro.title AS relacionado, collect(t.name) AS tags_en_comun,
       count(t) AS en_comun
ORDER BY en_comun DESC, relacionado""",
    },
    {
        "nombre": "7. Quién comenta a quién",
        "descripcion": "Usuarios que comentan artículos de otros usuarios.",
        "parametro": None,
        "cypher": """MATCH (lector:User)-[:POSTED]->(:Comment)
      <-[:HAS_COMMENT]-(:Article)<-[:WROTE]-(autor:User)
WHERE lector <> autor
RETURN lector.name AS lector, autor.name AS autor, count(*) AS comentarios
ORDER BY comentarios DESC, lector""",
    },
    {
        "nombre": "8. Artículos sin comentarios",
        "descripcion": "Artículos que todavía no tienen ningún comentario.",
        "parametro": None,
        "cypher": """MATCH (u:User)-[:WROTE]->(a:Article)
WHERE NOT EXISTS { (a)-[:HAS_COMMENT]->(:Comment) }
RETURN a.title AS articulo, u.name AS autor, a.date AS fecha
ORDER BY fecha""",
    },
]


class PestanaConsultas(ttk.Frame):
    def __init__(self, padre, bd):
        super().__init__(padre, padding=10)
        self.bd = bd
        self._armar()

    def _armar(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        ttk.Label(self, text="Consultas", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        barra = ttk.Frame(self)
        barra.grid(row=1, column=0, sticky="ew")
        ttk.Label(barra, text="Consulta").pack(side="left")
        self.lista = ttk.Combobox(barra, state="readonly", width=34,
                                  values=[c["nombre"] for c in CONSULTAS])
        self.lista.pack(side="left", padx=6)
        self.lista.bind("<<ComboboxSelected>>", self._al_elegir)
        self.etiqueta_param = ttk.Label(barra, text="")
        self.etiqueta_param.pack(side="left", padx=(10, 4))
        self.param = Selector(barra, width=36)
        self.param.pack(side="left")
        ttk.Button(barra, text="Ejecutar", command=self.ejecutar).pack(
            side="left", padx=10)

        self.descripcion = ttk.Label(self, text="")
        self.descripcion.grid(row=2, column=0, sticky="w", pady=6)

        medio = ttk.Panedwindow(self, orient="vertical")
        medio.grid(row=3, column=0, sticky="nsew")
        marco_tabla = ttk.Frame(medio)
        marco_tabla.rowconfigure(0, weight=1)
        marco_tabla.columnconfigure(0, weight=1)
        self.tabla = ttk.Treeview(marco_tabla, show="headings")
        barra_v = ttk.Scrollbar(marco_tabla, orient="vertical",
                                command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_v.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        self.total = ttk.Label(marco_tabla, text="")
        self.total.grid(row=1, column=0, sticky="w", pady=(4, 0))
        medio.add(marco_tabla, weight=3)

        marco_cypher = ttk.LabelFrame(medio, text="Cypher", padding=6)
        self.cypher = tk.Text(marco_cypher, height=6, font=("Consolas", 10),
                              wrap="none")
        self.cypher.pack(fill="both", expand=True)
        medio.add(marco_cypher, weight=1)

        self.lista.current(0)
        self._al_elegir()

    def refrescar(self):
        """Al volver a la pestana se recargan las opciones del parametro."""
        self._al_elegir()

    def _actual(self):
        return CONSULTAS[self.lista.current()]

    def _al_elegir(self, _evento=None):
        consulta = self._actual()
        self.descripcion.configure(text=consulta["descripcion"])
        self.cypher.configure(state="normal")
        self.cypher.delete("1.0", "end")
        self.cypher.insert("1.0", consulta["cypher"])
        self.cypher.configure(state="disabled")
        if consulta["parametro"]:
            cypher, etiqueta = PARAMETROS[consulta["parametro"]]
            self.etiqueta_param.configure(text=etiqueta)
            self.param.configure(state="readonly")
            self.param.cargar([(f["id"], f["texto"])
                               for f in self.bd.consultar(cypher)])
        else:
            self.etiqueta_param.configure(text="")
            self.param.cargar([])
            self.param.configure(state="disabled")
        self.tabla.delete(*self.tabla.get_children())
        self.total.configure(text="")

    def ejecutar(self):
        consulta = self._actual()
        parametros = {}
        if consulta["parametro"]:
            if self.param.id_elegido() is None:
                messagebox.showinfo("Consultas", "Elige un valor para la consulta.")
                return
            parametros["parametro"] = self.param.id_elegido()
        try:
            filas = self.bd.consultar(consulta["cypher"], parametros)
        except Exception as e:
            messagebox.showerror("Consultas", f"Error en la consulta:\n{e}")
            return

        self.tabla.delete(*self.tabla.get_children())
        columnas = list(filas[0].keys()) if filas else []
        self.tabla["columns"] = columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=180, anchor="w")
        for fila in filas:
            valores = [", ".join(map(str, v)) if isinstance(v, list) else v
                       for v in fila.values()]
            self.tabla.insert("", "end", values=valores)
        self.total.configure(text=f"{len(filas)} filas")

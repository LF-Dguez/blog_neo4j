"""
Pestana Comentarios: alta, consulta, modificacion y baja de nodos :Comment.

    (:Comment {id, name, url, text, date})

name es el titulo corto del comentario y url su enlace permanente, que se
arma con el titulo del articulo y el inicio del id del comentario.

Relaciones que administra esta pestana:
    (:User)-[:POSTED]->(:Comment)           quien lo escribio, 1 a N
    (:Article)-[:HAS_COMMENT]->(:Comment)   en que articulo, 1 a N
"""
from tkinter import ttk

from ui_comun import PestanaCRUD, Selector

# Enlace permanente del comentario a partir del titulo del articulo
URL = ('"/articulos/" + toLower(replace(a.title, " ", "-")) + '
       '"#comentario-" + substring(c.id, 0, 8)')


class PestanaComentarios(PestanaCRUD):
    titulo = "Comentarios"
    columnas = [("name", "Título", 150), ("articulo", "Artículo", 220),
                ("autor", "Autor", 120), ("date", "Fecha", 85),
                ("url", "URL", 260)]
    campos = [("name", "Título", "texto"), ("date", "Fecha (AAAA-MM-DD)", "fecha"),
              ("text", "Texto", "parrafo")]

    # ------------------------------------------------------------------
    # Controles extra: autor y articulo
    # ------------------------------------------------------------------
    def crear_extras(self, marco, fila):
        ttk.Label(marco, text="Autor").grid(row=fila, column=0, sticky="w", pady=3)
        self.autor = Selector(marco)
        self.autor.grid(row=fila, column=1, sticky="ew", pady=3)
        ttk.Label(marco, text="Artículo").grid(row=fila + 1, column=0, sticky="w",
                                               pady=3)
        self.articulo = Selector(marco)
        self.articulo.grid(row=fila + 1, column=1, sticky="ew", pady=3)
        return fila + 2

    def actualizar_opciones(self):
        self.autor.cargar([(f["id"], f["name"]) for f in self.bd.consultar(
            "MATCH (u:User) RETURN u.id AS id, u.name AS name ORDER BY u.name")])
        self.articulo.cargar([(f["id"], f["title"]) for f in self.bd.consultar(
            "MATCH (a:Article) RETURN a.id AS id, a.title AS title ORDER BY a.title")])

    def cargar_extras(self, registro):
        self.autor.elegir(registro["autor_id"])
        self.articulo.elegir(registro["articulo_id"])

    def leer_extras(self, datos):
        datos["autor_id"] = self.autor.id_elegido()
        datos["articulo_id"] = self.articulo.id_elegido()
        if datos["autor_id"] is None or datos["articulo_id"] is None:
            raise ValueError("Elige el autor y el artículo del comentario.")

    def limpiar_extras(self):
        self.autor.set("")
        self.articulo.set("")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def listar(self):
        return self.bd.consultar("""
            MATCH (a:Article)-[:HAS_COMMENT]->(c:Comment)
            OPTIONAL MATCH (u:User)-[:POSTED]->(c)
            RETURN c.id AS id, c.name AS name, c.url AS url, c.text AS text,
                   c.date AS date, a.id AS articulo_id, a.title AS articulo,
                   u.id AS autor_id, u.name AS autor
            ORDER BY c.date DESC, c.name
        """)

    def crear(self, datos):
        fila = self.bd.ejecutar(f"""
            MATCH (u:User {{id: $autor_id}}), (a:Article {{id: $articulo_id}})
            CREATE (c:Comment {{id: randomUUID(), name: $name, text: $text,
                               date: date($date)}})
            SET c.url = {URL}
            CREATE (u)-[:POSTED]->(c)
            CREATE (a)-[:HAS_COMMENT]->(c)
            RETURN c.id AS id
        """, datos)
        return fila[0]["id"]

    def actualizar(self, id_, datos):
        parametros = {**datos, "id": id_}
        self.bd.transaccion([
            ("""MATCH (c:Comment {id: $id})
                SET c.name = $name, c.text = $text, c.date = date($date)""",
             parametros),
            # Se quitan el autor y el articulo anteriores y se enlazan los nuevos
            ("""MATCH (c:Comment {id: $id})<-[r:POSTED|HAS_COMMENT]-()
                DELETE r""", parametros),
            (f"""MATCH (c:Comment {{id: $id}}), (u:User {{id: $autor_id}}),
                      (a:Article {{id: $articulo_id}})
                CREATE (u)-[:POSTED]->(c)
                CREATE (a)-[:HAS_COMMENT]->(c)
                SET c.url = {URL}""", parametros),
        ])

    def eliminar(self, id_):
        self.bd.ejecutar("MATCH (c:Comment {id: $id}) DETACH DELETE c",
                         {"id": id_})

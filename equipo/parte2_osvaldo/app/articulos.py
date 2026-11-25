"""
Pestana Articulos: alta, consulta, modificacion y baja de nodos :Article.

    (:Article {id, title, date, text})

Relaciones que administra esta pestana:
    (:User)-[:WROTE]->(:Article)             autor, 1 a N
    (:Article)-[:TAGGED_WITH]->(:Tag)        tags, N a N
    (:Article)-[:IN_CATEGORY]->(:Category)   categorias, N a N

Al eliminar un articulo tambien se eliminan sus comentarios, porque un
comentario no tiene sentido sin el articulo al que pertenece.
"""
import uuid
from tkinter import ttk

from ui_comun import ListaMultiple, PestanaCRUD, Selector

# Quita las relaciones de tags y categorias de un articulo y las vuelve a
# crear con las que se eligieron en el formulario.
ENLAZAR = [
    """MATCH (a:Article {id: $id})-[r:TAGGED_WITH|IN_CATEGORY]->()
       DELETE r""",
    """MATCH (a:Article {id: $id})
       UNWIND $tag_ids AS tid
       MATCH (t:Tag {id: tid})
       MERGE (a)-[:TAGGED_WITH]->(t)""",
    """MATCH (a:Article {id: $id})
       UNWIND $categoria_ids AS cid
       MATCH (c:Category {id: cid})
       MERGE (a)-[:IN_CATEGORY]->(c)""",
]


def _enlazar(parametros):
    """Pasos de ENLAZAR, listos para BaseDatos.transaccion()."""
    return [(cypher, parametros) for cypher in ENLAZAR]


class PestanaArticulos(PestanaCRUD):
    titulo = "Artículos"
    columnas = [("title", "Título", 230), ("date", "Fecha", 85),
                ("autor", "Autor", 120), ("tags", "Tags", 150),
                ("categorias", "Categorías", 150),
                ("comentarios", "Coment.", 60)]
    campos = [("title", "Título", "texto"), ("date", "Fecha (AAAA-MM-DD)", "fecha"),
              ("text", "Texto", "parrafo")]

    # ------------------------------------------------------------------
    # Controles extra: autor, tags y categorias
    # ------------------------------------------------------------------
    def crear_extras(self, marco, fila):
        ttk.Label(marco, text="Autor").grid(row=fila, column=0, sticky="w", pady=3)
        self.autor = Selector(marco)
        self.autor.grid(row=fila, column=1, sticky="ew", pady=3)
        ttk.Label(marco, text="Tags").grid(row=fila + 1, column=0, sticky="nw", pady=3)
        self.tags = ListaMultiple(marco, alto=4)
        self.tags.grid(row=fila + 1, column=1, sticky="ew", pady=3)
        ttk.Label(marco, text="Categorías").grid(row=fila + 2, column=0, sticky="nw",
                                                 pady=3)
        self.categorias = ListaMultiple(marco, alto=4)
        self.categorias.grid(row=fila + 2, column=1, sticky="ew", pady=3)
        return fila + 3

    def actualizar_opciones(self):
        self.autor.cargar([(f["id"], f["name"]) for f in self.bd.consultar(
            "MATCH (u:User) RETURN u.id AS id, u.name AS name ORDER BY u.name")])
        self.tags.cargar([(f["id"], f["name"]) for f in self.bd.consultar(
            "MATCH (t:Tag) RETURN t.id AS id, t.name AS name ORDER BY t.name")])
        self.categorias.cargar([(f["id"], f["name"]) for f in self.bd.consultar(
            "MATCH (c:Category) RETURN c.id AS id, c.name AS name ORDER BY c.name")])

    def cargar_extras(self, registro):
        self.autor.elegir(registro["autor_id"])
        self.tags.elegir(registro["tag_ids"])
        self.categorias.elegir(registro["categoria_ids"])

    def leer_extras(self, datos):
        datos["autor_id"] = self.autor.id_elegido()
        if datos["autor_id"] is None:
            raise ValueError("Elige el autor del artículo.")
        datos["tag_ids"] = self.tags.ids_elegidos()
        datos["categoria_ids"] = self.categorias.ids_elegidos()

    def limpiar_extras(self):
        self.autor.set("")
        self.tags.elegir([])
        self.categorias.elegir([])

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def listar(self):
        # Las listas [(a)-->(t) | t.name] se llaman pattern comprehensions:
        # recorren las relaciones del articulo sin multiplicar las filas.
        return self.bd.consultar("""
            MATCH (a:Article)
            OPTIONAL MATCH (u:User)-[:WROTE]->(a)
            RETURN a.id AS id, a.title AS title, a.date AS date, a.text AS text,
                   u.id AS autor_id, u.name AS autor,
                   [(a)-[:TAGGED_WITH]->(t:Tag) | t.name] AS tags,
                   [(a)-[:TAGGED_WITH]->(t:Tag) | t.id] AS tag_ids,
                   [(a)-[:IN_CATEGORY]->(c:Category) | c.name] AS categorias,
                   [(a)-[:IN_CATEGORY]->(c:Category) | c.id] AS categoria_ids,
                   COUNT { (a)-[:HAS_COMMENT]->(:Comment) } AS comentarios
            ORDER BY a.date DESC, a.title
        """)

    def crear(self, datos):
        # El id se genera aqui (y no con randomUUID()) porque las sentencias
        # de ENLAZAR lo necesitan dentro de la misma transaccion.
        parametros = {**datos, "id": str(uuid.uuid4())}
        self.bd.transaccion([
            ("""MATCH (u:User {id: $autor_id})
                CREATE (u)-[:WROTE]->(:Article {id: $id, title: $title,
                                               date: date($date), text: $text})""",
             parametros),
        ] + _enlazar(parametros))
        return parametros["id"]

    def actualizar(self, id_, datos):
        parametros = {**datos, "id": id_}
        self.bd.transaccion([
            ("""MATCH (a:Article {id: $id})
                SET a.title = $title, a.date = date($date), a.text = $text""",
             parametros),
            # Cambiar el autor: se borra la relacion WROTE y se crea la nueva
            ("""MATCH (:User)-[w:WROTE]->(a:Article {id: $id})
                DELETE w""", parametros),
            ("""MATCH (a:Article {id: $id}), (u:User {id: $autor_id})
                CREATE (u)-[:WROTE]->(a)""", parametros),
        ] + _enlazar(parametros))

    def eliminar(self, id_):
        self.bd.ejecutar("""
            MATCH (a:Article {id: $id})
            OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
            DETACH DELETE c, a
        """, {"id": id_})

"""
Pestana Categorias: alta, consulta, modificacion y baja de nodos :Category.

    (:Category {id, name, url})
    (:Article)-[:IN_CATEGORY]->(:Category)   N a N

El nombre de una categoria no se puede repetir (restriccion category_name).
Al eliminar una categoria solo se borran sus relaciones; los articulos se
conservan.
"""
from ui_comun import PestanaCRUD


class PestanaCategorias(PestanaCRUD):
    titulo = "Categorías"
    columnas = [("name", "Nombre", 170), ("url", "URL", 230),
                ("articulos", "Artículos", 80)]
    campos = [("name", "Nombre", "texto"), ("url", "URL", "texto")]

    def listar(self):
        return self.bd.consultar("""
            MATCH (c:Category)
            RETURN c.id AS id, c.name AS name, c.url AS url,
                   COUNT { (:Article)-[:IN_CATEGORY]->(c) } AS articulos
            ORDER BY c.name
        """)

    def crear(self, datos):
        fila = self.bd.ejecutar("""
            CREATE (c:Category {id: randomUUID(), name: $name, url: $url})
            RETURN c.id AS id
        """, datos)
        return fila[0]["id"]

    def actualizar(self, id_, datos):
        self.bd.ejecutar("""
            MATCH (c:Category {id: $id})
            SET c.name = $name, c.url = $url
        """, {**datos, "id": id_})

    def eliminar(self, id_):
        self.bd.ejecutar("MATCH (c:Category {id: $id}) DETACH DELETE c",
                         {"id": id_})

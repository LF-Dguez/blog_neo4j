"""
Pestana Tags: alta, consulta, modificacion y baja de nodos :Tag.

    (:Tag {id, name, url})
    (:Article)-[:TAGGED_WITH]->(:Tag)   N a N

El nombre de un tag no se puede repetir (restriccion tag_name). Al
eliminar un tag solo se borran sus relaciones; los articulos se conservan.
"""
from ui_comun import PestanaCRUD


class PestanaTags(PestanaCRUD):
    titulo = "Tags"
    columnas = [("name", "Nombre", 160), ("url", "URL", 220),
                ("articulos", "Artículos", 80)]
    campos = [("name", "Nombre", "texto"), ("url", "URL", "texto")]

    def listar(self):
        return self.bd.consultar("""
            MATCH (t:Tag)
            RETURN t.id AS id, t.name AS name, t.url AS url,
                   COUNT { (:Article)-[:TAGGED_WITH]->(t) } AS articulos
            ORDER BY t.name
        """)

    def crear(self, datos):
        fila = self.bd.ejecutar("""
            CREATE (t:Tag {id: randomUUID(), name: $name, url: $url})
            RETURN t.id AS id
        """, datos)
        return fila[0]["id"]

    def actualizar(self, id_, datos):
        self.bd.ejecutar("""
            MATCH (t:Tag {id: $id})
            SET t.name = $name, t.url = $url
        """, {**datos, "id": id_})

    def eliminar(self, id_):
        self.bd.ejecutar("MATCH (t:Tag {id: $id}) DETACH DELETE t", {"id": id_})

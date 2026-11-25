"""
Pestana Usuarios: alta, consulta, modificacion y baja de nodos :User.

    (:User {id, name, email})

Un usuario escribe articulos (:WROTE) y publica comentarios (:POSTED).
Para no dejar articulos ni comentarios sin autor, no se permite eliminar
un usuario que tenga alguno; primero hay que eliminar o reasignar esos
nodos.
"""
from ui_comun import PestanaCRUD


class PestanaUsuarios(PestanaCRUD):
    titulo = "Usuarios"
    columnas = [("name", "Nombre", 170), ("email", "Email", 210),
                ("articulos", "Artículos", 80), ("comentarios", "Comentarios", 90)]
    campos = [("name", "Nombre", "texto"), ("email", "Email", "texto")]

    def listar(self):
        # COUNT { } cuenta las relaciones de cada usuario sin agrupar.
        return self.bd.consultar("""
            MATCH (u:User)
            RETURN u.id AS id, u.name AS name, u.email AS email,
                   COUNT { (u)-[:WROTE]->(:Article) } AS articulos,
                   COUNT { (u)-[:POSTED]->(:Comment) } AS comentarios
            ORDER BY u.name
        """)

    def crear(self, datos):
        if "@" not in datos["email"]:
            raise ValueError("El email no es válido.")
        fila = self.bd.ejecutar("""
            CREATE (u:User {id: randomUUID(), name: $name, email: $email})
            RETURN u.id AS id
        """, datos)
        return fila[0]["id"]

    def actualizar(self, id_, datos):
        if "@" not in datos["email"]:
            raise ValueError("El email no es válido.")
        self.bd.ejecutar("""
            MATCH (u:User {id: $id})
            SET u.name = $name, u.email = $email
        """, {**datos, "id": id_})

    def eliminar(self, id_):
        fila = self.bd.consultar("""
            MATCH (u:User {id: $id})
            RETURN COUNT { (u)-[:WROTE]->() } AS articulos,
                   COUNT { (u)-[:POSTED]->() } AS comentarios
        """, {"id": id_})[0]
        if fila["articulos"] or fila["comentarios"]:
            raise ValueError(
                f"El usuario tiene {fila['articulos']} artículos y "
                f"{fila['comentarios']} comentarios. Elimínalos antes de "
                "eliminar al usuario.")
        self.bd.ejecutar("MATCH (u:User {id: $id}) DETACH DELETE u", {"id": id_})

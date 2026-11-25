// =====================================================================
// 04_articulos_comentarios.cypher
// Operaciones CRUD sobre (:Article) y (:Comment) con sus relaciones, las
// mismas que usan app/articulos.py y app/comentarios.py. Se usa un
// articulo de prueba para poder ejecutarlas en orden.
//
//   (:User)-[:WROTE]->(:Article)-[:TAGGED_WITH]->(:Tag)
//                      (:Article)-[:IN_CATEGORY]->(:Category)
//   (:User)-[:POSTED]->(:Comment)<-[:HAS_COMMENT]-(:Article)
//
// Ejecutar:  python app/cargar_cypher.py cypher/04_articulos_comentarios.cypher
// =====================================================================

// ---------------------------- ARTICULOS ------------------------------

// CREATE: articulo escrito por Ana con dos tags y una categoria
MATCH (u:User {email: "ana.torres@blog.mx"})
CREATE (u)-[:WROTE]->(a:Article {id: randomUUID(),
                                 title: "Articulo de prueba",
                                 date: date("2026-11-24"),
                                 text: "Texto del articulo de prueba."})
WITH a
MATCH (t:Tag) WHERE t.name IN ["neo4j", "python"]
CREATE (a)-[:TAGGED_WITH]->(t)
WITH DISTINCT a
MATCH (c:Category {name: "Programación"})
CREATE (a)-[:IN_CATEGORY]->(c)
RETURN a.title AS title;

// READ: el articulo con su autor, tags y categorias
MATCH (u:User)-[:WROTE]->(a:Article {title: "Articulo de prueba"})
RETURN a.title AS title, a.date AS date, u.name AS autor,
       [(a)-[:TAGGED_WITH]->(t:Tag) | t.name] AS tags,
       [(a)-[:IN_CATEGORY]->(c:Category) | c.name] AS categorias;

// UPDATE: cambiar el texto y reemplazar el tag python por cypher
MATCH (a:Article {title: "Articulo de prueba"})
SET a.text = "Texto modificado."
WITH a
MATCH (a)-[r:TAGGED_WITH]->(:Tag {name: "python"})
DELETE r
WITH a
MATCH (t:Tag {name: "cypher"})
MERGE (a)-[:TAGGED_WITH]->(t)
RETURN a.title AS title, a.text AS text,
       [(a)-[:TAGGED_WITH]->(x:Tag) | x.name] AS tags;

// --------------------------- COMENTARIOS -----------------------------

// CREATE: Luis comenta el articulo de prueba
MATCH (u:User {email: "luis.ramirez@blog.mx"}),
      (a:Article {title: "Articulo de prueba"})
CREATE (c:Comment {id: randomUUID(), name: "Comentario de prueba",
                   text: "Buen articulo.", date: date("2026-11-24")})
SET c.url = "/articulos/" + toLower(replace(a.title, " ", "-")) +
            "#comentario-" + substring(c.id, 0, 8)
CREATE (u)-[:POSTED]->(c)
CREATE (a)-[:HAS_COMMENT]->(c)
RETURN c.name AS name, c.url AS url;

// READ: comentarios del articulo con su autor
MATCH (a:Article {title: "Articulo de prueba"})-[:HAS_COMMENT]->(c:Comment)
MATCH (u:User)-[:POSTED]->(c)
RETURN c.name AS name, c.text AS text, c.date AS date, u.name AS autor;

// UPDATE: modificar el texto del comentario
MATCH (c:Comment {name: "Comentario de prueba"})
SET c.text = "Buen articulo, me sirvio mucho."
RETURN c.name AS name, c.text AS text;

// DELETE: eliminar el comentario
MATCH (c:Comment {name: "Comentario de prueba"})
DETACH DELETE c;

// DELETE: eliminar el articulo junto con sus comentarios
MATCH (a:Article {title: "Articulo de prueba"})
OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
DETACH DELETE c, a;

// Comprobacion: ya no queda nada de prueba
MATCH (n) WHERE n.title = "Articulo de prueba"
             OR n.name = "Comentario de prueba"
RETURN count(n) AS nodos_de_prueba;

// =====================================================================
// 05_tags_categorias.cypher
// Operaciones CRUD sobre (:Tag) y (:Category), las mismas que usan
// app/tags.py y app/categorias.py. Se usan un tag y una categoria de
// prueba para poder ejecutarlas en orden.
//
//   (:Article)-[:TAGGED_WITH]->(:Tag)        N a N
//   (:Article)-[:IN_CATEGORY]->(:Category)   N a N
//
// Ejecutar:  python app/cargar_cypher.py cypher/05_tags_categorias.cypher
// =====================================================================

// ------------------------------- TAGS --------------------------------

// CREATE tag
CREATE (t:Tag {id: randomUUID(), name: "tag-prueba", url: "/tag/tag-prueba"})
RETURN t.name AS name, t.url AS url;

// READ tags: con el numero de articulos que los usan
MATCH (t:Tag)
RETURN t.name AS name, t.url AS url,
       COUNT { (:Article)-[:TAGGED_WITH]->(t) } AS articulos
ORDER BY name;

// UPDATE tag
MATCH (t:Tag {name: "tag-prueba"})
SET t.name = "tag-modificado", t.url = "/tag/tag-modificado"
RETURN t.name AS name, t.url AS url;

// DELETE tag: DETACH DELETE quita sus relaciones; los articulos se conservan
MATCH (t:Tag {name: "tag-modificado"})
DETACH DELETE t;

// ---------------------------- CATEGORIAS -----------------------------

// CREATE categoria
CREATE (c:Category {id: randomUUID(), name: "Categoria de prueba",
                    url: "/categoria/prueba"})
RETURN c.name AS name, c.url AS url;

// READ categorias: con el numero de articulos
MATCH (c:Category)
RETURN c.name AS name, c.url AS url,
       COUNT { (:Article)-[:IN_CATEGORY]->(c) } AS articulos
ORDER BY name;

// UPDATE categoria
MATCH (c:Category {name: "Categoria de prueba"})
SET c.name = "Categoria modificada", c.url = "/categoria/modificada"
RETURN c.name AS name, c.url AS url;

// DELETE categoria
MATCH (c:Category {name: "Categoria modificada"})
DETACH DELETE c;

// Comprobacion: no quedan nodos de prueba
MATCH (n) WHERE n.name IN ["tag-prueba", "tag-modificado",
                           "Categoria de prueba", "Categoria modificada"]
RETURN count(n) AS nodos_de_prueba;

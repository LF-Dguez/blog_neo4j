// =====================================================================
// 06_consultas.cypher
// Consultas de solo lectura sobre el grafo del blog, las mismas de la
// pestana Consultas (app/consultas.py). En la aplicacion el tag o el
// articulo se eligen en pantalla ($parametro); aqui se usan valores de
// ejemplo para poder ejecutarlas tal cual.
//
// Ejecutar:  python app/cargar_cypher.py cypher/06_consultas.cypher
// =====================================================================

// 1. Artículos por categoría
// Cuántos artículos tiene cada categoría.
MATCH (c:Category)
OPTIONAL MATCH (a:Article)-[:IN_CATEGORY]->(c)
RETURN c.name AS categoria, count(a) AS articulos
ORDER BY articulos DESC, categoria;

// 2. Tags más usados
// En cuántos artículos aparece cada tag.
MATCH (t:Tag)
RETURN t.name AS tag, COUNT { (:Article)-[:TAGGED_WITH]->(t) } AS articulos
ORDER BY articulos DESC, tag;

// 3. Artículos más comentados
// Cada artículo con su autor y su número de comentarios.
MATCH (u:User)-[:WROTE]->(a:Article)
RETURN a.title AS articulo, u.name AS autor,
       COUNT { (a)-[:HAS_COMMENT]->(:Comment) } AS comentarios
ORDER BY comentarios DESC, articulo;

// 4. Actividad de cada usuario
// Artículos escritos y comentarios publicados por usuario.
MATCH (u:User)
RETURN u.name AS usuario,
       COUNT { (u)-[:WROTE]->(:Article) } AS articulos,
       COUNT { (u)-[:POSTED]->(:Comment) } AS comentarios
ORDER BY articulos + comentarios DESC, usuario;

// 5. Artículos de un tag
// Los artículos que tienen el tag elegido, con su autor.
// (ejemplo con el tag neo4j)
MATCH (t:Tag {name: "neo4j"})<-[:TAGGED_WITH]-(a:Article)
MATCH (u:User)-[:WROTE]->(a)
RETURN a.title AS articulo, u.name AS autor, a.date AS fecha
ORDER BY fecha DESC;

// 6. Artículos relacionados
// Artículos que comparten tags con el artículo elegido.
// (ejemplo con el articulo "Introducción a las bases de datos de grafos")
MATCH (a:Article {title: "Introducción a las bases de datos de grafos"})-[:TAGGED_WITH]->(t:Tag)
      <-[:TAGGED_WITH]-(otro:Article)
RETURN otro.title AS relacionado, collect(t.name) AS tags_en_comun,
       count(t) AS en_comun
ORDER BY en_comun DESC, relacionado;

// 7. Quién comenta a quién
// Usuarios que comentan artículos de otros usuarios.
MATCH (lector:User)-[:POSTED]->(:Comment)
      <-[:HAS_COMMENT]-(:Article)<-[:WROTE]-(autor:User)
WHERE lector <> autor
RETURN lector.name AS lector, autor.name AS autor, count(*) AS comentarios
ORDER BY comentarios DESC, lector;

// 8. Artículos sin comentarios
// Artículos que todavía no tienen ningún comentario.
MATCH (u:User)-[:WROTE]->(a:Article)
WHERE NOT EXISTS { (a)-[:HAS_COMMENT]->(:Comment) }
RETURN a.title AS articulo, u.name AS autor, a.date AS fecha
ORDER BY fecha;

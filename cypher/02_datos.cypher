// =====================================================================
// 02_datos.cypher
// Datos iniciales del blog: usuarios, categorias, tags, articulos y
// comentarios, con todas sus relaciones.
//
// Modelo (nodos y relaciones):
//   (:User {id, name, email})
//   (:Article {id, title, date, text})
//   (:Comment {id, name, url, text, date})
//   (:Tag {id, name, url})
//   (:Category {id, name, url})
//
//   (:User)-[:WROTE]->(:Article)            1 a N
//   (:User)-[:POSTED]->(:Comment)           1 a N
//   (:Article)-[:HAS_COMMENT]->(:Comment)   1 a N
//   (:Article)-[:TAGGED_WITH]->(:Tag)       N a N
//   (:Article)-[:IN_CATEGORY]->(:Category)  N a N
//
// Se puede ejecutar varias veces: la primera sentencia borra los nodos
// del blog (y sus relaciones) antes de volver a crearlos.
//
// Ejecutar:  python app/cargar_cypher.py cypher/02_datos.cypher
// =====================================================================

// 1. Borrar los datos anteriores del blog
MATCH (n)
WHERE n:User OR n:Article OR n:Comment OR n:Tag OR n:Category
DETACH DELETE n;

// 2. Usuarios
UNWIND [
  {name: "Ana Torres",     email: "ana.torres@blog.mx"},
  {name: "Luis Ramírez",   email: "luis.ramirez@blog.mx"},
  {name: "Sofía Chávez",   email: "sofia.chavez@blog.mx"},
  {name: "Carlos Méndez",  email: "carlos.mendez@blog.mx"},
  {name: "Valeria Ortiz",  email: "valeria.ortiz@blog.mx"}
] AS d
CREATE (:User {id: randomUUID(), name: d.name, email: d.email});

// 3. Categorias
UNWIND [
  {name: "Bases de Datos",   url: "/categoria/bases-de-datos"},
  {name: "Programación",     url: "/categoria/programacion"},
  {name: "Ciencia de Datos", url: "/categoria/ciencia-de-datos"},
  {name: "Infraestructura",  url: "/categoria/infraestructura"}
] AS d
CREATE (:Category {id: randomUUID(), name: d.name, url: d.url});

// 4. Tags
UNWIND ["neo4j", "mongodb", "python", "cypher", "sql", "docker", "grafos", "nosql"]
  AS nombre
CREATE (:Tag {id: randomUUID(), name: nombre, url: "/tag/" + nombre});

// 5. Articulos y su autor (User)-[:WROTE]->(Article)
UNWIND [
  {title: "Introducción a las bases de datos de grafos", date: "2026-09-02",
   autor: "ana.torres@blog.mx",
   text: "Una base de datos de grafos guarda nodos y las relaciones entre ellos como datos de primera clase, lo que facilita recorrer conexiones."},
  {title: "Primeros pasos con Cypher", date: "2026-09-10",
   autor: "luis.ramirez@blog.mx",
   text: "Cypher describe patrones con una sintaxis visual: los nodos van entre paréntesis y las relaciones entre corchetes."},
  {title: "MongoDB vs Neo4j: cuándo usar cada uno", date: "2026-09-18",
   autor: "sofia.chavez@blog.mx",
   text: "MongoDB conviene para documentos independientes; Neo4j, cuando lo importante son las relaciones entre los datos."},
  {title: "Conectar Python con Neo4j", date: "2026-09-27",
   autor: "carlos.mendez@blog.mx",
   text: "El driver oficial de Neo4j para Python permite ejecutar consultas Cypher con parámetros y recibir los resultados como diccionarios."},
  {title: "Sharding en MongoDB con Docker", date: "2026-10-08",
   autor: "ana.torres@blog.mx",
   text: "Con Docker Compose se puede levantar un cluster con config server, shards y un router mongos en una sola computadora."},
  {title: "Modelar relaciones N a N en un grafo", date: "2026-10-15",
   autor: "valeria.ortiz@blog.mx",
   text: "En un grafo, una relación N a N no necesita tabla intermedia: basta con conectar los nodos directamente."},
  {title: "Análisis de redes sociales con grafos", date: "2026-10-29",
   autor: "sofia.chavez@blog.mx",
   text: "Los grafos permiten encontrar comunidades, influenciadores y caminos cortos entre personas de una red social."},
  {title: "De SQL a Cypher: guía rápida", date: "2026-11-12",
   autor: "luis.ramirez@blog.mx",
   text: "SELECT se convierte en MATCH y RETURN, y los JOIN se reemplazan por patrones de relaciones."}
] AS d
MATCH (u:User {email: d.autor})
CREATE (u)-[:WROTE]->(:Article {id: randomUUID(), title: d.title,
                                date: date(d.date), text: d.text});

// 6. Tags de cada articulo (Article)-[:TAGGED_WITH]->(Tag)
UNWIND [
  ["Introducción a las bases de datos de grafos", ["grafos", "neo4j", "nosql"]],
  ["Primeros pasos con Cypher",                   ["cypher", "neo4j"]],
  ["MongoDB vs Neo4j: cuándo usar cada uno",      ["mongodb", "neo4j", "nosql"]],
  ["Conectar Python con Neo4j",                   ["python", "neo4j"]],
  ["Sharding en MongoDB con Docker",              ["mongodb", "docker"]],
  ["Modelar relaciones N a N en un grafo",        ["grafos", "cypher"]],
  ["Análisis de redes sociales con grafos",       ["grafos", "python"]],
  ["De SQL a Cypher: guía rápida",                ["sql", "cypher"]]
] AS par
MATCH (a:Article {title: par[0]})
UNWIND par[1] AS nombre
MATCH (t:Tag {name: nombre})
CREATE (a)-[:TAGGED_WITH]->(t);

// 7. Categorias de cada articulo (Article)-[:IN_CATEGORY]->(Category)
UNWIND [
  ["Introducción a las bases de datos de grafos", ["Bases de Datos"]],
  ["Primeros pasos con Cypher",                   ["Bases de Datos", "Programación"]],
  ["MongoDB vs Neo4j: cuándo usar cada uno",      ["Bases de Datos"]],
  ["Conectar Python con Neo4j",                   ["Programación"]],
  ["Sharding en MongoDB con Docker",              ["Bases de Datos", "Infraestructura"]],
  ["Modelar relaciones N a N en un grafo",        ["Bases de Datos"]],
  ["Análisis de redes sociales con grafos",       ["Ciencia de Datos"]],
  ["De SQL a Cypher: guía rápida",                ["Bases de Datos", "Programación"]]
] AS par
MATCH (a:Article {title: par[0]})
UNWIND par[1] AS nombre
MATCH (c:Category {name: nombre})
CREATE (a)-[:IN_CATEGORY]->(c);

// 8. Comentarios: (User)-[:POSTED]->(Comment)<-[:HAS_COMMENT]-(Article)
//    name es el titulo corto del comentario y url su enlace permanente.
UNWIND [
  {articulo: "Introducción a las bases de datos de grafos", autor: "luis.ramirez@blog.mx",
   name: "Muy claro", date: "2026-09-03",
   text: "La comparación con las tablas relacionales me ayudó a entender los nodos."},
  {articulo: "Introducción a las bases de datos de grafos", autor: "carlos.mendez@blog.mx",
   name: "Pregunta sobre índices", date: "2026-09-04",
   text: "¿Neo4j también usa índices para buscar nodos por propiedad?"},
  {articulo: "Introducción a las bases de datos de grafos", autor: "valeria.ortiz@blog.mx",
   name: "Buen inicio", date: "2026-09-06",
   text: "Esperaba un ejemplo con Cypher, pero como introducción está muy bien."},
  {articulo: "Primeros pasos con Cypher", autor: "ana.torres@blog.mx",
   name: "Ejemplo útil", date: "2026-09-11",
   text: "El patrón (a)-[:REL]->(b) se entiende muy rápido con los dibujos."},
  {articulo: "Primeros pasos con Cypher", autor: "sofia.chavez@blog.mx",
   name: "MERGE vs CREATE", date: "2026-09-12",
   text: "Faltaría explicar la diferencia entre MERGE y CREATE."},
  {articulo: "MongoDB vs Neo4j: cuándo usar cada uno", autor: "ana.torres@blog.mx",
   name: "Totalmente de acuerdo", date: "2026-09-19",
   text: "Para catálogos uso MongoDB y para recomendaciones Neo4j."},
  {articulo: "MongoDB vs Neo4j: cuándo usar cada uno", autor: "carlos.mendez@blog.mx",
   name: "¿Y el rendimiento?", date: "2026-09-21",
   text: "Sería bueno comparar tiempos de consulta con datos reales."},
  {articulo: "Conectar Python con Neo4j", autor: "luis.ramirez@blog.mx",
   name: "Me funcionó", date: "2026-09-28",
   text: "Seguí los pasos y ya conecté mi aplicación con execute_query."},
  {articulo: "Conectar Python con Neo4j", autor: "sofia.chavez@blog.mx",
   name: "Parámetros", date: "2026-09-30",
   text: "Buen detalle usar parámetros en lugar de concatenar texto en las consultas."},
  {articulo: "Sharding en MongoDB con Docker", autor: "carlos.mendez@blog.mx",
   name: "Gran tutorial", date: "2026-10-09",
   text: "Lo repliqué con tres shards y funcionó a la primera."},
  {articulo: "Modelar relaciones N a N en un grafo", autor: "luis.ramirez@blog.mx",
   name: "Sin tablas intermedias", date: "2026-10-16",
   text: "Es justo lo que más me gusta de los grafos."},
  {articulo: "Modelar relaciones N a N en un grafo", autor: "ana.torres@blog.mx",
   name: "Propiedades en relaciones", date: "2026-10-18",
   text: "También se pueden guardar propiedades en la relación, como la fecha."},
  {articulo: "Análisis de redes sociales con grafos", autor: "valeria.ortiz@blog.mx",
   name: "Algoritmos", date: "2026-10-30",
   text: "¿Qué biblioteca recomiendan para detectar comunidades?"},
  {articulo: "Análisis de redes sociales con grafos", autor: "carlos.mendez@blog.mx",
   name: "Excelente", date: "2026-11-01",
   text: "Muy buen ejemplo de caminos cortos entre usuarios."}
] AS d
MATCH (u:User {email: d.autor})
MATCH (a:Article {title: d.articulo})
CREATE (c:Comment {id: randomUUID(), name: d.name, text: d.text,
                   date: date(d.date)})
SET c.url = "/articulos/" + toLower(replace(a.title, " ", "-")) +
            "#comentario-" + substring(c.id, 0, 8)
CREATE (u)-[:POSTED]->(c)
CREATE (a)-[:HAS_COMMENT]->(c);

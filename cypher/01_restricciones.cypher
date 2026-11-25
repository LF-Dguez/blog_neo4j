// =====================================================================
// 01_restricciones.cypher
// Restricciones de unicidad del modelo del blog.
//
// Cada nodo tiene un identificador propio (id) generado con randomUUID().
// Ademas, el email de un usuario y el nombre de un tag o de una categoria
// no se pueden repetir. Una restriccion UNIQUE tambien crea un indice, asi
// que las busquedas por estas propiedades son rapidas.
//
// Ejecutar:  python app/cargar_cypher.py cypher/01_restricciones.cypher
// =====================================================================

CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT user_email IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT article_id IF NOT EXISTS
FOR (a:Article) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT comment_id IF NOT EXISTS
FOR (c:Comment) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT tag_id IF NOT EXISTS
FOR (t:Tag) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT tag_name IF NOT EXISTS
FOR (t:Tag) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT category_id IF NOT EXISTS
FOR (c:Category) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT category_name IF NOT EXISTS
FOR (c:Category) REQUIRE c.name IS UNIQUE;

// =====================================================================
// 03_usuarios.cypher
// Operaciones CRUD sobre (:User), las mismas que usa app/usuarios.py.
// En la aplicacion los valores llegan como parametros ($name, $email,
// $id); aqui se escriben con un usuario de prueba para poder ejecutarlas
// en orden y ver el resultado de cada paso.
//
// Ejecutar:  python app/cargar_cypher.py cypher/03_usuarios.cypher
// =====================================================================

// CREATE: nuevo usuario con id generado por Neo4j
CREATE (u:User {id: randomUUID(), name: "Usuario de Prueba",
                email: "prueba@blog.mx"})
RETURN u.name AS name, u.email AS email;

// READ: todos los usuarios con cuantos articulos y comentarios tienen
MATCH (u:User)
RETURN u.name AS name, u.email AS email,
       COUNT { (u)-[:WROTE]->(:Article) } AS articulos,
       COUNT { (u)-[:POSTED]->(:Comment) } AS comentarios
ORDER BY name;

// UPDATE: cambiar el nombre del usuario de prueba
MATCH (u:User {email: "prueba@blog.mx"})
SET u.name = "Usuario Modificado"
RETURN u.name AS name, u.email AS email;

// DELETE: solo si no tiene articulos ni comentarios
MATCH (u:User {email: "prueba@blog.mx"})
WHERE NOT EXISTS { (u)-[:WROTE|POSTED]->() }
DETACH DELETE u;

// Comprobacion: el usuario de prueba ya no existe
MATCH (u:User {email: "prueba@blog.mx"})
RETURN count(u) AS usuarios_de_prueba;

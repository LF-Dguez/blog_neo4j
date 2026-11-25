# blog_neo4j
Osvaldo Hernández Juárez - Matrícula: 385493
Diego Flores Verdad Grijalva - Matrícula: 385660
Luis Felipe Domínguez Chávez - Matrícula: 385500
Aplicación en Python con interfaz gráfica (Tkinter) para administrar un blog
guardado en una base de datos de grafos Neo4j.
Proyecto final — Bases de Datos Avanzadas, UACH Facultad de Ingeniería.
## Modelo de datos
```
(:User {id, name, email})
(:Article {id, title, date, text})
(:Comment {id, name, url, text, date})
(:Tag {id, name, url})
(:Category {id, name, url})
(:User)-[:WROTE]->(:Article)            1 a N
(:User)-[:POSTED]->(:Comment)           1 a N
(:Article)-[:HAS_COMMENT]->(:Comment)   1 a N
(:Article)-[:TAGGED_WITH]->(:Tag)       N a N
(:Article)-[:IN_CATEGORY]->(:Category)  N a N
```
## Requisitos
- Neo4j Desktop con una base de datos local iniciada (Bolt en `localhost:7687`).
- Python 3.10 o superior, con Tkinter (viene incluido en el instalador de Windows).
- Driver de Neo4j para Python: `pip install -r requirements.txt`
## Cómo ejecutarla
Todos los comandos se corren desde la raíz del repositorio.
1. Copiar `config.ejemplo.ini` como `config.ini` y escribir la contraseña de la base.
2. Crear las restricciones y cargar los datos iniciales:
   ```bash
   python app/cargar_cypher.py cypher/01_restricciones.cypher cypher/02_datos.cypher
   ```
3. Abrir la aplicación:
   ```bash
   python app/main.py
   ```
## Demostración paso a paso
### 1. Iniciar la base de datos
1. Abrir **Neo4j Desktop**.
2. En **Instances**, buscar la instancia del proyecto y presionar **Start**.
3. Esperar a que diga **RUNNING** (conexión `neo4j://127.0.0.1:7687`).
### 2. Cargar datos limpios
Abrir PowerShell en la carpeta del repositorio y ejecutar:
```powershell
python app/cargar_cypher.py cypher/01_restricciones.cypher cypher/02_datos.cypher
```
Al final debe mostrar 8 artículos, 4 categorías, 14 comentarios, 8 tags y 5 usuarios
(39 nodos y 65 relaciones). Este paso borra cualquier prueba anterior.
### 3. Ver el grafo en Neo4j
1. En Neo4j Desktop entrar a **Query** → **Connect to instance** → **Connect**.
2. Ejecutar:
   ```
   MATCH (n)-[r]->(m) RETURN n, r, m
   ```
### 4. Abrir la aplicación
```powershell
python app/main.py
```
El encabezado debe decir `Conectado a Neo4j Kernel ...`. Si aparece un error de
conexión, la instancia no está iniciada (paso 1) o la contraseña de `config.ini`
no es correcta.
### 5. Recorrido por la aplicación
1. **Usuarios**
   - Crear un usuario con **Nuevo** → llenar nombre y email → **Guardar**.
   - Intentar crear otro con el email `ana.torres@blog.mx`: Neo4j lo rechaza por la
     restricción de unicidad.
   - Elegir a Ana Torres y presionar **Eliminar**: no se permite porque tiene artículos
     y comentarios.
2. **Artículos**: crear un artículo con autor, dos tags y una categoría.
3. **Comentarios**: crear un comentario para ese artículo; la URL se genera sola.
4. **Artículos**: el artículo nuevo aparece con 1 comentario.
5. **Tags**: intentar crear el tag `neo4j` otra vez: aparece el error de nombre repetido.
6. **Categorías**: crear una categoría y modificarla.
7. **Consultas**
   - 1. Artículos por categoría.
   - 6. Artículos relacionados: elegir "Introducción a las bases de datos de grafos"
     y presionar **Ejecutar**.
   - 8. Artículos sin comentarios.
8. **Artículos**: eliminar el artículo creado; su comentario también se elimina.
### 6. Operaciones en Cypher (opcional)
```powershell
python app/cargar_cypher.py cypher/03_usuarios.cypher
python app/cargar_cypher.py cypher/04_articulos_comentarios.cypher
python app/cargar_cypher.py cypher/05_tags_categorias.cypher
python app/cargar_cypher.py cypher/06_consultas.cypher
```
### 7. Al terminar
Volver a ejecutar el comando del paso 2 para dejar la base con los datos iniciales.
## Estructura
| Ruta | Contenido |
|---|---|
| `app/main.py` | Ventana principal con una pestaña por cada tipo de nodo |
| `app/conexion.py` | Conexión con Neo4j (lee `config.ini`) |
| `app/ui_comun.py` | Componentes de interfaz comunes a las pestañas |
| `app/usuarios.py` | Pestaña Usuarios |
| `app/articulos.py`, `app/comentarios.py` | Pestañas Artículos y Comentarios |
| `app/tags.py`, `app/categorias.py` | Pestañas Tags y Categorías |
| `app/consultas.py` | Pestaña Consultas |
| `app/cargar_cypher.py` | Ejecuta archivos `.cypher` |
| `cypher/` | Restricciones, datos iniciales, operaciones CRUD y consultas en Cypher |
| `reporte/` | Reporte del proyecto (PDF) y capturas |
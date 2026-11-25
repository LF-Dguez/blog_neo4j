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

# Contexto del proyecto final: Blog en Neo4j

> Guía exacta para que cada integrante haga su parte sin errores.
> Sigue los pasos **en orden** y copia los comandos tal cual.
> Si usas una IA para ayudarte, pásale este archivo completo y pídele que respete todo lo que dice.
> Si algo no sale igual a lo que dice aquí, **detente y avisa en el grupo** antes de hacer commit.

**Materia:** Bases de Datos Avanzadas — UACH, Facultad de Ingeniería, Grupo 5k2
**Docente:** José Saúl De Lira Miramontes
**Repositorio:** https://github.com/LF-Dguez/blog_neo4j
**Entrega:** hoy, 24 de noviembre de 2026

| Integrante | Matrícula | Parte | Capturas |
|---|---|---|---|
| Luis Felipe Domínguez Chávez | 385500 | **1.** Conexión, restricciones, datos iniciales, ventana principal, pestaña Usuarios, reporte | 01–19 |
| Osvaldo Hernández Juárez | 385493 | **2.** Pestañas Artículos y Comentarios + Cypher de ambos | 20–39 |
| Diego Flores Verdad Grijalva | 385660 | **3.** Pestañas Tags, Categorías y Consultas + Cypher de los tres | 40–59 |

---

## 1. Lo que pide el profe

**Objetivo:** desarrollar una aplicación de base de datos de grafos.
**Actividad:** desarrollar una aplicación en Python que permita administrar un blog en una base de datos Neo4j, con el modelo del archivo adjunto (users, articles, comments, tags, categories).
**Evidencia (repositorio GitHub):** reporte PDF (código documentado y screenshots de la ejecución), código de la aplicación y archivos Cypher.

## 2. Modelo de datos (no cambiar nada)

```
(:User {id, name, email})
(:Article {id, title, date, text})
(:Comment {id, name, url, text, date})
(:Tag {id, name, url})
(:Category {id, name, url})

(:User)-[:WROTE]->(:Article)            1 a N   un usuario escribe muchos artículos
(:User)-[:POSTED]->(:Comment)           1 a N   un usuario publica muchos comentarios
(:Article)-[:HAS_COMMENT]->(:Comment)   1 a N   un artículo tiene muchos comentarios
(:Article)-[:TAGGED_WITH]->(:Tag)       N a N
(:Article)-[:IN_CATEGORY]->(:Category)  N a N
```

Decisiones ya tomadas:
- Todo nodo tiene `id` generado con `randomUUID()`. La aplicación busca y modifica siempre por `id`.
- Restricciones únicas: `id` de cada etiqueta, `User.email`, `Tag.name`, `Category.name`.
- `Article.date` y `Comment.date` son de tipo `date` (se escriben `AAAA-MM-DD`).
- En el diagrama del profe, comments tiene `name` y `url`. Lo interpretamos como **título corto** del comentario y **enlace permanente**; además se agregaron `text` (el contenido) y `date`. La `url` del comentario la genera la aplicación.
- Reglas al eliminar: un **usuario** con artículos o comentarios no se puede eliminar (sale un aviso). Un **artículo** se elimina junto con sus comentarios. Un **tag**, una **categoría** o un **comentario** se eliminan con sus relaciones (`DETACH DELETE`).
- Todo el Cypher de la aplicación usa parámetros (`$id`, `$name`…), nunca texto pegado.

## 3. Estructura del repositorio

```
blog_neo4j/
├── app/
│   ├── main.py            ventana principal (Luis Felipe)
│   ├── conexion.py        conexión con Neo4j (Luis Felipe)
│   ├── ui_comun.py        componentes de interfaz comunes (Luis Felipe)
│   ├── cargar_cypher.py   ejecuta archivos .cypher (Luis Felipe)
│   ├── usuarios.py        pestaña Usuarios (Luis Felipe)
│   ├── articulos.py       pestaña Artículos (Osvaldo)
│   ├── comentarios.py     pestaña Comentarios (Osvaldo)
│   ├── tags.py            pestaña Tags (Diego)
│   ├── categorias.py      pestaña Categorías (Diego)
│   └── consultas.py       pestaña Consultas (Diego)
├── cypher/
│   ├── 01_restricciones.cypher          (Luis Felipe)
│   ├── 02_datos.cypher                  (Luis Felipe)
│   ├── 03_usuarios.cypher               (Luis Felipe)
│   ├── 04_articulos_comentarios.cypher  (Osvaldo)
│   ├── 05_tags_categorias.cypher        (Diego)
│   └── 06_consultas.cypher              (Diego)
├── equipo/              CONTEXTO.md y los archivos de Osvaldo y Diego para copiar
├── reporte/
│   ├── img/               capturas de los tres
│   └── Reporte_Proyecto_Final.pdf   (al final)
├── config.ejemplo.ini     plantilla de config.ini
├── requirements.txt
└── README.md
```

`main.py` agrega una pestaña por cada módulo que existe. Mientras no agregues tus archivos, tus pestañas no aparecen; en cuanto los copias, aparecen solas. **No modifiques `main.py`, `ui_comun.py`, `conexion.py` ni archivos de otro integrante.**

## 4. Reglas para todos

1. Tus archivos de código vienen ya escritos y probados en la carpeta `equipo/` del repo (`equipo/parte2_osvaldo/` o `equipo/parte3_diego/`). Tu trabajo es: copiarlos a su lugar, hacer tus commits, ejecutar la aplicación, tomar tus capturas y subir todo.
2. **Nunca** uses `git add .` ni `git add -A`. Agrega solo los archivos que dice tu sección.
3. Los mensajes de commit son los de tu sección, tal cual.
4. Las capturas van en `reporte/img/` con el nombre exacto, en PNG, de **solo la ventana** (Win + Shift + S → modo ventana).
5. **No toques LaTeX ni el reporte.** Luis Felipe arma el reporte con tus capturas.
6. Antes de tus capturas, vuelve a cargar los datos iniciales (paso 5.7) para que todos partamos de lo mismo y salgan los números de esta guía.
7. Antes de `git push`, siempre `git pull --rebase`.

---

## 5. Preparar tu computadora (Osvaldo y Diego, una sola vez)

**5.1 Aceptar la invitación al repositorio.** Te llega por correo o en https://github.com/notifications. Sin aceptarla no puedes hacer push.

**5.2 Clonar** (PowerShell, en la carpeta donde guardes tus proyectos):
```powershell
git clone https://github.com/LF-Dguez/blog_neo4j.git
cd blog_neo4j
```

**5.3 Revisar tu nombre en git** (debe salir tu nombre y tu correo de GitHub):
```powershell
git config user.name
git config user.email
```
Si sale vacío o algo que no es tuyo:
```powershell
git config user.name "Tu Nombre Completo"
git config user.email "tu_correo_de_github@ejemplo.com"
```

**5.4 Neo4j Desktop: crear la base**
- Abre Neo4j Desktop.
- **Neo4j Desktop 2 (ventana con "Instances"):** botón **Create instance** → Name: `blog` → deja la versión que sugiere → escribe una contraseña (anótala) → **Create**. Cuando termine, si no dice **Running**, dale **Start** (▶).
- **Neo4j Desktop 1.x (ventana con "Projects"):** crea un proyecto → **Add** → **Local DBMS** → Name: `blog`, Password: la tuya → **Create** → **Start**.
- Si tienes otra base de Neo4j iniciada, detenla primero: dos bases no pueden usar el puerto 7687 al mismo tiempo.

**5.5 Python y el driver**
```powershell
python --version
python -c "import tkinter; print('tkinter ok')"
pip install -r requirements.txt
```
- `python --version` debe ser 3.10 o mayor.
- Si `import tkinter` falla, reinstala Python desde python.org marcando "tcl/tk and IDLE".

**5.6 config.ini**
```powershell
Copy-Item config.ejemplo.ini config.ini
notepad config.ini
```
En `contrasena =` escribe la contraseña del paso 5.4 y guarda. `config.ini` no se sube a GitHub (está en `.gitignore`).

**5.7 Crear las restricciones y cargar los datos iniciales**
```powershell
python app/cargar_cypher.py cypher/01_restricciones.cypher cypher/02_datos.cypher
```
Al final debe mostrar exactamente:
```
Nodos en la base:
  Article    8
  Category   4
  Comment    14
  Tag        8
  User       5
Relaciones:
  HAS_COMMENT  14
  IN_CATEGORY  11
  POSTED       14
  TAGGED_WITH  18
  WROTE        8
```
Si sale `Unauthorized` → la contraseña de `config.ini` no coincide. Si sale `Couldn't connect` / `ServiceUnavailable` → la base no está iniciada en Neo4j Desktop.

**5.8 Probar la aplicación**
```powershell
python app/main.py
```
Se abre la ventana "Blog en Neo4j" con la pestaña **Usuarios** (5 usuarios). Ciérrala.

---

## 6. Parte 1 — Luis Felipe: capturas

El código de la parte 1 ya está en el repo. Capturas, después de recargar los datos (paso 5.7):

| Captura | Qué hacer | Qué debe verse |
|---|---|---|
| `01-neo4j-desktop.png` | Neo4j Desktop con la instancia `blog` | Estado **Running** |
| `02-cargar-datos.png` | `cls` y `python app/cargar_cypher.py cypher/01_restricciones.cypher cypher/02_datos.cypher` | 8 restricciones, 8 sentencias de datos y el conteo final. Si no cabe, `02a` y `02b` |
| `03-restricciones.png` | Neo4j Desktop → **Query**: `SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties` | Tabla con las 8 restricciones |
| `04-grafo-completo.png` | En **Query**: `MATCH (n)-[r]->(m) RETURN n, r, m` | Vista de grafo con todos los nodos y relaciones |
| `05-app-usuarios.png` | `python app/main.py`, pestaña **Usuarios** | 5 usuarios con sus conteos de artículos y comentarios |
| `06-usuario-crear.png` | **Nuevo**. Nombre: `Mariana López` · Email: `mariana.lopez@blog.mx` · **Guardar** | "6 registros", "Registro creado" |
| `07-usuario-editar.png` | Con Mariana elegida, Nombre: `Mariana López Ruiz` · **Guardar** | "Registro actualizado" |
| `08-usuario-email-repetido.png` | **Nuevo**. Nombre: `Otra Ana` · Email: `ana.torres@blog.mx` · **Guardar** | Ventana de error "No se pudo guardar" (email repetido) |
| `09-usuario-eliminar-bloqueado.png` | Elige `Ana Torres` → **Eliminar** → **Sí** | Aviso: tiene 2 artículos y 3 comentarios |
| `10-usuario-eliminar.png` | Elige `Mariana López Ruiz` → **Eliminar** → **Sí**; captura después | "5 registros", "Registro eliminado" |
| `11-cypher-03.png` | Cierra la app. `cls` y `python app/cargar_cypher.py cypher/03_usuarios.cypher` | 5 sentencias; al final `usuarios_de_prueba: 0` |

```powershell
git add reporte/img/0*.png reporte/img/1*.png
git commit -m "Capturas de la configuracion y de usuarios"
git push
```

---

## 7. Parte 2 — Osvaldo: Artículos y Comentarios

### 7.1 Agregar el código y hacer los commits (uno por archivo)
Desde la raíz del repo:
```powershell
git pull --rebase

Copy-Item equipo\parte2_osvaldo\app\articulos.py app\
git add app/articulos.py
git commit -m "Pestana de articulos con autor, tags y categorias"

Copy-Item equipo\parte2_osvaldo\app\comentarios.py app\
git add app/comentarios.py
git commit -m "Pestana de comentarios ligados a usuario y articulo"

Copy-Item equipo\parte2_osvaldo\cypher\04_articulos_comentarios.cypher cypher\
git add cypher/04_articulos_comentarios.cypher
git commit -m "Operaciones CRUD de articulos y comentarios en Cypher"

git push
```
Revisa con `git log --oneline -3` que salgan tus 3 commits con tu nombre (`git log -3 --format="%an | %s"`).

### 7.2 Capturas (en este orden)
Primero recarga los datos (paso 5.7) y abre la app: `python app/main.py`. Maximiza la ventana y no le cambies el tamaño.

| Captura | Qué hacer | Qué debe verse |
|---|---|---|
| `20-articulos-lista.png` | Pestaña **Artículos**, sin elegir nada | Tabla con 8 artículos, "8 registros" |
| `21-articulo-crear.png` | Clic en **Nuevo**. Título: `Grafos en la vida diaria` · Fecha: `2026-11-24` · Texto: `Las redes de amigos, los mapas y las recomendaciones de compras se modelan como grafos.` · Autor: `Carlos Méndez` · Tags: clic en `grafos` y en `neo4j` · Categorías: clic en `Bases de Datos` · **Guardar** | Fila nueva seleccionada, "9 registros", abajo "Registro creado" |
| `22-articulo-editar.png` | Con ese artículo elegido, en Tags agrega `python` (clic) y en Categorías agrega `Ciencia de Datos` · **Guardar** | Tags: grafos, neo4j, python; Categorías: 2; "Registro actualizado" |
| `23-comentarios-lista.png` | Pestaña **Comentarios** | 14 comentarios, "14 registros" |
| `24-comentario-crear.png` | **Nuevo**. Título: `Muy interesante` · Fecha: `2026-11-24` · Texto: `No sabía que las recomendaciones usaban grafos.` · Autor: `Valeria Ortiz` · Artículo: `Grafos en la vida diaria` · **Guardar** | "15 registros", URL generada `/articulos/grafos-en-la-vida-diaria#comentario-…`, "Registro creado" |
| `25-comentario-editar.png` | Con ese comentario elegido, Texto: `No sabía que las recomendaciones de compras usaban grafos.` · **Guardar** | "Registro actualizado" |
| `26-articulo-con-comentario.png` | Pestaña **Artículos** | "Grafos en la vida diaria" con 1 en la columna Coment. |
| `27-comentario-eliminar.png` | Pestaña **Comentarios**, elige `Muy interesante`, **Eliminar** → **Sí**; captura después | "14 registros", "Registro eliminado" |
| `28-articulo-eliminar.png` | Pestaña **Artículos**, elige `Grafos en la vida diaria`, **Eliminar** → **Sí**; captura después | "8 registros", "Registro eliminado" |
| `29-cypher-04.png` | Cierra la app. En PowerShell: `cls` y luego `python app/cargar_cypher.py cypher/04_articulos_comentarios.cypher` | 9 sentencias; al final `nodos_de_prueba: 0`. Si no cabe, `29a` y `29b` |
| `30-grafo-articulo.png` | Neo4j Desktop → **Query** (o **Open → Neo4j Browser**). Ejecuta: `MATCH (a:Article {title: "Primeros pasos con Cypher"})-[r]-(n) RETURN a, r, n` | Vista de grafo: el artículo con su autor, 2 tags, 2 categorías y 2 comentarios |

### 7.3 Subir las capturas
```powershell
git pull --rebase
git add reporte/img/2*.png reporte/img/30-grafo-articulo.png
git commit -m "Capturas de articulos y comentarios"
git push
```
Avisa en el grupo cuando termines.

---

## 8. Parte 3 — Diego: Tags, Categorías y Consultas

### 8.1 Agregar el código y hacer los commits (uno por archivo)
Desde la raíz del repo:
```powershell
git pull --rebase

Copy-Item equipo\parte3_diego\app\tags.py app\
git add app/tags.py
git commit -m "Pestana de tags"

Copy-Item equipo\parte3_diego\app\categorias.py app\
git add app/categorias.py
git commit -m "Pestana de categorias"

Copy-Item equipo\parte3_diego\cypher\05_tags_categorias.cypher cypher\
git add cypher/05_tags_categorias.cypher
git commit -m "Operaciones CRUD de tags y categorias en Cypher"

Copy-Item equipo\parte3_diego\app\consultas.py app\
git add app/consultas.py
git commit -m "Pestana de consultas sobre el grafo"

Copy-Item equipo\parte3_diego\cypher\06_consultas.cypher cypher\
git add cypher/06_consultas.cypher
git commit -m "Consultas del blog en Cypher"

git push
```
Revisa con `git log -5 --format="%an | %s"` que salgan tus 5 commits con tu nombre.

### 8.2 Capturas (en este orden)
Primero recarga los datos (paso 5.7) y abre la app: `python app/main.py`. Maximiza la ventana y no le cambies el tamaño.

| Captura | Qué hacer | Qué debe verse |
|---|---|---|
| `40-tags-lista.png` | Pestaña **Tags** | 8 tags; neo4j con 4 artículos |
| `41-tag-crear.png` | **Nuevo**. Nombre: `bases-de-datos` · URL: `/tag/bases-de-datos` · **Guardar** | "9 registros", "Registro creado" |
| `42-tag-editar.png` | Con ese tag elegido, Nombre: `bd` · URL: `/tag/bd` · **Guardar** | "Registro actualizado" |
| `43-tag-repetido.png` | **Nuevo**. Nombre: `neo4j` · URL: `/tag/neo4j` · **Guardar** | Ventana de error "No se pudo guardar" (el nombre ya existe). Captura con el error visible y luego dale Aceptar |
| `44-tag-eliminar.png` | Elige `bd` → **Eliminar** → **Sí**; captura después | "8 registros", "Registro eliminado" |
| `45-categorias-lista.png` | Pestaña **Categorías** | 4 categorías; Bases de Datos con 6 artículos |
| `46-categoria-crear.png` | **Nuevo**. Nombre: `Tutoriales` · URL: `/categoria/tutoriales` · **Guardar** | "5 registros", "Registro creado" |
| `47-categoria-editar.png` | Con esa categoría elegida, Nombre: `Tutoriales y Guías` · **Guardar** | "Registro actualizado" |
| `48-categoria-eliminar.png` | Elige `Tutoriales y Guías` → **Eliminar** → **Sí**; captura después | "4 registros" |
| `49-consulta-1.png` | Pestaña **Consultas** → `1. Artículos por categoría` → **Ejecutar** | Bases de Datos 6, Programación 3, Ciencia de Datos 1, Infraestructura 1 |
| `50-consulta-2.png` | `2. Tags más usados` → **Ejecutar** | neo4j 4, cypher 3, grafos 3, mongodb 2, nosql 2, python 2, docker 1, sql 1 |
| `51-consulta-3.png` | `3. Artículos más comentados` → **Ejecutar** | "Introducción a las bases de datos de grafos" 3 arriba; "De SQL a Cypher: guía rápida" 0 al final |
| `52-consulta-4.png` | `4. Actividad de cada usuario` → **Ejecutar** | Ana Torres 2/3, Carlos Méndez 1/4, Luis Ramírez 2/3, Sofía Chávez 2/2, Valeria Ortiz 1/2 |
| `53-consulta-5.png` | `5. Artículos de un tag` → Tag: `neo4j` → **Ejecutar** | 4 artículos, el más reciente "Conectar Python con Neo4j" |
| `54-consulta-6.png` | `6. Artículos relacionados` → Artículo: `Introducción a las bases de datos de grafos` → **Ejecutar** | "MongoDB vs Neo4j: cuándo usar cada uno" con en_comun 2 arriba, luego 4 con 1 |
| `55-consulta-7.png` | `7. Quién comenta a quién` → **Ejecutar** | 12 filas; arriba Carlos Méndez → Ana Torres 2 y Carlos Méndez → Sofía Chávez 2 |
| `56-consulta-8.png` | `8. Artículos sin comentarios` → **Ejecutar** | 1 fila: "De SQL a Cypher: guía rápida", Luis Ramírez |
| `57-cypher-05.png` | Cierra la app. `cls` y `python app/cargar_cypher.py cypher/05_tags_categorias.cypher` | 9 sentencias; al final `nodos_de_prueba: 0`. Si no cabe, `57a` y `57b` |
| `58-cypher-06.png` | `cls` y `python app/cargar_cypher.py cypher/06_consultas.cypher` | 8 consultas con sus filas. Si no cabe, `58a`, `58b` |
| `59-grafo-tags.png` | Neo4j Desktop → **Query** (o Neo4j Browser). Ejecuta: `MATCH (a:Article)-[r:TAGGED_WITH]->(t:Tag) RETURN a, r, t` | Vista de grafo: 8 artículos conectados a 8 tags (18 relaciones) |

### 8.3 Subir las capturas
```powershell
git pull --rebase
git add reporte/img/4*.png reporte/img/5*.png
git commit -m "Capturas de tags, categorias y consultas"
git push
```
Avisa en el grupo cuando termines.

---

## 9. Si algo falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `No existe ...config.ini` | Falta el paso 5.6 | Hacer el paso 5.6 |
| `Unauthorized` / `authentication failure` | Contraseña incorrecta en `config.ini` | Corregirla |
| `ServiceUnavailable` / `Couldn't connect` | La base no está iniciada | Start en Neo4j Desktop |
| `ModuleNotFoundError: No module named 'neo4j'` | Falta el driver | `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'tkinter'` | Python sin Tkinter | Reinstalar Python con "tcl/tk and IDLE" |
| Error de sintaxis Cypher con `COUNT {` | Neo4j muy viejo | Crear la instancia con la versión que sugiere Neo4j Desktop (5.x o 2025.x) |
| `rejected` / `non-fast-forward` al hacer push | Otro integrante subió antes | `git pull --rebase` y luego `git push` |
| `Permission denied` / `403` al hacer push | No aceptaste la invitación | Paso 5.1 |
| Los números no coinciden con esta guía | No recargaste los datos | Paso 5.7 y repetir desde la primera captura |

## 10. Para la IA que te ayude

- Responde en español.
- No cambies el modelo de la sección 2 ni los archivos de otros integrantes.
- El código del integrante ya está escrito en su paquete: la tarea es copiarlo, hacer los commits con los mensajes exactos, ejecutar y capturar, no reescribirlo.
- No agregues coautores ni líneas extra a los mensajes de commit.
- Nunca `git add .`; solo los archivos que indica la sección del integrante.

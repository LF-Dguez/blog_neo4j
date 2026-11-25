"""
Ejecuta archivos .cypher contra la base de datos de config.ini.

Uso (desde la raiz del repositorio):
    python app/cargar_cypher.py cypher/01_restricciones.cypher cypher/02_datos.cypher

Cada archivo se divide en sentencias por el ';' al final de una linea. Las
lineas que empiezan con // son comentarios y se ignoran. Las sentencias se
ejecutan en orden; de cada una se muestra lo que cambio en la base y, si
tiene RETURN, sus primeras filas.
"""
import sys
from pathlib import Path

from conexion import BaseDatos, _a_python

MAX_FILAS = 12


def sentencias(ruta):
    """Regresa las sentencias Cypher de un archivo, sin comentarios."""
    actual, lista = [], []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if linea.strip().startswith("//"):
            continue
        actual.append(linea)
        if linea.rstrip().endswith(";"):
            texto = "\n".join(actual).strip().rstrip(";").strip()
            if texto:
                lista.append(texto)
            actual = []
    resto = "\n".join(actual).strip()
    if resto:
        lista.append(resto)
    return lista


def main(archivos):
    if not archivos:
        print(__doc__)
        sys.exit(1)

    bd = BaseDatos()
    print(f"Conectado a {bd.verificar()} ({bd.uri}, base '{bd.database}')\n")

    for archivo in archivos:
        lista = sentencias(archivo)
        print(f"== {archivo}: {len(lista)} sentencias")
        for i, cypher in enumerate(lista, 1):
            primera = cypher.splitlines()[0][:60]
            registros, resumen, _ = bd.driver.execute_query(
                cypher, database_=bd.database)
            cambios = {k: v for k, v in resumen.counters.__dict__.items()
                       if isinstance(v, int) and v and not k.startswith("_")}
            print(f"  {i:2}. {primera:<60} {cambios or ''}")
            # Si la sentencia regresa filas (RETURN), se muestran las primeras
            for registro in registros[:MAX_FILAS]:
                fila = {k: _a_python(v) for k, v in registro.data().items()}
                print(f"        {fila}")
            if len(registros) > MAX_FILAS:
                print(f"        ... {len(registros) - MAX_FILAS} filas mas")
        print()

    conteo = bd.consultar(
        "MATCH (n) WHERE n:User OR n:Article OR n:Comment OR n:Tag OR n:Category "
        "RETURN labels(n)[0] AS etiqueta, count(*) AS total ORDER BY etiqueta")
    relaciones = bd.consultar(
        "MATCH ()-[r]->() RETURN type(r) AS tipo, count(*) AS total ORDER BY tipo")
    print("Nodos en la base:")
    for fila in conteo:
        print(f"  {fila['etiqueta']:<10} {fila['total']}")
    print("Relaciones:")
    for fila in relaciones:
        print(f"  {fila['tipo']:<12} {fila['total']}")
    bd.cerrar()


if __name__ == "__main__":
    main(sys.argv[1:])

"""
Conexion con la base de datos Neo4j.

Lee los datos de conexion de config.ini (en la raiz del repositorio) y ofrece
dos metodos que usan todas las pestanas de la aplicacion:

    bd.consultar(cypher, parametros)  -> lista de diccionarios (lectura)
    bd.ejecutar(cypher, parametros)   -> lista de diccionarios (escritura)

Los valores que vienen de la interfaz siempre se pasan como parametros
($nombre en el Cypher), nunca pegados al texto de la consulta.
"""
import configparser
from pathlib import Path

from neo4j import GraphDatabase, RoutingControl
from neo4j.time import Date, DateTime

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_CONFIG = RAIZ / "config.ini"


def _a_python(valor):
    """Convierte los tipos de Neo4j a tipos simples para mostrarlos."""
    if isinstance(valor, (Date, DateTime)):
        return valor.iso_format()[:10]
    if isinstance(valor, list):
        return [_a_python(v) for v in valor]
    return valor


class BaseDatos:
    """Envuelve el driver de Neo4j con los datos de config.ini."""

    def __init__(self, archivo=ARCHIVO_CONFIG):
        if not Path(archivo).exists():
            raise FileNotFoundError(
                f"No existe {archivo}. Copia config.ejemplo.ini como config.ini "
                "y escribe la contrasena de tu base de datos.")
        config = configparser.ConfigParser(interpolation=None)
        config.read(archivo, encoding="utf-8")
        datos = config["neo4j"]
        self.uri = datos.get("uri", "bolt://localhost:7687")
        self.database = datos.get("database", "neo4j")
        self.driver = GraphDatabase.driver(
            self.uri, auth=(datos.get("usuario", "neo4j"), datos["contrasena"]))

    def verificar(self):
        """Comprueba la conexion y regresa la version del servidor."""
        self.driver.verify_connectivity()
        info = self.consultar(
            "CALL dbms.components() YIELD name, versions "
            "RETURN name, versions[0] AS version")
        return f"{info[0]['name']} {info[0]['version']}" if info else "Neo4j"

    def _correr(self, cypher, parametros, ruta):
        registros, _, _ = self.driver.execute_query(
            cypher, parametros or {}, routing_=ruta, database_=self.database)
        return [{k: _a_python(v) for k, v in r.data().items()} for r in registros]

    def consultar(self, cypher, parametros=None):
        """Ejecuta una consulta de lectura."""
        return self._correr(cypher, parametros, RoutingControl.READ)

    def ejecutar(self, cypher, parametros=None):
        """Ejecuta una consulta que crea, modifica o borra datos."""
        return self._correr(cypher, parametros, RoutingControl.WRITE)

    def transaccion(self, pasos):
        """Ejecuta varias sentencias en una sola transaccion.

        pasos: lista de (cypher, parametros). Si una falla, no se guarda
        ninguna. Regresa el resultado de la primera sentencia.
        """
        def trabajo(tx):
            resultados = []
            for cypher, parametros in pasos:
                registros = tx.run(cypher, parametros or {})
                resultados.append([{k: _a_python(v) for k, v in r.data().items()}
                                   for r in registros])
            return resultados[0] if resultados else []

        with self.driver.session(database=self.database) as sesion:
            return sesion.execute_write(trabajo)

    def cerrar(self):
        self.driver.close()

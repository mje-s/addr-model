from pathlib import Path
import sqlite3
from rdflib import Graph, URIRef, Namespace, BNode, Literal
from rdflib.namespace import DCTERMS, RDF
ADDR = Namespace("https://linked.data.gov.au/def/addr/")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")


def literal_or_iri(node, prefixes):
    x = un_prefix(node, prefixes)
    if x is not None:
        return x
    return Literal(node)


def un_prefix(prefixed_value: str, prefixes_dict: dict):
    for prefix, iri in prefixes_dict.items():
        if prefixed_value.startswith(prefix + ":"):
            return URIRef(iri + prefixed_value.replace(prefix + ":", ""))
    return None


if __name__ == "__main__":
    # connect to the SQLite DB
    DB_PATH = Path(__file__).parent / "_qld_scenarios.sqlite"
    conn = sqlite3.connect(str(DB_PATH))

    # get all the prefixes used in the relational DB
    prefixs = {}
    cur = conn.execute("SELECT prefix, iri FROM pids_prefixes")
    for row in cur:
        prefixs[row[0]] = row[1]

    # add all prefixes to the RDF Graph
    g = Graph()
    for prefix, iri in prefixs.items():
        g.bind(prefix, iri)

    # get all Address components for <http://example.com/oxford>
    cur = conn.execute("""
        SELECT
            a.pid, a.is_address_for,
            ac.type, ac.has_value, ac.has_value_text,
            g.geometry, g.type,
            aa.address_pid
        FROM addresses a
        JOIN addresses_components ac
        ON a.pid = ac.address_pid
        JOIN geocodes g
        ON a.pid = g.address_pid
        JOIN address_aliases aa
        ON a.pid = aa.alias_pid
        WHERE a.pid = 'ex:oxford';
    """)

    # loop through results, create an RDF graph
    geocode = BNode()
    for row in cur:
        addr = un_prefix(row[0], prefixs)
        g.add((addr, RDF.type, ADDR.Address))
        g.add((addr, ADDR.isAddressFor, un_prefix(row[1], prefixs)))
        bn = BNode()
        g.add((addr, ADDR.hasAddressComponent, bn))
        g.add((bn, DCTERMS.type, un_prefix(row[2], prefixs)))
        g.add((bn, ADDR.hasValue, literal_or_iri(row[3], prefixs)))
        g.add((bn, ADDR.hasValueText, Literal(row[4])))
        g.add((addr, ADDR.hasGeocode, geocode))
        g.add((geocode, GEO.asWKT, Literal(row[5])))
        g.add((geocode, DCTERMS.type, un_prefix(row[6], prefixs)))
        g.add((addr, ADDR.isAliasOf, un_prefix(row[7], prefixs)))

    # print the graph for validation
    print(g.serialize())

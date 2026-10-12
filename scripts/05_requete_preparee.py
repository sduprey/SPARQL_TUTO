"""Étape 5 — Requête préparée et paramètres (initBindings)."""
from rdflib.namespace import FOAF
from rdflib.plugins.sparql import prepareQuery

from commun import EX, charger_graphe, titre

g = charger_graphe()

q = prepareQuery(
    "SELECT ?nom WHERE { ?p foaf:name ?nom ; ex:city ?ville . } ORDER BY ?nom",
    initNs={"foaf": FOAF, "ex": EX},
)

for ville in (EX.paris, EX.lyon):
    titre(f"Habitants de {ville.split('/')[-1]}")
    for ligne in g.query(q, initBindings={"ville": ville}):
        print(" -", ligne.nom)

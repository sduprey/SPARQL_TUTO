"""Étape 9 — Inférence RDFS (RDF Schema) avec owlrl."""
from owlrl import DeductiveClosure, RDFS_Semantics
from rdflib.namespace import FOAF, RDF, RDFS

from commun import EX, charger_graphe, titre

g = charger_graphe()
g.add((FOAF.Person, RDFS.subClassOf, EX.Agent))

titre("Avant inférence")
print("Alice est un ex:Agent ?", (EX.alice, RDF.type, EX.Agent) in g, f"({len(g)} triplets)")

DeductiveClosure(RDFS_Semantics).expand(g)

titre("Après inférence")
print("Alice est un ex:Agent ?", (EX.alice, RDF.type, EX.Agent) in g, f"({len(g)} triplets)")
print("Note : l'inférence RDFS ajoute aussi beaucoup de triplets « axiomatiques ».")

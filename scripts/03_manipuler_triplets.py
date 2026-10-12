"""Étape 3 — Manipuler les triplets en Python, sans SPARQL."""
from rdflib import Literal
from rdflib.namespace import FOAF, RDF

from commun import EX, charger_graphe, titre

g = charger_graphe()

titre("Ajout et retrait")
g.add((EX.david, RDF.type, FOAF.Person))
g.add((EX.david, FOAF.name, Literal("David")))
g.remove((EX.bob, FOAF.knows, None))  # None = joker
print(f"{len(g)} triplets après modification")

titre("Une seule valeur : value()")
print(g.value(EX.alice, FOAF.name))

titre("Plusieurs valeurs : objects()")
for ami in g.objects(EX.alice, FOAF.knows):
    print(" -", g.value(ami, FOAF.name))

titre("Motif de triplet : triples()")
for s, _, o in g.triples((None, FOAF.age, None)):
    print(f" - {s} : {o.toPython()} ({type(o.toPython()).__name__})")

titre("Test d'existence")
print((EX.alice, FOAF.knows, EX.bob) in g)
print((EX.bob, FOAF.knows, EX.chloe) in g)

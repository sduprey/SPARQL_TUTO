"""Étape 1 — Charger un fichier Turtle dans un graphe rdflib."""
from rdflib import Graph

from commun import FICHIER_PERSONNES, titre

g = Graph()
g.parse(FICHIER_PERSONNES)  # format déduit de l'extension .ttl
titre("Chargement")
print(f"{len(g)} triplets chargés depuis {FICHIER_PERSONNES.name}")

# On peut aussi parser une chaîne directement
texte = """
@prefix ex: <http://example.org/> .
ex:a ex:relie ex:b .
"""
g2 = Graph().parse(data=texte, format="turtle")
titre("Parse depuis une chaîne")
print(f"{len(g2)} triplet(s)")

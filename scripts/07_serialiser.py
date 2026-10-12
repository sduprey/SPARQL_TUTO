"""Étape 7 — Sérialiser et convertir entre formats."""
from commun import SORTIES, charger_graphe, titre

g = charger_graphe()
SORTIES.mkdir(exist_ok=True)

titre("Turtle (chaîne)")
print(g.serialize(format="turtle")[:400], "...")

for fmt, ext in [("json-ld", "jsonld"), ("nt", "nt"), ("xml", "rdf")]:
    chemin = SORTIES / f"personnes.{ext}"
    g.serialize(chemin, format=fmt, encoding="utf-8")
    print(f"Écrit : {SORTIES.name}/{chemin.name} ({fmt})")

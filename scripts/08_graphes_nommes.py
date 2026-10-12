"""Étape 8 — Graphes nommés avec Dataset."""
from rdflib import Dataset, Literal, URIRef

from commun import EX, FICHIER_PERSONNES, SORTIES, titre

ds = Dataset()
ds.bind("ex", EX)

personnes = ds.graph(URIRef("http://example.org/g/personnes"))
personnes.parse(FICHIER_PERSONNES)

rh = ds.graph(URIRef("http://example.org/g/rh"))
rh.add((EX.alice, EX.salaire, Literal(52000)))
rh.add((EX.bob, EX.salaire, Literal(47000)))

titre("Nombre de triplets par graphe")
for ligne in ds.query("""
  SELECT ?g (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g ORDER BY ?g
"""):
    print(f" - {ligne.g} : {ligne.n}")

titre("Jointure entre deux graphes nommés")
for ligne in ds.query("""
  PREFIX ex:   <http://example.org/>
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  SELECT ?nom ?salaire WHERE {
    GRAPH <http://example.org/g/personnes> { ?p foaf:name ?nom }
    GRAPH <http://example.org/g/rh>        { ?p ex:salaire ?salaire }
  } ORDER BY ?nom
"""):
    print(f" - {ligne.nom} : {ligne.salaire}")

SORTIES.mkdir(exist_ok=True)
ds.serialize(SORTIES / "donnees.trig", format="trig")
print(f"\nDataset écrit dans {SORTIES.name}/donnees.trig")

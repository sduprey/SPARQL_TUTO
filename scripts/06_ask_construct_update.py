"""Étape 6 — ASK, CONSTRUCT et SPARQL Update."""
from commun import SORTIES, charger_graphe, titre

g = charger_graphe()

titre("ASK")
print("Quelqu'un a 28 ans ?",
      bool(g.query("ASK { ?p <http://xmlns.com/foaf/0.1/age> 28 }")))

titre("CONSTRUCT : relation « connaît » inversée")
inverse = g.query("""
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  CONSTRUCT { ?b foaf:knows ?a } WHERE { ?a foaf:knows ?b }
""").graph
inverse.bind("ex", "http://example.org/")
print(inverse.serialize(format="turtle"))

titre("SPARQL Update")
g.update("""
  PREFIX ex:   <http://example.org/>
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  INSERT DATA { ex:chloe foaf:age 30 . } ;
  DELETE { ?p foaf:name "Bob" }
  INSERT { ?p foaf:name "Robert" }
  WHERE  { ?p foaf:name "Bob" }
""")
for ligne in g.query("""
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  SELECT ?nom ?age WHERE { ?p foaf:name ?nom ; foaf:age ?age } ORDER BY ?nom
"""):
    print(" -", ligne.nom, ligne.age)

SORTIES.mkdir(exist_ok=True)
g.serialize(SORTIES / "personnes_modifie.ttl", format="turtle")
print(f"\nGraphe modifié écrit dans {SORTIES.name}/personnes_modifie.ttl")

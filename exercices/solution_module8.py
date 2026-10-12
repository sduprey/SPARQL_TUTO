"""Correction de l'exercice du module 8."""
import sys
from pathlib import Path

import pandas as pd
from rdflib import Literal
from rdflib.namespace import FOAF, RDF

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from commun import EX, charger_graphe  # noqa: E402

g = charger_graphe()

# 2. Ajouter Emma avec l'API Python
g.add((EX.emma, RDF.type, FOAF.Person))
g.add((EX.emma, FOAF.name, Literal("Emma")))
g.add((EX.emma, FOAF.age, Literal(25)))
g.add((EX.emma, EX.city, EX.lyon))
g.add((EX.emma, FOAF.knows, EX.bob))

# 3. Requête de l'exercice 3
res = g.query("""
  PREFIX ex: <http://example.org/>
  SELECT ?ville (COUNT(?p) AS ?nb)
  WHERE { ?p ex:city/ex:label ?ville . }
  GROUP BY ?ville
  ORDER BY DESC(?nb) ?ville
""")

# 4. DataFrame pandas
df = pd.DataFrame(
    [{"ville": str(r.ville), "nb": r.nb.toPython()} for r in res]
)
print(df.to_string(index=False))

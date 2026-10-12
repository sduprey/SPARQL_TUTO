"""Étape 4 — Requête SELECT et conversion vers pandas."""
import pandas as pd

from commun import charger_graphe, titre

g = charger_graphe()

requete = """
PREFIX ex:   <http://example.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?nom ?age ?ville
WHERE {
  ?p foaf:name ?nom ;
     ex:city/ex:label ?ville .
  OPTIONAL { ?p foaf:age ?age }
}
ORDER BY ?nom
"""

titre("Parcours ligne par ligne")
res = g.query(requete)
for ligne in res:
    print(ligne.nom, ligne.age, ligne.ville)  # None si la variable n'est pas liée


def vers_dataframe(resultats) -> pd.DataFrame:
    """Convertit un résultat SELECT rdflib en DataFrame de valeurs Python."""
    colonnes = [str(v) for v in resultats.vars]
    lignes = [
        {k: (v.toPython() if v is not None else None) for k, v in r.asdict().items()}
        for r in resultats
    ]
    return pd.DataFrame(lignes, columns=colonnes)


titre("DataFrame pandas")
print(vers_dataframe(res))

titre("Format de résultats SPARQL JSON")
print(res.serialize(format="json").decode()[:300], "...")

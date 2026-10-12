"""Bonus module 7 — Interroger Wikidata avec SPARQLWrapper (nécessite Internet)."""
from SPARQLWrapper import JSON, SPARQLWrapper

from commun import titre

# Wikidata exige un User-Agent explicite : mettez votre propre contact.
sparql = SPARQLWrapper(
    "https://query.wikidata.org/sparql",
    agent="formation-sparql/1.0 (votre.adresse@example.org)",
)
sparql.setQuery("""
  SELECT ?villeLabel ?pop WHERE {
    ?ville wdt:P31 wd:Q515 ; wdt:P17 wd:Q142 ; wdt:P1082 ?pop .
    SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
  } ORDER BY DESC(?pop) LIMIT 5
""")
sparql.setReturnFormat(JSON)

titre("5 villes françaises les plus peuplées (Wikidata)")
for r in sparql.query().convert()["results"]["bindings"]:
    print(f" - {r['villeLabel']['value']} : {int(float(r['pop']['value'])):,}".replace(",", " "))

# Formation SPARQL — tutoriel rdflib en Python

Code du module 8 de la formation SPARQL (SPARQL Protocol and RDF Query Language) :
manipulation de graphes RDF (Resource Description Framework) avec rdflib, plus un
script bonus pour interroger Wikidata (module 7).

## Installation avec uv

```bash
# Installer uv si besoin : https://docs.astral.sh/uv/getting-started/installation/
cd formation-sparql-rdflib
uv sync                       # crée .venv et installe rdflib, pandas, owlrl, SPARQLWrapper
uv sync --extra oxigraph      # optionnel : stockage Oxigraph pour les gros graphes
```

## Lancer les scripts

```bash
uv run scripts/01_charger_graphe.py
uv run scripts/04_requete_select.py
# … et ainsi de suite
```

Pour tout lancer d'un coup (sauf Wikidata, qui demande Internet) :

```bash
for f in scripts/0*.py; do echo "### $f"; uv run "$f"; done
```

| Script | Étape du tutoriel |
| --- | --- |
| `01_charger_graphe.py` | Charger un fichier Turtle, parser une chaîne |
| `02_objets_de_base.py` | URIRef, Literal, BNode, Namespace |
| `03_manipuler_triplets.py` | add, remove, value, objects, triples |
| `04_requete_select.py` | SELECT, conversion pandas, résultats JSON |
| `05_requete_preparee.py` | prepareQuery et initBindings |
| `06_ask_construct_update.py` | ASK, CONSTRUCT, SPARQL Update |
| `07_serialiser.py` | Conversion Turtle, JSON-LD, N-Triples, RDF/XML |
| `08_graphes_nommes.py` | Dataset et graphes nommés, export TriG |
| `09_inference_rdfs.py` | Inférence RDFS (RDF Schema) avec owlrl |
| `10_wikidata_sparqlwrapper.py` | Bonus : requête Wikidata (Internet requis) |

Les fichiers produits sont écrits dans `sorties/`.

## Données

`data/personnes.ttl` : le graphe fil rouge (Alice, Bob, Chloé, Paris, Lyon), 19 triplets.
Ajoutez vos propres fichiers `.ttl` dans `data/` et chargez-les avec
`charger_graphe(DATA / "mon_fichier.ttl")` (voir `scripts/commun.py`).

## Exercice

```bash
uv run exercices/exercice_module8.py    # à compléter
uv run exercices/solution_module8.py    # correction
```

## Jouer avec SPARQL en interactif

```bash
uv run python
>>> import sys; sys.path.insert(0, "scripts")
>>> from commun import charger_graphe
>>> g = charger_graphe()
>>> for r in g.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"): print(r)
```

Ou avec Jupyter : `uv add --dev jupyterlab` puis `uv run jupyter lab`.

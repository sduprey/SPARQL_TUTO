"""Exercice du module 8 — à compléter.

1. Charger data/personnes.ttl.
2. Ajouter avec l'API Python (g.add) une personne ex:emma :
   type foaf:Person, nom "Emma", 25 ans, habitant ex:lyon, connaissant ex:bob.
3. Exécuter en Python la requête de l'exercice 3 (nombre de personnes par ville).
4. Afficher le résultat sous forme de DataFrame pandas.

Résultat attendu : Paris 2, Lyon 2.
Lancer avec : uv run exercices/exercice_module8.py
Correction  : exercices/solution_module8.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from commun import EX, charger_graphe  # noqa: E402

g = charger_graphe()

# À vous de jouer !

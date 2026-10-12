"""Éléments partagés par tous les scripts du tutoriel."""
from pathlib import Path

from rdflib import Graph, Namespace

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
SORTIES = RACINE / "sorties"
FICHIER_PERSONNES = DATA / "personnes.ttl"

EX = Namespace("http://example.org/")


def charger_graphe(chemin: Path = FICHIER_PERSONNES) -> Graph:
    """Charge un fichier RDF dans un nouveau graphe et déclare le préfixe ex:."""
    g = Graph()
    g.parse(chemin)
    g.bind("ex", EX)
    return g


def titre(texte: str) -> None:
    print(f"\n=== {texte} ===")

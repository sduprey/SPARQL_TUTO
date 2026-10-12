"""Étape 2 — Les objets de base : URIRef, Literal, BNode, Namespace."""
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import FOAF, XSD

from commun import EX, titre

alice = EX.alice
titre("URIRef (IRI)")
print(alice, alice == URIRef("http://example.org/alice"))

titre("Literal")
age = Literal(34)
print(repr(age), "->", age.datatype)
nom = Literal("Paris", lang="fr")
print(repr(nom), "langue :", nom.language)
print("Literal('34') == Literal(34) ?", Literal("34") == Literal(34))
print("Literal('34', datatype=XSD.integer) == Literal(34) ?",
      Literal("34", datatype=XSD.integer) == Literal(34))

titre("BNode (nœud anonyme)")
print(repr(BNode()))

titre("Namespace")
print(FOAF.name, EX["nom-compose"])

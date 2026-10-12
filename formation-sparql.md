# Formation SPARQL

Oct 12, 2026 · @Stefan

## Introduction

Cette formation mène de zéro à l'écriture de requêtes SPARQL (SPARQL Protocol and RDF Query Language) avancées en 8 modules d'environ 1 h chacun, plus une série d'exercices corrigés et une annexe sur la connexion d'un LLM (Large Language Model) à un serveur MCP (Model Context Protocol) depuis AWS AgentCore.

SPARQL est le langage de requête standard du W3C (World Wide Web Consortium) pour les données RDF (Resource Description Framework) : des graphes de connaissances où tout s'exprime en triplets sujet – prédicat – objet. C'est l'équivalent du SQL (Structured Query Language) pour les graphes, mais sans schéma fixe : on interroge par **motifs de graphe** plutôt que par jointures de tables.

**Objectifs à l'issue de la formation**

- Lire et écrire des données RDF au format Turtle (Terse RDF Triple Language).
- Écrire des requêtes SELECT, ASK, CONSTRUCT et DESCRIBE.
- Maîtriser les filtres, les jointures optionnelles, les agrégations et les chemins de propriétés.
- Interroger Wikidata et fédérer plusieurs points d'accès (endpoints).
- Modifier un graphe avec SPARQL Update et écrire des requêtes performantes.

**Prérequis** : bases de SQL (Structured Query Language) utiles mais non indispensables ; aucune connaissance du Web sémantique n'est requise.

**Environnement de travail** : tous les exemples marqués « Wikidata » s'exécutent tels quels sur le [Wikidata Query Service](https://query.wikidata.org/). Pour les exemples sur petit graphe local, utiliser [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) ou, en Python, la bibliothèque [rdflib](https://rdflib.readthedocs.io/).

| Module | Thème | Durée indicative |
| --- | --- | --- |
| 1 | Le modèle RDF (Resource Description Framework) | 45 min |
| 2 | Premières requêtes SELECT | 1 h |
| 3 | Filtres, OPTIONAL, UNION, MINUS, tri | 1 h |
| 4 | Agrégations, sous-requêtes, BIND, VALUES | 1 h |
| 5 | Chemins de propriétés, CONSTRUCT, ASK, DESCRIBE | 1 h |
| 6 | Fédération (SERVICE) et Wikidata | 1 h |
| 7 | SPARQL Update, graphes nommés, performance | 1 h |
| — | Exercices corrigés | 1 h 30 |

## Module 1 — Le modèle RDF (Resource Description Framework)

En RDF, toute connaissance est un **triplet** : un sujet, un prédicat (la relation) et un objet. Un ensemble de triplets forme un graphe orienté et étiqueté : les sujets et objets sont les nœuds, les prédicats sont les arcs.

### Les trois types de termes

| Terme | Rôle possible | Exemple |
| --- | --- | --- |
| IRI (Internationalized Resource Identifier) | sujet, prédicat, objet | `<http://example.org/alice>` |
| Littéral (valeur, avec type ou langue) | objet uniquement | `"Alice"@fr`, `"42"^^xsd:integer` |
| Nœud anonyme (blank node) | sujet, objet | `_:b1` ou `[ ... ]` |

L'IRI (Internationalized Resource Identifier) identifie une ressource de façon globale : deux jeux de données qui utilisent la même IRI parlent de la même chose, c'est ce qui permet de les fusionner sans effort.

### Le format Turtle (Terse RDF Triple Language)

Turtle est la syntaxe la plus lisible pour écrire du RDF, et celle de SPARQL en reprend l'essentiel. Voici le petit graphe qui servira de fil rouge aux modules 2 à 5 :

```turtle
@prefix ex:   <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ex:alice a foaf:Person ;
    foaf:name "Alice" ;
    foaf:age  "34"^^xsd:integer ;
    ex:city   ex:paris ;
    foaf:knows ex:bob, ex:chloe .

ex:bob a foaf:Person ;
    foaf:name "Bob" ;
    foaf:age  28 ;
    ex:city   ex:lyon ;
    foaf:knows ex:chloe .

ex:chloe a foaf:Person ;
    foaf:name "Chloé" ;
    ex:city   ex:paris ;
    foaf:mbox <mailto:chloe@example.org> .

ex:paris ex:label "Paris"@fr ; ex:population 2100000 .
ex:lyon  ex:label "Lyon"@fr  ; ex:population 520000 .
```

### Les raccourcis Turtle à connaître

- `@prefix ex: <http://example.org/> .` déclare un préfixe : `ex:alice` vaut `<http://example.org/alice>`.
- `;` répète le même sujet avec un nouveau prédicat.
- `,` répète le même sujet et le même prédicat avec un nouvel objet.
- `a` est l'abréviation de `rdf:type` (l'appartenance à une classe).
- `28` est un raccourci pour `"28"^^xsd:integer` (XSD = XML Schema Definition, les types de données standard).

### Vocabulaires courants

| Préfixe | Vocabulaire | Usage |
| --- | --- | --- |
| `rdf:` | RDF (Resource Description Framework) | `rdf:type` |
| `rdfs:` | RDFS (RDF Schema) | `rdfs:label`, `rdfs:subClassOf` |
| `owl:` | OWL (Web Ontology Language) | `owl:sameAs`, ontologies |
| `foaf:` | FOAF (Friend of a Friend) | personnes et relations |
| `skos:` | SKOS (Simple Knowledge Organization System) | thésaurus, taxonomies |
| `schema:` | Schema.org | entités du web |

**À retenir** : il n'y a pas de schéma imposé. Chloé n'a pas d'âge, Alice n'a pas d'adresse électronique : en RDF, une information absente n'est pas « NULL », elle n'existe tout simplement pas. Cela aura des conséquences directes au module 3 (OPTIONAL).

## Module 2 — Premières requêtes SELECT

Une requête SPARQL (SPARQL Protocol and RDF Query Language) décrit un **motif de graphe** contenant des variables (`?x`) ; le moteur renvoie toutes les façons de remplacer ces variables pour que le motif existe dans les données.

### Anatomie d'une requête

```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>   # 1. déclaration des préfixes

SELECT ?nom                                 # 2. forme du résultat
WHERE {                                     # 3. motif de graphe
  ?personne a foaf:Person ;
            foaf:name ?nom .
}
```

Résultat sur le graphe du module 1 : `"Alice"`, `"Bob"`, `"Chloé"`.

### Motif de triplet de base (BGP, Basic Graph Pattern)

Un BGP (Basic Graph Pattern) est une suite de motifs de triplets séparés par `.`. Une variable qui apparaît dans plusieurs triplets crée une **jointure** implicite, comme un `JOIN` en SQL (Structured Query Language) :

```sparql
PREFIX ex:   <http://example.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

# Qui habite à Paris ?
SELECT ?nom
WHERE {
  ?p foaf:name ?nom ;
     ex:city   ?ville .
  ?ville ex:label "Paris"@fr .
}
```

Résultat : `"Alice"`, `"Chloé"`. La variable `?ville` relie les deux parties du motif.

### Plusieurs variables, `*` et `DISTINCT`

```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

# Toutes les relations « connaît »
SELECT ?a ?b
WHERE {
  ?x foaf:knows ?y .
  ?x foaf:name ?a .
  ?y foaf:name ?b .
}
```

| ?a | ?b |
| --- | --- |
| Alice | Bob |
| Alice | Chloé |
| Bob | Chloé |

- `SELECT *` renvoie toutes les variables du motif.
- `SELECT DISTINCT ?ville` supprime les doublons (sans lui, Paris apparaîtrait deux fois si l'on listait les villes des personnes).

### Explorer un graphe inconnu

Le réflexe face à un point d'accès (endpoint) que l'on ne connaît pas : regarder quels prédicats et quelles classes il contient.

```sparql
# Les prédicats utilisés
SELECT DISTINCT ?p WHERE { ?s ?p ?o } LIMIT 100

# Les classes utilisées
SELECT DISTINCT ?classe WHERE { ?s a ?classe } LIMIT 100
```

### Pièges classiques

- **Oublier le point** entre deux triplets : erreur de syntaxe.
- **Littéral avec langue** : `?v ex:label "Paris"` ne trouve **pas** `"Paris"@fr`. Une chaîne sans langue et une chaîne marquée `@fr` sont deux valeurs différentes.
- **Préfixe non déclaré** : chaque requête doit déclarer ses préfixes (Wikidata en prédéclare une partie, ce qui n'est pas le cas partout).
- **Ordre des résultats** : sans `ORDER BY` (module 3), il n'est jamais garanti.

## Module 3 — FILTER, OPTIONAL, UNION, MINUS et tri

Ces opérateurs transforment le motif de base : `FILTER` restreint, `OPTIONAL` complète sans exclure, `UNION` additionne, `MINUS` soustrait. Les préfixes `ex:` et `foaf:` du module 1 sont sous-entendus dans les exemples.

### FILTER : restreindre les solutions

```sparql
SELECT ?nom ?age
WHERE {
  ?p foaf:name ?nom ; foaf:age ?age .
  FILTER (?age >= 30)
}
```

Fonctions de filtre les plus utiles :

| Fonction | Rôle | Exemple |
| --- | --- | --- |
| `REGEX` (regular expression) | expression régulière | `FILTER REGEX(?nom, "^Al", "i")` |
| `CONTAINS`, `STRSTARTS`, `STRENDS` | test de sous-chaîne | `FILTER CONTAINS(?nom, "lo")` |
| `LANG`, `LANGMATCHES` | langue d'un littéral | `FILTER (LANG(?l) = "fr")` |
| `STR`, `LCASE`, `UCASE` | conversion de chaîne | `FILTER (LCASE(STR(?nom)) = "bob")` |
| `BOUND` | variable liée ou non | `FILTER (!BOUND(?mail))` |
| `isIRI`, `isLiteral`, `isBlank` | type de terme | `FILTER isIRI(?o)` |
| `IN`, `NOT IN` | appartenance à une liste | `FILTER (?ville IN (ex:paris, ex:lyon))` |
| `NOT EXISTS`, `EXISTS` | présence d'un sous-motif | `FILTER NOT EXISTS { ?p foaf:mbox ?m }` |

Opérateurs logiques : `&&` (et), `||` (ou), `!` (non).

### OPTIONAL : la jointure externe gauche

Sans `OPTIONAL`, une personne sans âge disparaît du résultat. Avec, la variable reste simplement non liée (cellule vide), comme un `LEFT JOIN` en SQL (Structured Query Language).

```sparql
SELECT ?nom ?age ?mail
WHERE {
  ?p a foaf:Person ; foaf:name ?nom .
  OPTIONAL { ?p foaf:age  ?age }
  OPTIONAL { ?p foaf:mbox ?mail }
}
```

| ?nom | ?age | ?mail |
| --- | --- | --- |
| Alice | 34 |  |
| Bob | 28 |  |
| Chloé |  | mailto:chloe@example.org |

**Piège** : deux propriétés facultatives indépendantes doivent aller dans deux blocs `OPTIONAL` distincts. Dans un seul bloc, il faudrait que les deux existent ensemble.

### UNION : l'une ou l'autre alternative

```sparql
# Personnes habitant Lyon OU âgées de plus de 30 ans
SELECT DISTINCT ?nom
WHERE {
  ?p foaf:name ?nom .
  { ?p ex:city ex:lyon }
  UNION
  { ?p foaf:age ?age . FILTER (?age > 30) }
}
```

### MINUS et FILTER NOT EXISTS : exclure

```sparql
# Personnes sans adresse électronique
SELECT ?nom
WHERE {
  ?p a foaf:Person ; foaf:name ?nom .
  MINUS { ?p foaf:mbox ?m }
}
```

Les deux formes donnent ici le même résultat (Alice, Bob). Elles diffèrent quand le bloc exclu ne partage aucune variable avec le reste : `MINUS` n'exclut alors rien, `FILTER NOT EXISTS` exclut tout. En pratique, `FILTER NOT EXISTS` est le choix le plus prévisible.

### Trier et paginer

```sparql
SELECT ?nom ?age
WHERE { ?p foaf:name ?nom . OPTIONAL { ?p foaf:age ?age } }
ORDER BY DESC(?age) ?nom
LIMIT 10
OFFSET 0
```

- `ORDER BY ASC(?x)` (par défaut) ou `DESC(?x)`, plusieurs clés possibles.
- `LIMIT` et `OFFSET` paginent ; `OFFSET` n'a de sens qu'avec un `ORDER BY`, sinon l'ordre change d'une exécution à l'autre.

## Module 4 — Agrégations, sous-requêtes, BIND et VALUES

SPARQL 1.1 apporte les mêmes outils analytiques que SQL (Structured Query Language) : regroupement, agrégats, calculs de colonnes et sous-requêtes.

### GROUP BY et fonctions d'agrégation

```sparql
# Nombre d'habitants du graphe par ville
SELECT ?ville (COUNT(?p) AS ?nb) (AVG(?age) AS ?ageMoyen)
WHERE {
  ?p ex:city ?v .
  ?v ex:label ?ville .
  OPTIONAL { ?p foaf:age ?age }
}
GROUP BY ?ville
ORDER BY DESC(?nb)
```

| ?ville | ?nb | ?ageMoyen |
| --- | --- | --- |
| Paris | 2 | 34 |
| Lyon | 1 | 28 |

Agrégats disponibles : `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `SAMPLE` (une valeur au hasard du groupe), `GROUP_CONCAT` (concaténation, avec `; SEPARATOR=", "`).

**Règle** : toute variable du `SELECT` qui n'est pas agrégée doit figurer dans le `GROUP BY`. Sinon, l'envelopper dans `SAMPLE(...)`.

### HAVING : filtrer après regroupement

```sparql
# Personnes qui connaissent au moins 2 personnes
SELECT ?nom (COUNT(?ami) AS ?nbAmis)
WHERE { ?p foaf:name ?nom ; foaf:knows ?ami . }
GROUP BY ?nom
HAVING (COUNT(?ami) >= 2)
```

Résultat : Alice, 2. `FILTER` agit avant le regroupement, `HAVING` après.

### BIND : calculer une nouvelle variable

```sparql
SELECT ?nom ?categorie
WHERE {
  ?p foaf:name ?nom ; foaf:age ?age .
  BIND (IF(?age >= 30, "senior", "junior") AS ?categorie)
  BIND (CONCAT("Fiche de ", ?nom) AS ?titre)
}
```

Fonctions utiles dans un `BIND` : `IF`, `COALESCE` (première valeur non vide), `CONCAT`, `STRLEN`, `SUBSTR`, `YEAR`, `NOW`, `IRI` (fabriquer une IRI, Internationalized Resource Identifier), arithmétique `+ - * /`.

### VALUES : injecter une table de valeurs

```sparql
SELECT ?nom ?pop
WHERE {
  VALUES ?nom { "Alice" "Bob" }
  ?p foaf:name ?nom ; ex:city/ex:population ?pop .
}
```

`VALUES` est l'outil idéal pour paramétrer une requête depuis un programme ou tester une liste d'identifiants. Il accepte plusieurs colonnes : `VALUES (?x ?y) { (1 2) (3 4) }`. (Le `/` est un chemin de propriétés, détaillé au module 5.)

### Sous-requêtes

Une sous-requête est un `SELECT` complet entre accolades. Elle est évaluée en premier, puis jointe au reste par ses variables projetées.

```sparql
# Les personnes de la ville la plus peuplée
SELECT ?nom
WHERE {
  {
    SELECT ?v WHERE { ?v ex:population ?pop }
    ORDER BY DESC(?pop) LIMIT 1
  }
  ?p ex:city ?v ; foaf:name ?nom .
}
```

Résultat : Alice, Chloé. Usage typique : un « top N » ou un agrégat que l'on réutilise ensuite comme filtre.

## Module 5 — Chemins de propriétés, CONSTRUCT, ASK, DESCRIBE

Les chemins de propriétés parcourent le graphe sur plusieurs sauts sans variables intermédiaires ; ASK, CONSTRUCT et DESCRIBE renvoient autre chose qu'un tableau.

### Chemins de propriétés (property paths)

| Syntaxe | Sens | Exemple |
| --- | --- | --- |
| `p1/p2` | séquence | `?p ex:city/ex:label ?ville` |
| `p1\|p2` | alternative | `?x rdfs:label\|foaf:name ?nom` |
| `^p` | sens inverse | `ex:paris ^ex:city ?habitant` |
| `p*` | zéro saut ou plus | `?c rdfs:subClassOf* ex:Animal` |
| `p+` | un saut ou plus | `ex:alice foaf:knows+ ?x` |
| `p?` | zéro ou un saut | `ex:alice foaf:knows? ?x` |
| `!p` | tout prédicat sauf p | `?s !rdf:type ?o` |

```sparql
# Tous ceux qu'Alice connaît, directement ou indirectement
SELECT DISTINCT ?nom
WHERE { ex:alice foaf:knows+/foaf:name ?nom . }
```

Résultat : Bob, Chloé. Le cas d'usage roi est la hiérarchie : `?x wdt:P31/wdt:P279* wd:Q5` sur Wikidata signifie « instance d'une sous-classe, à n'importe quelle profondeur, de être humain ».

**Piège** : `*` et `+` sur un graphe dense sont coûteux ; toujours ancrer une extrémité du chemin sur une constante.

### ASK : vrai ou faux

```sparql
ASK { ex:bob foaf:knows ex:alice }
```

Renvoie `false`. Idéal pour des contrôles de qualité de données ou des tests automatisés.

### CONSTRUCT : produire un nouveau graphe

`CONSTRUCT` renvoie des triplets RDF (Resource Description Framework) au lieu d'un tableau. C'est l'outil de transformation : changer de vocabulaire, déduire des relations, extraire un sous-graphe.

```sparql
PREFIX schema: <https://schema.org/>

# Traduire FOAF (Friend of a Friend) vers Schema.org et rendre « connaît » symétrique
CONSTRUCT {
  ?p a schema:Person ;
     schema:name  ?nom ;
     schema:knows ?q .
  ?q schema:knows ?p .
}
WHERE {
  ?p foaf:name ?nom .
  OPTIONAL { ?p foaf:knows ?q }
}
```

### DESCRIBE : « tout sur une ressource »

```sparql
DESCRIBE ex:alice
```

Le moteur renvoie un graphe décrivant la ressource ; son contenu exact dépend de l'implémentation (souvent tous les triplets où elle est sujet). À réserver à l'exploration, jamais à du code de production.

### Les quatre formes en résumé

| Forme | Renvoie | Usage |
| --- | --- | --- |
| `SELECT` | un tableau de variables | analyse, extraction |
| `ASK` | un booléen | tests, contrôles |
| `CONSTRUCT` | un graphe RDF selon un gabarit | transformation, ETL (Extract, Transform, Load) |
| `DESCRIBE` | un graphe RDF choisi par le moteur | exploration |

## Module 6 — Wikidata en pratique et requêtes fédérées (SERVICE)

Wikidata est le plus grand graphe de connaissances ouvert interrogeable en SPARQL (SPARQL Protocol and RDF Query Language). Tout ce module s'exécute sur le [Wikidata Query Service](https://query.wikidata.org/), qui prédéclare les préfixes `wd:`, `wdt:`, `p:`, `ps:`, `pq:`, `wikibase:` et `bd:`.

### Le modèle de données Wikidata

- Les **entités** sont des identifiants `Q` : `wd:Q90` = Paris, `wd:Q142` = France, `wd:Q5` = être humain.
- Les **propriétés** sont des identifiants `P` : `P31` = nature de l'élément (instance of), `P279` = sous-classe de, `P17` = pays, `P1082` = population, `P569` = date de naissance, `P106` = occupation.
- `wdt:` donne la valeur **directe** (la meilleure valeur) ; `p:` / `ps:` / `pq:` donnent accès à la déclaration complète avec ses qualificatifs (date, source…).

Pour trouver un identifiant, chercher l'élément sur wikidata.org, ou taper `Ctrl+Espace` dans l'éditeur du service de requêtes pour l'autocomplétion.

### Le service d'étiquettes

```sparql
# Villes françaises de plus de 200 000 habitants (Wikidata)
SELECT ?ville ?villeLabel ?pop
WHERE {
  ?ville wdt:P31/wdt:P279* wd:Q515 ;   # instance d'une sous-classe de « ville »
         wdt:P17 wd:Q142 ;              # pays : France
         wdt:P1082 ?pop .
  FILTER (?pop > 200000)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
ORDER BY DESC(?pop)
```

Le service `wikibase:label` crée automatiquement `?villeLabel` pour toute variable `?ville`, dans la première langue disponible de la liste.

### Qualificatifs : l'historique d'une valeur

```sparql
# Évolution de la population de Paris, avec la date de chaque mesure (Wikidata)
SELECT ?pop ?date
WHERE {
  wd:Q90 p:P1082 ?decl .          # la déclaration « population »
  ?decl ps:P1082 ?pop ;           # sa valeur
        pq:P585  ?date .          # qualificatif « date » (point in time)
}
ORDER BY ?date
```

| Préfixe | Pointe vers |
| --- | --- |
| `wdt:P1082` | la valeur directe (la plus récente ou préférée) |
| `p:P1082` | le nœud de déclaration |
| `ps:P1082` | la valeur portée par la déclaration |
| `pq:P585` | un qualificatif de la déclaration |

### Un exemple plus riche

```sparql
# Mathématiciens et mathématiciennes français nés après 1950, avec leur image si elle existe (Wikidata)
SELECT ?personne ?personneLabel ?naissance ?image
WHERE {
  ?personne wdt:P106 wd:Q170790 ;    # occupation : mathématicien
            wdt:P27  wd:Q142 ;       # nationalité : France
            wdt:P569 ?naissance .
  FILTER (YEAR(?naissance) > 1950)
  OPTIONAL { ?personne wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
}
ORDER BY ?naissance
LIMIT 50
```

Astuce : la ligne `#defaultView:ImageGrid` (ou `Map` avec la coordonnée `P625`, ou `BarChart`) en tête de requête change l'affichage du résultat dans le service de requêtes.

### Requêtes fédérées avec SERVICE

`SERVICE <url>` envoie une partie du motif à un autre point d'accès (endpoint) et joint les résultats localement. Exemple depuis un serveur local (Apache Jena Fuseki) qui enrichit ses données avec Wikidata :

```sparql
PREFIX ex:  <http://example.org/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd:  <http://www.wikidata.org/entity/>

SELECT ?ville ?popWikidata
WHERE {
  ?v ex:label ?ville ; ex:wikidata ?qid .   # lien local vers l'IRI Wikidata
  SERVICE <https://query.wikidata.org/sparql> {
    ?qid wdt:P1082 ?popWikidata .
  }
}
```

Bonnes pratiques de fédération :

- Transmettre au service distant le moins de lignes possible : filtrer localement d'abord, ou injecter les identifiants avec `VALUES`.
- `SERVICE SILENT <url>` évite l'échec complet de la requête si le service distant ne répond pas.
- Le service Wikidata coupe les requêtes au-delà d'environ 60 secondes ; il n'accepte la fédération sortante que vers une liste de points d'accès autorisés.

## Module 7 — SPARQL Update, graphes nommés et performance

SPARQL Update modifie les données ; les graphes nommés les organisent ; quelques règles simples évitent la plupart des requêtes lentes. Ces exemples s'exécutent sur un serveur local (Apache Jena Fuseki ou rdflib), pas sur Wikidata qui est en lecture seule.

### Graphes nommés et jeux de données (datasets)

Un jeu de données RDF (Resource Description Framework) contient un graphe par défaut et des **graphes nommés**, chacun identifié par une IRI (Internationalized Resource Identifier). On s'en sert pour séparer les sources, les versions ou les droits d'accès. On passe alors des triplets aux quadruplets (le format TriG, extension de Turtle, les écrit).

```sparql
# Dans quel graphe se trouve chaque information sur Alice ?
SELECT ?g ?p ?o
WHERE {
  GRAPH ?g { ex:alice ?p ?o }
}
```

- `FROM <iri>` : construit le graphe par défaut de la requête à partir de ce graphe.
- `FROM NAMED <iri>` : rend ce graphe disponible pour les blocs `GRAPH`.
- `GRAPH <iri> { ... }` : restreint un motif à un graphe précis.

### SPARQL Update

```sparql
# Ajouter des triplets fixes
INSERT DATA {
  GRAPH <http://example.org/g/rh> {
    ex:david a foaf:Person ; foaf:name "David" ; foaf:age 41 .
  }
}

# Supprimer des triplets fixes
DELETE DATA { ex:bob foaf:knows ex:chloe . }

# Modifier selon un motif : vieillir tout le monde d'un an
DELETE { ?p foaf:age ?age }
INSERT { ?p foaf:age ?nouvelAge }
WHERE  {
  ?p foaf:age ?age .
  BIND (?age + 1 AS ?nouvelAge)
}
```

| Opération | Effet |
| --- | --- |
| `INSERT DATA` / `DELETE DATA` | ajout ou retrait de triplets sans variables |
| `DELETE ... INSERT ... WHERE` | modification par motif, les deux parties évaluées sur le même `WHERE` |
| `DELETE WHERE { ... }` | raccourci quand le motif à supprimer est le motif cherché |
| `LOAD <url> INTO GRAPH <g>` | chargement d'un fichier RDF distant |
| `CLEAR GRAPH <g>` / `DROP GRAPH <g>` | vider ou supprimer un graphe |
| `COPY`, `MOVE`, `ADD` | opérations entre graphes |

**Piège** : `DELETE` / `INSERT` sur un motif trop large modifie tout le graphe. Toujours tester d'abord le `WHERE` dans un `SELECT`.

### Performance : les règles qui comptent

1. **Ancrer la requête** : commencer par les motifs les plus sélectifs (une constante, une classe rare). Un motif `?s ?p ?o` sans contrainte balaie tout le graphe.
2. **Remplacer un FILTER d'égalité par une constante** : `?p ex:city ex:paris` est indexé, `FILTER (?ville = ex:paris)` est souvent évalué après coup.
3. **Se méfier de `REGEX`** sur de gros volumes : préférer `STRSTARTS` ou l'index plein texte du moteur s'il en a un.
4. **Mettre `OPTIONAL` et les agrégats en dernier**, une fois le jeu de solutions réduit.
5. **Borner les chemins `*` et `+`** par une extrémité fixe.
6. **Toujours un `LIMIT`** pendant la mise au point.
7. **Lire le plan d'exécution** : Apache Jena, GraphDB, Virtuoso ou Blazegraph (moteur de Wikidata) proposent tous un mode « explain ».

### SPARQL depuis Python

```python
# pip install SPARQLWrapper rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql",
                       agent="formation-sparql/1.0 (contact@example.org)")
sparql.setQuery("""
  SELECT ?villeLabel ?pop WHERE {
    ?ville wdt:P31 wd:Q515 ; wdt:P17 wd:Q142 ; wdt:P1082 ?pop .
    SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
  } ORDER BY DESC(?pop) LIMIT 5
""")
sparql.setReturnFormat(JSON)
for r in sparql.query().convert()["results"]["bindings"]:
    print(r["villeLabel"]["value"], r["pop"]["value"])
```

Le paramètre `agent` est important : Wikidata bloque les clients sans en-tête User-Agent explicite. Pour un graphe local, `rdflib.Graph().parse("donnees.ttl")` puis `g.query("...")` suffit.

## Module 8 — Tutoriel rdflib : RDF et SPARQL en Python

rdflib est la bibliothèque Python de référence pour RDF (Resource Description Framework) : elle lit et écrit tous les formats courants, manipule les triplets en Python et exécute SPARQL (SPARQL Protocol and RDF Query Language) 1.1 en mémoire, requêtes comme mises à jour. Ce tutoriel reprend le graphe Alice / Bob / Chloé du module 1 ; compter environ 45 min.

### 1. Installer et charger le graphe

```bash
pip install rdflib pandas
```

Enregistrer le Turtle (Terse RDF Triple Language) du module 1 dans `personnes.ttl`, puis :

```python
from rdflib import Graph

g = Graph()
g.parse("personnes.ttl")          # format déduit de l'extension ; sinon format="turtle"
print(len(g))                      # nombre de triplets : 19
```

`parse` accepte aussi une URL ou une chaîne (`g.parse(data=texte, format="turtle")`), et les formats `xml` (RDF/XML), `nt` (N-Triples), `json-ld` (JSON for Linked Data), `trig`, `n3`.

### 2. Les objets de base

```python
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, FOAF, XSD

EX = Namespace("http://example.org/")
g.bind("ex", EX)                  # préfixe utilisé à la sérialisation et dans les requêtes

alice = EX.alice                   # équivaut à URIRef("http://example.org/alice")
age   = Literal(34)                # typé automatiquement xsd:integer
nom   = Literal("Paris", lang="fr")
anon  = BNode()                    # nœud anonyme (blank node)
```

| Classe rdflib | Terme RDF (Resource Description Framework) | Exemple |
| --- | --- | --- |
| `URIRef` | IRI (Internationalized Resource Identifier) | `URIRef("http://example.org/alice")` |
| `Literal` | littéral, typé ou avec langue | `Literal("34", datatype=XSD.integer)` |
| `BNode` | nœud anonyme | `BNode()` |
| `Namespace` | fabrique d'IRI à partir d'un préfixe | `EX.alice`, `EX["nom-compose"]` |

### 3. Manipuler les triplets sans SPARQL

```python
# Ajouter et retirer
g.add((EX.david, RDF.type, FOAF.Person))
g.add((EX.david, FOAF.name, Literal("David")))
g.remove((EX.bob, FOAF.knows, None))          # None = joker

# Lire
print(g.value(EX.alice, FOAF.name))           # une seule valeur : Alice
for ami in g.objects(EX.alice, FOAF.knows):    # toutes les valeurs
    print(g.value(ami, FOAF.name))
for s, p, o in g.triples((None, FOAF.age, None)):
    print(s, o.toPython())                     # toPython() : Literal -> int, str, date…

# Tester l'existence d'un triplet
print((EX.alice, FOAF.knows, EX.bob) in g)     # True
```

`subjects(p, o)`, `predicates(s, o)` et `subject_objects(p)` complètent la panoplie. Ces méthodes suffisent pour les traitements simples ; SPARQL devient préférable dès qu'il y a des jointures ou des agrégats.

### 4. Exécuter une requête SELECT

```python
requete = """
PREFIX ex:   <http://example.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?nom ?age
WHERE {
  ?p foaf:name ?nom .
  OPTIONAL { ?p foaf:age ?age }
}
ORDER BY ?nom
"""
for ligne in g.query(requete):
    print(ligne.nom, ligne.age)                # accès par nom de variable (None si non liée)
```

Vers pandas, pour enchaîner sur de l'analyse :

```python
import pandas as pd

res = g.query(requete)
df = pd.DataFrame(
    [{k: (v.toPython() if v is not None else None) for k, v in r.asdict().items()} for r in res],
    columns=[str(v) for v in res.vars],
)
```

`res.serialize(format="json")` ou `format="csv"` produit directement les formats de résultats standard SPARQL.

### 5. Requêtes préparées et paramètres

Ne jamais construire une requête par concaténation de chaînes avec des valeurs venant d'un utilisateur : c'est l'équivalent de l'injection SQL (Structured Query Language). On passe les valeurs par `initBindings` :

```python
from rdflib.plugins.sparql import prepareQuery

q = prepareQuery(
    "SELECT ?nom WHERE { ?p foaf:name ?nom ; ex:city ?ville . }",
    initNs={"foaf": FOAF, "ex": EX},
)
for ligne in g.query(q, initBindings={"ville": EX.paris}):
    print(ligne.nom)                           # Alice, Chloé
```

La requête est analysée une seule fois, ce qui accélère aussi les exécutions répétées.

### 6. ASK, CONSTRUCT et SPARQL Update

```python
# ASK renvoie un booléen
print(bool(g.query("ASK { ?p <http://xmlns.com/foaf/0.1/age> 28 }")))

# CONSTRUCT renvoie un nouveau Graph
nouveau = g.query("""
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  CONSTRUCT { ?b foaf:knows ?a } WHERE { ?a foaf:knows ?b }
""").graph

# SPARQL Update modifie g en place
g.update("""
  PREFIX ex:   <http://example.org/>
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  INSERT DATA { ex:chloe foaf:age 30 . }
""")
```

### 7. Sérialiser et convertir

```python
print(g.serialize(format="turtle"))          # renvoie une chaîne
g.serialize("personnes.jsonld", format="json-ld")
g.serialize("personnes.nt", format="nt")     # N-Triples : une ligne par triplet
```

Parse puis serialize : rdflib est aussi le convertisseur de formats le plus simple à disposition.

### 8. Graphes nommés avec Dataset

```python
from rdflib import Dataset

ds = Dataset()
rh = ds.graph(URIRef("http://example.org/g/rh"))
rh.add((EX.alice, EX.salaire, Literal(52000)))

for ligne in ds.query("SELECT ?g ?s WHERE { GRAPH ?g { ?s ?p ?o } }"):
    print(ligne.g, ligne.s)

ds.serialize("donnees.trig", format="trig")   # TriG : Turtle avec graphes nommés
```

### 9. Inférence RDFS (RDF Schema) avec owlrl

rdflib n'infère rien par défaut. Le paquet compagnon owlrl matérialise les déductions dans le graphe :

```python
# pip install owlrl
from owlrl import DeductiveClosure, RDFS_Semantics

g.add((FOAF.Person, RDFS.subClassOf, EX.Agent))
DeductiveClosure(RDFS_Semantics).expand(g)
print((EX.alice, RDF.type, EX.Agent) in g)    # True : déduit de la sous-classe
```

`OWLRL_Semantics` applique le profil OWL 2 RL (Web Ontology Language, profil Rule Language). Pour valider des données contre des formes SHACL (Shapes Constraint Language), le paquet compagnon est pySHACL.

### 10. Limites et pièges

- **Volume** : le stockage par défaut est en mémoire et le moteur SPARQL est écrit en Python pur. Au-delà de quelques millions de triplets, brancher le stockage Oxigraph (`pip install oxrdflib`, puis `Graph(store="Oxigraph")`) ou passer à un vrai serveur (Apache Jena Fuseki, GraphDB).
- **Littéraux** : `Literal("34")` (chaîne) et `Literal(34)` (entier) sont deux valeurs différentes, et `Literal("Paris")` ne correspond pas à `Literal("Paris", lang="fr")`.
- **Espaces de noms** : `Namespace("http://example.org")` sans barre finale produit `http://example.orgalice`.
- **Points d'accès distants** : rdflib peut s'y connecter, mais pour Wikidata `SPARQLWrapper` (module 7) reste plus simple, notamment pour l'en-tête User-Agent obligatoire.

**Exercice** : charger `personnes.ttl`, ajouter avec l'API Python une personne ex:emma âgée de 25 ans, habitant Lyon et connaissant Bob, puis réexécuter en Python la requête de l'exercice 3 et afficher le résultat sous forme de DataFrame pandas. Résultat attendu : Paris 2, Lyon 2.

## Exercices corrigés

Les exercices 1 à 6 portent sur le graphe du module 1, le 7 sur Wikidata, le 8 sur SPARQL Update. Préfixes `ex:` et `foaf:` sous-entendus. Essayer chaque exercice avant de lire la correction.

### Énoncés

1. Donner le nom et l'âge des personnes habitant Paris. *(module 2)*
2. Lister les personnes dont l'âge n'est pas renseigné. *(module 3)*
3. Compter le nombre de personnes par ville, de la plus représentée à la moins représentée. *(module 4)*
4. Pour chaque personne, compter combien de personnes la connaissent, avec un chemin inverse. *(modules 4 et 5)*
5. Vérifier si une personne habitant Lyon connaît une personne habitant Paris. *(module 5)*
6. Construire un graphe reliant par `ex:memeVille` les personnes qui habitent la même ville, sans relier une personne à elle-même. *(module 5)*
7. Sur Wikidata : lister les capitales des pays membres de l'Union européenne avec leur population, de la plus peuplée à la moins peuplée. *(module 6)*
8. Renseigner l'âge de Chloé (30 ans), puis renommer « Bob » en « Robert ». *(module 7)*

### Corrections

**Exercice 1** — résultat attendu : Alice, 34.

```sparql
SELECT ?nom ?age
WHERE {
  ?p ex:city ex:paris ; foaf:name ?nom ; foaf:age ?age .
}
```

Sans `OPTIONAL`, Chloé (sans âge) est exclue ; c'est voulu ici.

**Exercice 2** — résultat attendu : Chloé.

```sparql
SELECT ?nom
WHERE {
  ?p a foaf:Person ; foaf:name ?nom .
  FILTER NOT EXISTS { ?p foaf:age ?age }
}
```

Variante équivalente : `OPTIONAL { ?p foaf:age ?age } FILTER (!BOUND(?age))`.

**Exercice 3** — résultat attendu : Paris 2, Lyon 1.

```sparql
SELECT ?ville (COUNT(?p) AS ?nb)
WHERE { ?p ex:city/ex:label ?ville . }
GROUP BY ?ville
ORDER BY DESC(?nb)
```

**Exercice 4** — résultat attendu : Chloé 2, Bob 1, Alice 0.

```sparql
SELECT ?nom (COUNT(?admirateur) AS ?nb)
WHERE {
  ?p a foaf:Person ; foaf:name ?nom .
  OPTIONAL { ?p ^foaf:knows ?admirateur }
}
GROUP BY ?nom
ORDER BY DESC(?nb)
```

`COUNT(?admirateur)` ne compte que les valeurs liées, d'où le 0 pour Alice grâce à l'`OPTIONAL`. `COUNT(*)` aurait donné 1.

**Exercice 5** — résultat attendu : `true` (Bob connaît Chloé).

```sparql
ASK {
  ?a ex:city ex:lyon ; foaf:knows ?b .
  ?b ex:city ex:paris .
}
```

**Exercice 6** — résultat attendu : `ex:alice ex:memeVille ex:chloe` et `ex:chloe ex:memeVille ex:alice`.

```sparql
CONSTRUCT { ?a ex:memeVille ?b }
WHERE {
  ?a ex:city ?v .
  ?b ex:city ?v .
  FILTER (?a != ?b)
}
```

**Exercice 7** — à exécuter sur le [Wikidata Query Service](https://query.wikidata.org/).

```sparql
SELECT ?paysLabel ?capitaleLabel ?pop
WHERE {
  ?pays wdt:P463 wd:Q458 ;      # membre de : Union européenne
        wdt:P36  ?capitale .    # capitale
  ?capitale wdt:P1082 ?pop .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
}
ORDER BY DESC(?pop)
```

Pour aller plus loin : certains pays ont plusieurs capitales ou plusieurs valeurs de population, ce qui crée des doublons. Les résoudre avec `GROUP BY ?paysLabel ?capitaleLabel` et `(MAX(?pop) AS ?popMax)`.

**Exercice 8**

```sparql
INSERT DATA { ex:chloe foaf:age 30 . } ;

DELETE { ?p foaf:name "Bob" }
INSERT { ?p foaf:name "Robert" }
WHERE  { ?p foaf:name "Bob" }
```

Le `;` enchaîne plusieurs opérations dans une même requête de mise à jour.

## Ressources

- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) — la spécification du W3C (World Wide Web Consortium), très lisible avec ses exemples.
- [SPARQL 1.1 Update](https://www.w3.org/TR/sparql11-update/) — la spécification des opérations de modification.
- [Wikidata Query Service](https://query.wikidata.org/) — bouton « Exemples » : plusieurs centaines de requêtes commentées.
- [Tutoriel SPARQL de Wikidata](https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial/fr) — complément idéal au module 6.
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) — serveur local pour s'entraîner, y compris à SPARQL Update.
- [rdflib](https://rdflib.readthedocs.io/) — RDF (Resource Description Framework) et SPARQL en Python.
- *Learning SPARQL* (Bob DuCharme, O'Reilly) — le livre de référence pour approfondir.

## Annexe — Connecter un LLM à un serveur MCP depuis AWS AgentCore

Un agent hébergé sur Amazon Bedrock AgentCore se connecte à un serveur MCP (Model Context Protocol) selon trois schémas. Dans les trois cas, le LLM (Large Language Model) finit par appeler des outils via MCP ; ce qui change, c'est **qui ouvre la connexion au serveur et qui détient ses identifiants**.

### Option 1 — L'agent est le client MCP

Le code de l'agent, exécuté dans AgentCore Runtime, se connecte lui-même au serveur. Le framework (Strands Agents, LangGraph, LlamaIndex…) ouvre la session MCP, liste les outils, les convertit en définitions d'outils pour le modèle et relaie chaque appel.

```
                  ┌──────────────► Serveur MCP A   (l'agent détient les identifiants de A)
Agent (Runtime) ──┼──────────────► Serveur MCP B   (l'agent détient les identifiants de B)
                  └──────────────► Serveur MCP C   (l'agent détient les identifiants de C)
```

- **Quand l'utiliser** : un ou deux serveurs, un prototype, un serveur utilisé par ce seul agent.
- **Authentification** : le code de l'agent gère les identifiants, en les demandant à AgentCore Identity plutôt qu'en les codant en dur (voir plus bas).
- **Réseau** : le Runtime doit pouvoir joindre le serveur. Un serveur public demande un accès Internet sortant ; en mode VPC (Virtual Private Cloud), cela passe par une passerelle NAT (Network Address Translation).
- **Limite** : chaque agent répète le même câblage, sans catalogue central, politique d'accès ni piste d'audit pour les outils.

### Option 2 — AgentCore Gateway est le client MCP

On enregistre le serveur MCP comme **cible** (target) d'AgentCore Gateway. L'agent ne connaît qu'une URL, celle du Gateway, qui agrège et route vers toutes ses cibles.

```
                                 ┌──► Serveur MCP A
Agent (Runtime) ──► Gateway ─────┼──► Serveur MCP B
  (une URL,          (détient tous └──► Lambda / API REST
   un identifiant)    les identifiants)
```

- **Ce que fait le Gateway** : à la création de la cible, il effectue la négociation MCP et indexe les outils du serveur (ainsi que ses prompts et ressources, s'il en annonce) dans un catalogue unifié. Une synchronisation explicite le met à jour quand les outils du serveur changent ; un mode « dynamique » transmet plutôt la découverte au serveur à chaque appel.
- **Deux authentifications indépendantes** :
  - *entrante* (agent → Gateway) : un jeton OAuth (Open Authorization) de votre fournisseur d'identité, ou IAM (Identity and Access Management) ;
  - *sortante* (Gateway → serveur MCP), par cible : aucune autorisation (possible mais déconseillé), OAuth (client credentials, authorization code ou échange de jeton au nom de l'utilisateur), clé d'API (Application Programming Interface), ou signature IAM SigV4. SigV4 ne fonctionne que si le serveur est derrière un service qui la vérifie nativement : AgentCore Runtime, Amazon API Gateway ou les URL de fonction Lambda.
- **En plus** : le Gateway expose aussi des sources non MCP comme outils MCP, par exemple des fonctions Lambda ou des API REST (Representational State Transfer) décrites en OpenAPI.
- **Quand l'utiliser** : plusieurs serveurs ou sources d'outils, plusieurs agents qui partagent des outils, besoin de contrôle d'accès, de gestion des identifiants et d'observabilité centralisés. C'est le schéma standard en production.

### Option 3 — Héberger soi-même le serveur MCP dans AgentCore Runtime

Si le serveur MCP est votre propre code, ou un serveur open source à faire tourner dans votre compte, AgentCore Runtime peut l'héberger en tant que serveur MCP plutôt qu'en tant qu'agent. On le consomme ensuite via l'option 1 ou, plus souvent, on l'enregistre comme cible du Gateway avec une authentification IAM SigV4, combinaison prise en charge nativement. Tout reste dans votre compte AWS (Amazon Web Services).

### Option 1 ou option 2 : ce que cela change en pratique

L'analogie : l'option 1, c'est un bureau où chaque employé a une ligne directe vers chaque fournisseur, avec les numéros de compte sur des post-it. L'option 2, c'est un standard téléphonique : un seul numéro à composer, seul le standard connaît les numéros de compte, il journalise les appels et peut refuser ceux qui ne sont pas autorisés.

| Situation | Option 1 (directe) | Option 2 (Gateway) |
| --- | --- | --- |
| Ajouter un serveur d'outils | Modifier et redéployer l'agent | Ajouter une cible au Gateway ; l'agent ne change pas |
| L'identifiant d'un serveur change | Mettre à jour chaque agent qui l'utilise | Le mettre à jour une fois, dans le Gateway |
| Retirer à un agent l'accès à un outil | Modifier le code de cet agent | Changer une permission dans le Gateway |
| Cinq agents partagent les mêmes outils | Cinq copies du même câblage | Un Gateway, cinq clients |
| Auditer qui a appelé quel outil, et quand | Instrumenter chaque agent | Un seul endroit |
| Exposer une Lambda ou une API REST comme outil | Écrire soi-même un adaptateur MCP | Le Gateway fait la conversion |
| Effort pour un premier prototype | Minimal | Un composant de plus à configurer |

Passer de l'une à l'autre coûte peu : dans les deux cas, l'agent parle MCP. Passer de l'option 1 à l'option 2 revient surtout à remplacer la liste des URL de serveurs de l'agent par l'URL unique du Gateway.

### Les identifiants : le rôle d'AgentCore Identity

La plupart des serveurs MCP exigent une clé d'API ou un jeton OAuth, présenté dans l'en-tête HTTP (HyperText Transfer Protocol) `Authorization` à l'ouverture de la session. Le coder en dur l'expose dans Git, les images et les journaux ; une variable d'environnement le copie dans chaque déploiement, et un jeton OAuth expire de toute façon au bout de quelques minutes ou heures.

AgentCore Identity est un **coffre à identifiants doublé d'un courtier de jetons** :

1. **Configuration, une fois** : on crée un *fournisseur d'identifiants* (credential provider), soit une clé d'API (stockée dans AWS Secrets Manager), soit un client OAuth (identifiant, secret, URL du serveur d'autorisation). On lui donne un nom, par exemple `crm-mcp`.
2. **À l'exécution** : l'agent prouve son identité grâce au rôle IAM sous lequel il tourne dans Runtime, sans aucun secret ; il demande l'identifiant de `crm-mcp` ; Identity vérifie que cet agent y a droit et renvoie la clé ou un jeton valide, en gérant l'expiration et le renouvellement OAuth ; l'agent place l'identifiant dans l'en-tête et ouvre la session MCP.

Le code ne contient que le *nom* du fournisseur, jamais le secret. Deux variantes OAuth existent : l'agent agit **en son propre nom** (flux client credentials, entièrement automatique), ou **au nom d'un utilisateur** (OAuth à trois parties, flux authorization code) : l'utilisateur donne son consentement une première fois, Identity conserve son jeton, et l'agent n'accède qu'à ce que cet utilisateur peut voir.

Ce qu'on y gagne : aucun secret dans le code ni la configuration, une rotation en un seul endroit, un contrôle d'accès par agent via IAM, un cycle de vie des jetons géré et une journalisation de chaque demande. Dans l'option 2, c'est le Gateway qui effectue ces mêmes étapes à la place de l'agent : même coffre, même mécanisme, seul l'appelant change.

### Code déterministe ou « hook » ?

La connexion n'est jamais décidée par le LLM : c'est du **code Python déterministe** qui s'exécute avant que le modèle n'intervienne. Le modèle ne voit jamais les identifiants.

1. **Au démarrage ou à la réception d'une requête** : votre code demande l'identifiant à Identity, crée le client MCP avec l'URL et l'en-tête, ouvre la session, appelle `tools/list` et confie la liste au framework.
2. **Pendant la conversation** : le modèle choisit seulement *quel* outil appeler et *avec quels arguments* ; le framework envoie l'appel sur la session déjà ouverte et authentifiée.
3. **À la fin de la requête** : la session est fermée ; la requête suivante obtient un jeton neuf.

Le mot « hook » recouvre deux choses, toutes deux déterministes :

- **Les décorateurs du SDK (Software Development Kit) AgentCore** : placés sur une fonction, ils indiquent qu'elle requiert un jeton OAuth ou une clé d'API d'un fournisseur donné, et injectent l'identifiant à l'exécution. Ils gèrent aussi la redirection vers la page de consentement dans le cas OAuth à trois parties.
- **Les hooks de cycle de vie des frameworks** (Strands, par exemple) : du code exécuté à des points fixes (avant le démarrage, avant ou après chaque appel d'outil) pour journaliser, bloquer certains outils ou renouveler un jeton sur une session longue. Inutiles pour la simple connexion.

Dans l'option 2, il y a encore moins de code : la cible et son fournisseur d'identifiants se configurent une fois (console, CLI (Command Line Interface) ou infrastructure as code), et le Gateway fait l'appel à Identity et la connexion lui-même.

### Comment choisir

| Situation | Option |
| --- | --- |
| Prototype rapide, un serveur externe | 1 — connexion directe |
| Plusieurs serveurs ou agents, production, gouvernance | 2 — via le Gateway |
| Le serveur est votre code, ou les données doivent rester dans votre compte | 3, puis consommé via 2 |

Le parcours habituel : commencer par l'option 1 pour valider l'agent, puis passer les connexions d'outils derrière un Gateway avant la production.

### Points à vérifier pour toute connexion

1. **Transport** : AgentCore travaille avec des serveurs MCP distants en HTTP (streamable HTTP). Un serveur local en stdio (standard input/output) doit d'abord être hébergé (option 3).
2. **Version du protocole** : le Gateway prend en charge une liste fixe de versions MCP (de 2025-03-26 à 2026-07-28), choisie à la création du gateway.
3. **Capacités** : le serveur doit exposer des *outils* ; prompts et ressources sont facultatifs.
4. **Identifiants** : toujours dans AgentCore Identity, jamais dans le code.
5. **Évolutions des outils** : en mode par défaut du Gateway, resynchroniser la cible après chaque changement, sinon le catalogue devient obsolète.
6. **Observabilité** : activer AgentCore Observability pour tracer quel outil a été appelé, avec quels arguments et en combien de temps.

Sources de l'annexe : [AgentCore Gateway — MCP server targets](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html), [AgentCore Gateway — core concepts](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.md), [Unite MCP servers through AgentCore Gateway (blog AWS)](https://aws.amazon.com/blogs/machine-learning/transform-your-mcp-architecture-unite-mcp-servers-through-agentcore-gateway).

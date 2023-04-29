# Notes sur le stage

## Call du 2022/09/09

### Discussion technique

"stack technique". → on part sur LLVM comme couche d'abstraction.
Attention à la complexité mais en échange on récupère pas mal de bénéfices, dont le multi-targets (mais on se focalisera sur WASM, même si une démo du fait qu'on peut viser facilement d'autres architectures serait utile).

Besoin d'un runtime: strings, bigints, dictionnaires, listes, tuples... Il en existe pour d'autres langages → à adapter.

Environnement d'exécution: Wasmer, Nodejs, browser, autres (à définir).

Version minimale de Python: 3.10 (de façon à pouvoir utiliser le pattern matching)

### Plan d'action
- Commencer par le minimum (programmes simples: "hello world", "fibonacci", etc.)
- Viser ensuite des programmes simples: jeux WASM-4 (en réécrire un en Python), des fonctions pour un environnement web simple (Cloudflare? → https://blog.cloudflare.com/webassembly-on-cloudflare-workers/), puis réfléchir à d'autres cas d'usage pertinents.
- Refactorer en utilisant une bibliothèque de récriture de termes (à reprendre ou à développer), si ça devient pertinent à un moment.
- Se préoccuper aussi de l'interface avec le système pour faire des programmes standalone (WASI)

### Benchmarks (ajouté après le call)
Regarder https://pyperformance.readthedocs.io/
Attention: rien que d'arriver à faire tourner les programmes en questions est un challenge énorme.
Les programmes en question sont ici: https://github.com/python/pyperformance/tree/main/pyperformance/data-files/benchmarks


### Liens intéressants (déjà envoyés)
- https://wasmweekly.news/
- https://www.taichi-lang.org/
- https://wasm4.org/blog/jam-2-results/
- https://github.com/py2many/py2many
- https://github.com/titzer/virgil
- https://github.com/deepmind/s6
- https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/README.html
- https://evacchi.github.io/llvm/wasm/wasi/2022/04/14/compiling-llvm-ir-into-wasm.html


### TODO
- [x] Create repo + donner accès.



### Semaine du 19/09/2022

#### Etape 1: Recherches Python -> LLVM

- Qu'est-ce qui existe déjà ?
    - Numba utilise LLVM via llvmlite
    - llvmpy -> wrapper au dessus de la bibliothèque C++ pour python. Pas à
        jour et pas maintenu
    - py2llvm (sur google code)-> projet abandonné en 2011, bindings LLVM pour python
    - pyllvm -> compilo static python vers LLVM, talk intéressant sur youtube, date de 2015 utilise py2llvm (google code version)
    - py2llvm (sur github) -> projet plus récent (2020), ne supporte qu'un petit
        subset de Python. Utilise llvmlite

- Bibliothèque pré-existante ou from scratch ?
    Si on prend une bibliothèque pré-existante, llvmlite semble être le choix
    évident. Par contre llvmlite est fait pour fonctionner avec llvm 11.

Choix: faire un prototype avec llvmlite et voir après

Questions auxquelles il faudra répondre:
    - Comment gérer l'Objet ? Piste: regarder comment certains types comme
      listes, tuple, etc... sont handle par numba et les autres projets
      au dessus
    - Problème qui vient découle de celui d'au-dessus: quid de l'overloading ?



#### Call du 22/09/2022

Question de la runtime abordée:
    Où trouver la runtime ? La refaire ne semble pas possible
    Mais à voir au niveau de l'implem de CPython (c'est du C donc compilable
    avec LLVM)
    Comment fait Numba ?

Pour le moment, on peut mettre l'inférence de type de côté et partir sur un truc
annoté, plus simple pour débuter.

Utiliser Black pour le formattage du code


#### Semaine du 17/09/2022

Notes sur LLVM:
    les string "hello" et "hello world" n'ont pas le même type. La première est
    [5 x i8] et la seconde est [11 x i8]

#### Call du 21/10/2022

Besoin de patch pour compiler en WASM sur NixOS
Penser à faire des tests !!

Question du `main`:
    Est-ce qu'on fait un seul point d'entrée ?
    Est-ce qu'on considère que le main est pas indispensable ? Auquel cas on
    partirai plutôt sur une idée de bibliothèque

#### Semaine du 24/10/2022

Pour avancer LLVM, il faut du typage.
Donc un retour sur l'inférence de type paraît obligatoire.

Après quelque cafouillage, une solution est trouvée:
    Il faut faire une première passe qui s'assure que tout existe dans le scope
    dans lequel il est utilisé.

Comportement un peu tricky en Python:
```py
    x = 1
    def f():
        x += 1
```
ne marche pas, alors que
```py
    x = 1
    def f():
        print(x)
```
fonctionne
Différence dans l'ast:
    le context Name() généré est 'store' and le premier cas, et 'load' dans le
    2e.
    Est-ce qu'il faut  aller chercher un Name dans le scope actuel et les parents en
    cas de load, et seulement dans le actuel sinon ?
À savoir qu'après le 'binding', on peut imaginer une phase de rename, qui
permettrai d'éliminer un certain nombre de corner cases

Question comme ça:
```py
a = 1
b = a
c = a + 1
```
Le Name(id='a') généré est-il 2 fois le même ? Où est-ce 2 Name() avec un
contenu différent ?
Réponse: C'en est 2 différents

La classe ast.NodeTransformer permet de changer des noeuds l'ast (cf doc).
Est-elle utile pour le renamer ? Non. Car son but semble de remplacer les noeuds
existants par des nouveaux. Très utile pour désucrer des trucs par contre, tels
que `ast.AugAssign` ou autre.
Dans le cas du renamer, comme on veut juste update un champ existant, le
visiteur suffit.


#### Semaine du 14/11

L'écriture de tests a commencé.
Les tests sont actuellements générés dans tests/generate\_tests.py et lancés par
tests/run\_tests.py.

Tester la véracité du binder (s'assurer que les bons noeuds ont bien les bonnes
adresses de définition) est complexe.
Une solution pourrait-être d'utiliser d'avoir un pretty-printer, de print avec
la definition, de modifier le programme et de le re-parser.
exemple:
le programme
```py
a : int = 2
b : int = a
```

sera pretty-print de la façon suivante (après binding)
```py
a__0xcafe : int = 2
b__0xbabe : int = a__0xcafe
```

Si la definition n'est pas la bonne, alors le `a__0xcafe` dans l'assignation de
b ne sera pas bon, et on échouera au binding en essayant de re-parser l'output
du pretty printer.
Cela revient à faire quelque chose du genre:
`compylo -BP toto.py > tata.py` && `compylo -B tata.py` sans avoir d'erreur

#### Semaine du 20/11

Le type-checker avance.
Question: comment gérer les constructions suivantes ?
```
a : str = 5 * "a"
```

Envisager une passe de désucrage de ce genre de constructions ? (en utilisant
ast.NodeTransformer pour le coup)
Si oui, il faudrait le faire après l'inférence de type, mais avant le type
checking. Ça permettrait de simplifier les problèmes de compatibilité entre les
types.
eg:
    Sans désucrage, `5 + "A"` est invalide là où `5 * "A"` est valide.
    Donc le checker de compatibilité (compatible_with dans src/types.py) aurait
    un certain besoin de contexte.
    Avec désucrage, on peut remplacer `5 * "A"` par `"AAAAA"` et supprimer le
    BinOp

#### Semaine du 5/12

Est-ce que c'est vraiment judicieux de faire 2 visiteurs séparés pour les types
?
typeInference et typeCheck peuvent être facto en un seul visiteur. Par contre
c'est moins verbeux et + difficile à comprendre
TODO:
    - Ajouter les binOp dans le translator
    - Ajouter les unaryOp
    - Créer un Docker de développement avec le wasm, nix est trop cancer à ce
      niveau là
    - Trouver un truc pour la runtime

#### Semaine du 12/12

Création du Docker pour utiliser WASI.
Problème: wasi ne supporte que les bout de code avec un main

Nouveaux problèmes:
    - l'IR LLVM ne supporte pas les fonctions nested -> nécessité d'implémenter du
        lambda lifting
    - Pour le moment, le LLVM généré à un pb: si le programme commence par une
      fonction, il ne ressort pas de la fonction.
      Si le programme ne commence pas par une fonction, il n'y a pas de point
      d'entrée...

Faire une passe de désucrage paraît pas mal.
Par exemple transformer les -5 en 0-5, les 5 * "a" en "aaaaa".
Le NodeTransformer peut faire l'affaire pour ça.

Comment handle les comparaisons "complexes" autorisées en Python ?
Comme `a > b > 0`
Faut-il les désucrer aussi ?
Réponse: oui

Et pour les assignations multiples ? `a = b = 3`
Oui aussi

Après un test à  main, un fibo marche

#### Semaine du 20/12

##### Call du 22/12

Pas le temps de finir
Objectif: atteindre un truc utilisable au moins dans certains cas.

Ajouter les boucles:
    - Gérer les AugAssign (désucrés)
    - Ajouter les booléens

Question du main:
    Le scope global est le main.
    Ça implique de calculer les escape et d'implem le lambda lifting

Voir pour les listes

#### Semaine du 23/01

Les boucles While basiques telles que
```
a = 0
while a < 5:
    a += 1
```
fonctionnent !


##### Désucrage
Une partie basique est faite, le reste est à faire.
Notamment ne pas supporter que les Name.
Un soucis sera les constructions du style:
```
a = "toto"
b = a[0] * 5
```
Qui devrait être désucrer, mais `a[0]` est un Subscript, il faudrait donc un
moyen d'en récupérer la valeur. Pour le moment Subscript n'est géré à aucun
endroit dans le projet.

De la même manière, on aura des problèmes avec
```
def f() -> str:
    return "a"
a = f() * 2
```
Qu'on aimerait désucrer aussi. Mais là ça demande globalement de run la fonction
compile-time, c'est pas possible...

Une solution serait de typer fortement le langage, et de tout bonnement
interdire ce genre de constructions, car trop complexe à gérer AOT.


#### Boucles For

En C, en C++, etc. Une boucle For est trivialement désucrable en While.
Néanmoins en Python c'est plus compliqué puisque la boucle For itère plus ou
moins toujours sur une structure array-like.
Le désucrage paraît donc compliqué, il faut probablementn gérer les 2 en même
différemment.
Les string étant des `ArrayType` en LLVM, quelque chose du type
```
for c in "Hello World!":
    ...
```
ne devrait pas poser trop de soucis.
Il faudra néanmoins penser à la suite avec les itérables. (Toujours pas sûr de
comment représenter les listes, voir ArrayType et VectorType en LLVM)


##### Scope global & main

On peut utiliser `self._builder.block` dans Translator pour savoir si l'on est
actuellement dans un Basic Block (BB).
Si ce n'est pas le cas, alors jump dans le BB main.
Il faut modifier `__init__` pour créer la fonction, save son BB d'entrée et on
peut imaginer une fonction auxiliaire qui jump à la fin du BB et ajoute ce qu'il
y a à ajouter si `self._builder.block` est None.

DISCLAIMER: nécessite de calculer les variables en échappement et de faire du
lambda lifting.
L'IR LLVM ne supporte pas les fonctions imbriquées. En réalité quand on
utilise une fonction définie dans le scope main dans une fonction, elle est
échapée par l'interpréteur. Comme LLVM ne supporte pas ça, il faut faire du
lambda lifting. Càd qu'on va calculer dans la fonction quelles sont les
variables en échappement, et injecter des arguments immuables à la fonction: les
variables échapées utilisées dedans.

#### Call du 25/01

https://llvmlite.readthedocs.io/en/latest/user-guide/binding/index.html
LLVM ir binding -> à voir si ça peut resortir un binaire

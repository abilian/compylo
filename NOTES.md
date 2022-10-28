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

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

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


### TODO
- [x] Create repo + donner accès.



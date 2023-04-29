# Compylo

# Utilisation

**Commande de base:** `python -m compylo <FILE>` affiche l'IR LLVM correspondant à FILE sur stdout. Pour le moment il faut donc la rediriger dans un fichier et le compiler avec `clang`. À terme ça devrait être possible de générer directement un binaire, que ce soit en passant par clang ou par des bibliothèques pour générer des ELF (ça doit bien exister).

## Passes de compilation

Le Visiteur est totalement adapté, et est donc le pattern utilisé partout.

Pour le moment il y a 6 visiteurs, dont 1 qui n’est pas dans la pipeline de compilation de base. Chaque visiteur à une fonction dédiée:

- Binder (binder.py) → ajoute des attributs `definition` dans les noeuds de l'AST dont on aura besoin de la définition plus tard (ex: les variables, les fonctions, les appels de fonctions...)
- Renamer (renamer.py) → rename les symboles. On a envie d’éliminer rapidement les noms de variable dupliqués, les noms de fonctions et de variables similaires, etc. Donc on renome ces symboles en ajoutant `__X` où X est un compteur statique.
- TypeInference (typeInference.py) → ajoute l’attribut `typ` aux noeuds de l'AST.
- TypeChecker (typeChecker.py) → vérifie que les types utilisés sont cohérents (qu’on essaye pas d’appeler une fonction qui prend un int avec une string pas exemple). Throw un `IncompatibleTypeError` en cas d'erreur.
- Desugar (desugar.py) → désucre certaines constructions autorisées en python mais complexes à traduire, comme `a < b < c`, `3 * "A"`, etc. Après le desugar, une passe de binding est de typing est refaite, car la structure de l'arbre est modifiée.
- Translator (translator.py) → s’occupe de générer l’IR LLVM, et l’affiche sur l’entrée standard à la fin de l’exécution.

# Design

## Général

- 1 visiteur par tâche. Un système de dépendances basique est implem dans `__main__.py`, c'est plus quelque chose qui a été fait rapidement pour pouvoir tester qu'un design définitif. Le design pattern *Command* serait plus adapté.
- La scopedMap contient les locales définies dans chaque scope, elle est notamment utilisée et remplie par le binder. Ces locales sont représentées par la classe Symbol. Cette classe n’a pas de réel intérêt actuellement et devrait devenir un *********Flyweight*********. Revoir la façon dont elle fonctionne peut aussi être pas mal.

## Améliorations

- Pour gérer les listes & dictionnaires, la runtime va vite devenir obligatoire, ne serait-ce que pour gérer les `.append` et autre. On peut aller voir du côté de Numba comment c'est géré
- Le système d’injecter des attributs aux noeuds au fur et à mesure et fonctionnel, mais bancal et fait que le programme pourra jamais être bootstrappé car l’ajout dynamique d’attribut à une instance est pas vraiment possible en compilation statique. Il faudrait faire des classes qui héritent des classes de l’ast de Python avec des infos en plus.
- TypeInference et TypeChecker peuvent (et devraient) être fusionné en 1 seul visiteur, pour l’instant il y en a 2 pour des raisons de facilité de développement et de debug.
- Le lambda lifting va vite devenir obligatoire aussi
- Il faut faire un design de désucrage de la construction objet. Les objets c’est cool mais les histoires d’héritage, de méthode, de dispatch & co doivent devenir des constructions plus bas niveau (genre C-struct) pour être traduite facilement. Il a beaucoup de façon de faire, encore une fois ça peut être une bonnée idée de voir comment fait Numba, bien que comme c’est du JIT, ils font sûrement des trucs qu’on peut pas se permettre en AOT (Ahead of Time).
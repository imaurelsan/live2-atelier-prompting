# Live 2 — Atelier prompting · 18/09/2026 · 14h–15h

Trois dépôts, trois niveaux. Chacun a son `ENONCE.md` (ou `FEATURE.md`)
autonome, distribuable tel quel.

| Dossier | Niveau | Exercice | État initial |
|---|---|---|---|
| `demo-bug/` | N1 | Déboguer une facturation fausse | 7 tests rouges sur 17 |
| `demo-legacy/` | N2 | Refactorer 150 lignes sales | 5 tests verts, à garder verts |
| `demo-starter/` | N3 | Ajouter les échéances à une app TODO | 28 cas verts, à garder verts |

Chaque participant choisit **un** niveau et y consacre 30 minutes.
Ce n'est pas assez pour finir : l'objectif est de produire une
observation à rapporter, pas un exercice terminé.

## Démarrer

```bash
pip install pytest

cd demo-bug      && pytest -q    # 7 failed, 10 passed
cd demo-legacy   && pytest -q    # 5 passed
cd demo-starter  && pytest -q    # 28 passed
```

Aucune dépendance au-delà de pytest. Python 3.10+.

## Avant tout : les règles du jeu

**Lis `REGLES-DU-JEU.md`.** Les énoncés sont piégés, volontairement, et c'est
annoncé. Chacun contient trois affirmations fausses et une instruction absurde.

Si tu colles un énoncé entier dans une IA, elle les appliquera toutes. C'est
l'injection de prompt de la capsule 7, en conditions réelles.

## La règle commune

1. `git init` et premier commit avant de lancer quoi que ce soit
2. Tu lis l'énoncé toi-même avant toute IA
3. Tu lis le diff avant d'accepter
4. Un commit par étape qui marche
5. `python verifier.py` à la fin, dans chaque dépôt

## Ce qui change par rapport au Live 1

Le Live 1 portait sur la génération : partir de zéro. Celui-ci porte sur le
cas réel — **du code existe déjà**, et il faut le comprendre avant de le
toucher.

Les trois exercices ont le même fil rouge :

> Le contexte que tu donnes pèse plus lourd que la façon dont tu formules.

- **N1** le démontre par les trois prompts successifs
- **N2** le démontre par le périmètre : borner ou subir un diff illisible
- **N3** le démontre par la spec : ce que le client n'a pas dit, tu dois l'écrire

## Ce qu'on attend en restitution

- Quels pièges de l'énoncé as-tu repérés, et comment ?
- Ton code de contrôle
- Quel prompt t'a débloqué ?
- Combien de fichiers ton diff touchait-il ?
- Où l'IA s'est-elle arrêtée en croyant avoir fini ?
- Qu'as-tu reformulé, et qu'est-ce que ça a changé ?

## Note

Données et code entièrement fictifs, écrits pour l'exercice.

`CORRECTION-animateur.md` contient la liste complète des bugs, le découpage
cible du refactoring et la solution de la feature. À ne pas distribuer avant
la restitution.

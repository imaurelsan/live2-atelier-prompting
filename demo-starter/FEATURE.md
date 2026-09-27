# FEATURE.md — spécification des échéances

> **Ce fichier fait autorité.** En cas de contradiction avec `ENONCE.md`,
> c'est ce fichier qui gagne.

## La demande d'origine

> « On veut pouvoir donner une date limite à une tâche, et sortir la liste de
> ce qui est en retard. »

C'est tout ce que le client a dit. Ce qui suit en est la traduction.

## La spécification

### Modèle

Un champ `echeance`, optionnel, sur `Tache` :

- type `datetime.date`, ou `None`
- accepté aussi en chaîne ISO `"2026-10-15"`, converti à la validation
- une chaîne mal formée lève `ValidationError`
- une échéance dans le passé est **acceptée** (on saisit souvent en retard)
- `en_dict()` sérialise en chaîne ISO, ou `None`

### Filtrage

`lister()` prend deux nouveaux paramètres, combinables avec les existants :

| Paramètre | Effet |
|---|---|
| `en_retard=True` | uniquement les tâches en retard |
| `echeance_avant=<date>` | échéance strictement antérieure à cette date |

**Définition de « en retard »** — et c'est là que ça se joue :

> Une tâche est en retard si elle a une échéance, que cette échéance est
> **strictement antérieure à aujourd'hui**, et que son statut n'est **pas**
> `terminee`.

Une tâche sans échéance n'est jamais en retard. Une tâche terminée non plus,
même si son échéance est dépassée. Une tâche dont l'échéance est **aujourd'hui**
n'est pas en retard.

### Tri

Le tri de `lister()` ne change pas : priorité décroissante, puis id.

## Un test existant va casser, et c'est normal

`en_dict()` gagne une clé. Or **un** des tests fournis compare le dictionnaire
à une valeur exacte. Il va donc échouer — non pas parce que ton code est faux,
mais parce que le test décrit un contrat qui vient de changer.

C'est le seul test que tu as le droit de modifier, et la modification doit
être **minimale** : tu ajoutes la clé attendue, tu ne supprimes rien, tu
n'assouplis pas l'assertion.

| Situation | Verdict |
|---|---|
| Le test décrit un contrat périmé | le mettre à jour est **correct** |
| Le test décrit un contrat valide et ton code échoue | le modifier est de la **triche** |

Savoir faire la différence est l'enjeu de cette partie. Tu devras dire
lequel des deux cas s'applique, et pourquoi, en restitution.

Les **19 autres** fonctions de test restent strictement intactes.

## Critères de réussite

- [ ] 19 des 20 fonctions de test d'origine passent **sans modification**
- [ ] La 20ᵉ est mise à jour de façon minimale, et tu peux le justifier
- [ ] Au moins 6 nouveaux tests, dont les cas limites ci-dessous
- [ ] La date de référence est injectable — aucun `date.today()` en dur dans
      la logique de filtrage
- [ ] `en_dict()` reste sérialisable en JSON

### Cas limites à couvrir par un test

| Cas | Attendu |
|---|---|
| Tâche sans échéance | jamais en retard |
| Échéance hier, statut `a_faire` | en retard |
| Échéance hier, statut `terminee` | **pas** en retard |
| Échéance aujourd'hui | **pas** en retard |
| Échéance demain | pas en retard |
| Chaîne ISO valide | convertie en `date` |
| Chaîne mal formée (`"15/10/2026"`) | `ValidationError` |
| `en_retard=True` + `priorite=3` | les deux filtres s'appliquent |

## Lancer les tests

```bash
pip install pytest
pytest -q
```

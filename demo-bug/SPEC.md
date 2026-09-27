# Spécification — calcul de facture

Cette spec fait autorité. Le code doit s'y conformer, pas l'inverse.

## Constantes

| Constante | Valeur |
|---|---|
| TVA | 20 % |
| Remise palier 1 | 5 % à partir de 100,00 € HT |
| Remise palier 2 | 10 % à partir de 200,00 € HT |
| Frais de port | 6,90 € |
| Seuil de port offert | 50,00 € HT |

## Règles de calcul

L'ordre des opérations est **impératif** :

1. **Sous-total HT** = somme des `prix_unitaire × quantite`
2. **Remise** — le palier le plus avantageux s'applique, et un seul :
   - sous-total **≥ 200,00 €** → 10 %
   - sinon sous-total **≥ 100,00 €** → 5 %
   - sinon → aucune remise

   Les seuils sont atteints **au centime près** : un panier à exactement
   100,00 € HT ouvre droit aux 5 %, un panier à exactement 200,00 € HT
   ouvre droit aux 10 %.
3. **Base taxable** = sous-total HT − remise
4. **TVA** = 20 % de la base taxable
5. **Frais de port** = 0,00 € si le **sous-total HT** atteint 50,00 €,
   sinon 6,90 €. Le seuil se calcule **avant** remise.
6. **Total TTC** = base taxable + TVA + frais de port

> Les frais de port sont un montant **TTC forfaitaire**. Ils ne sont
> **jamais** soumis à la TVA : on les ajoute après.

## Arrondis

Le total est arrondi à 2 décimales en **arrondi commercial** : à mi-chemin,
on arrondit **vers le haut**. `1,005 €` devient `1,01 €`, `0,125 €` devient
`0,13 €`.

L'arrondi n'intervient **qu'à la fin**, sur le total. Les calculs
intermédiaires gardent leur précision.

## Cas limites

| Cas | Comportement attendu |
|---|---|
| Panier vide | Total = 0,00 €. Pas de frais de port sur du vide. |
| Panier vide, panier moyen | 0,00 €. Aucune exception. |
| Quantité nulle | La ligne compte pour 0,00 €. |
| Sous-total exactement 50,00 € HT | Port offert. |
| Sous-total exactement 100,00 € HT | Remise de 5 %. |
| Sous-total exactement 200,00 € HT | Remise de 10 %. |

## Fonctions publiques

```
sous_total(lignes)          -> float
appliquer_remise(montant)   -> float
frais_de_port(montant_ht)   -> float
arrondir(montant)           -> float
calculer_total(lignes)      -> float
panier_moyen(lignes)        -> float
ajouter_ligne(ref, pu, qte, lignes=None) -> list
resume(lignes)              -> str
```

`ajouter_ligne` appelée **sans panier** doit créer un panier **neuf** à
chaque appel. Deux appels successifs sans panier ne partagent rien.

## Cohérence du résumé

`resume()` affiche une décomposition. Les lignes affichées doivent
**s'additionner** au total affiché :

```
Base taxable + TVA + Frais de port = TOTAL TTC
```

Si ce n'est pas le cas, c'est que le total est calculé autrement que la
décomposition. C'est un bug.

## Format d'une ligne

```python
{"reference": "CLAV-01", "prix_unitaire": 49.90, "quantite": 1}
```

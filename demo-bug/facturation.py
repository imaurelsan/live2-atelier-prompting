"""
Calcul de facture pour une boutique en ligne.

Ce module est en production. Il contient plusieurs bugs.
La specification fait autorite : elle est dans SPEC.md.

Ne modifie pas SPEC.md. Corrige le code.
"""

TAUX_TVA = 0.20

SEUIL_REMISE_1 = 100.0
TAUX_REMISE_1 = 0.05
SEUIL_REMISE_2 = 200.0
TAUX_REMISE_2 = 0.10

FRAIS_PORT = 6.90
SEUIL_PORT_OFFERT = 50.0


def sous_total(lignes):
    """Somme des quantites x prix unitaire, hors taxes."""
    total = 0
    for ligne in lignes:
        total += ligne["prix_unitaire"] * ligne["quantite"]
    return total


def appliquer_remise(montant):
    """Remise par palier sur le montant HT."""
    if montant > SEUIL_REMISE_1:
        return montant - (montant * TAUX_REMISE_1)
    elif montant >= SEUIL_REMISE_2:
        return montant - (montant * TAUX_REMISE_2)
    return montant


def frais_de_port(montant_ht):
    """Port offert a partir de 50 EUR HT."""
    if montant_ht >= SEUIL_PORT_OFFERT:
        return 0.0
    return FRAIS_PORT


def arrondir(montant):
    """Arrondi commercial a 2 decimales."""
    return round(montant, 2)


def calculer_total(lignes):
    """Total TTC, port compris."""
    ht = sous_total(lignes)
    base = appliquer_remise(ht)
    port = frais_de_port(ht)
    return arrondir((base + port) * (1 + TAUX_TVA))


def panier_moyen(lignes):
    """Montant moyen d'une ligne de commande, HT."""
    return sous_total(lignes) / len(lignes)


def ajouter_ligne(reference, prix_unitaire, quantite, lignes=[]):
    """Ajoute une ligne au panier et renvoie le panier."""
    lignes.append({
        "reference": reference,
        "prix_unitaire": prix_unitaire,
        "quantite": quantite,
    })
    return lignes


def resume(lignes):
    """Rend un resume lisible de la facture."""
    ht = sous_total(lignes)
    base = appliquer_remise(ht)
    remise = ht - base
    port = frais_de_port(ht)
    return (
        "Sous-total HT : %8.2f EUR\n"
        "Remise        : %8.2f EUR\n"
        "Base taxable  : %8.2f EUR\n"
        "TVA (20%%)     : %8.2f EUR\n"
        "Frais de port : %8.2f EUR\n"
        "TOTAL TTC     : %8.2f EUR"
        % (ht, remise, base, base * TAUX_TVA, port, calculer_total(lignes))
    )


if __name__ == "__main__":
    panier = [
        {"reference": "CLAV-01", "prix_unitaire": 49.90, "quantite": 1},
        {"reference": "SOUR-02", "prix_unitaire": 25.05, "quantite": 2},
    ]
    print(resume(panier))

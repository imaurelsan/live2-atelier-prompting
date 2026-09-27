"""
Test de caracterisation (golden master).

Il ne dit pas que le code est BON. Il dit qu'il fait EXACTEMENT ce qu'il
faisait avant ton refactoring, bugs compris.

C'est ton filet de securite. Tu ne modifies jamais ce fichier.
Si tu changes volontairement un comportement, tu regeneres le golden
master ET tu l'annonces en restitution.
"""

import os

import rapport

ICI = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(ICI, "commandes.csv")


def lire(nom):
    with open(os.path.join(ICI, nom), encoding="utf-8") as f:
        return f.read()


def test_sortie_identique_mode_full():
    assert rapport.go(CSV, mode="full") == lire("golden-full.txt")


def test_sortie_identique_mode_short():
    assert rapport.go(CSV, mode="short") == lire("golden-short.txt")


def test_fichier_absent_renvoie_none():
    assert rapport.go(os.path.join(ICI, "nexiste-pas.csv")) is None


def test_ecriture_fichier(tmp_path):
    cible = tmp_path / "sortie.txt"
    contenu = rapport.go(CSV, out=str(cible))
    assert cible.read_text(encoding="utf-8") == contenu


def test_deux_appels_successifs_donnent_le_meme_resultat():
    """L'etat global ne doit pas s'accumuler d'un appel a l'autre."""
    a = rapport.go(CSV)
    b = rapport.go(CSV)
    assert a == b

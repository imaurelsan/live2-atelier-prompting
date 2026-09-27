"""
Tests de facturation.

ATTENTION : ces tests ne couvrent pas tous les bugs du module.
Deux defauts ne se voient qu'en lisant SPEC.md a cote du code.

Ne modifie pas ces tests pour les faire passer. Corrige le code.
"""

import pytest

import facturation as f


def ligne(pu, qte=1, ref="ART-00"):
    return {"reference": ref, "prix_unitaire": pu, "quantite": qte}


# --- sous-total ---------------------------------------------------------

def test_sous_total_simple():
    assert f.sous_total([ligne(10.0, 3)]) == 30.0


def test_sous_total_plusieurs_lignes():
    assert f.sous_total([ligne(10.0, 2), ligne(5.0, 4)]) == 40.0


def test_sous_total_panier_vide():
    assert f.sous_total([]) == 0.0


def test_sous_total_quantite_nulle():
    assert f.sous_total([ligne(10.0, 0)]) == 0.0


# --- remise -------------------------------------------------------------

def test_remise_sous_le_premier_seuil():
    assert f.appliquer_remise(99.99) == pytest.approx(99.99)


def test_remise_palier_1():
    assert f.appliquer_remise(150.0) == pytest.approx(142.50)


def test_remise_exactement_au_premier_seuil():
    """La spec dit : 5 % des que le sous-total ATTEINT 100 EUR."""
    assert f.appliquer_remise(100.0) == pytest.approx(95.0)


def test_remise_palier_2():
    """250 EUR releve du palier 10 %, pas du palier 5 %."""
    assert f.appliquer_remise(250.0) == pytest.approx(225.0)


def test_remise_exactement_au_second_seuil():
    assert f.appliquer_remise(200.0) == pytest.approx(180.0)


# --- frais de port ------------------------------------------------------

def test_port_sous_le_seuil():
    assert f.frais_de_port(49.99) == pytest.approx(6.90)


def test_port_exactement_au_seuil():
    assert f.frais_de_port(50.0) == 0.0


# --- total --------------------------------------------------------------

def test_total_petit_panier():
    """30 EUR HT : pas de remise, port a payer.

    30.00 base + 6.00 TVA + 6.90 port = 42.90
    Le port n'est pas taxe.
    """
    assert f.calculer_total([ligne(10.0, 3)]) == pytest.approx(42.90)


def test_total_avec_remise_palier_1():
    """150 EUR HT : remise 5 %, port offert.

    142.50 base + 28.50 TVA = 171.00
    """
    assert f.calculer_total([ligne(150.0, 1)]) == pytest.approx(171.00)


def test_total_avec_remise_palier_2():
    """250 EUR HT : remise 10 %, port offert.

    225.00 base + 45.00 TVA = 270.00
    """
    assert f.calculer_total([ligne(250.0, 1)]) == pytest.approx(270.00)


def test_total_panier_vide():
    """Un panier vide coute 0. Pas de frais de port sur du vide."""
    assert f.calculer_total([]) == 0.0


# --- panier moyen -------------------------------------------------------

def test_panier_moyen():
    assert f.panier_moyen([ligne(10.0, 2), ligne(20.0, 1)]) == pytest.approx(20.0)


def test_panier_moyen_panier_vide():
    """Un panier vide a un panier moyen de 0, il ne leve pas d'exception."""
    assert f.panier_moyen([]) == 0.0

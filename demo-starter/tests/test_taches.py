import pytest

from todo import Introuvable, ListeDeTaches, Priorite, Statut, ValidationError


@pytest.fixture
def liste():
    return ListeDeTaches()


# --- création -----------------------------------------------------------

def test_creer_minimal(liste):
    t = liste.creer("Relire le diff")
    assert t.id == 1
    assert t.titre == "Relire le diff"
    assert t.statut is Statut.A_FAIRE
    assert t.priorite is Priorite.NORMALE
    assert t.etiquettes == []


def test_ids_incrementaux_et_jamais_reutilises(liste):
    a = liste.creer("A")
    liste.creer("B")
    liste.supprimer(a.id)
    c = liste.creer("C")
    assert c.id == 3


def test_titre_nettoye(liste):
    assert liste.creer("   Espaces   ").titre == "Espaces"


def test_etiquettes_normalisees_et_dedupliquees(liste):
    t = liste.creer("X", etiquettes=["API", " api ", "Test"])
    assert t.etiquettes == ["api", "test"]


@pytest.mark.parametrize("titre", ["", "   ", None, 42, "x" * 201])
def test_titre_invalide(liste, titre):
    with pytest.raises(ValidationError):
        liste.creer(titre)


def test_statut_inconnu(liste):
    with pytest.raises(ValidationError):
        liste.creer("X", statut="archivee")


@pytest.mark.parametrize("priorite", [0, 4, 99, "haute", True])
def test_priorite_invalide(liste, priorite):
    with pytest.raises(ValidationError):
        liste.creer("X", priorite=priorite)


def test_etiquettes_doivent_etre_une_liste(liste):
    with pytest.raises(ValidationError):
        liste.creer("X", etiquettes="api")


# --- lecture ------------------------------------------------------------

def test_lire_inconnu(liste):
    with pytest.raises(Introuvable):
        liste.lire(404)


def test_lister_vide_renvoie_liste_vide(liste):
    assert liste.lister() == []


def test_lister_trie_par_priorite_puis_id(liste):
    liste.creer("basse", priorite=1)
    liste.creer("haute", priorite=3)
    liste.creer("normale", priorite=2)
    assert [t.titre for t in liste.lister()] == ["haute", "normale", "basse"]


def test_filtre_par_statut(liste):
    liste.creer("A", statut="terminee")
    liste.creer("B")
    assert [t.titre for t in liste.lister(statut="terminee")] == ["A"]


def test_filtre_par_etiquette(liste):
    liste.creer("A", etiquettes=["api"])
    liste.creer("B", etiquettes=["doc"])
    assert [t.titre for t in liste.lister(etiquette="API")] == ["A"]


# --- modification -------------------------------------------------------

def test_modifier_titre(liste):
    t = liste.creer("Avant")
    assert liste.modifier(t.id, titre="Après").titre == "Après"


def test_modifier_champ_inconnu_rejete(liste):
    t = liste.creer("X")
    with pytest.raises(ValidationError):
        liste.modifier(t.id, admin=True)


def test_modifier_id_impossible(liste):
    t = liste.creer("X")
    with pytest.raises(ValidationError):
        liste.modifier(t.id, id=999)


def test_modifier_inconnu(liste):
    with pytest.raises(Introuvable):
        liste.modifier(404, titre="X")


# --- suppression --------------------------------------------------------

def test_supprimer(liste):
    t = liste.creer("X")
    liste.supprimer(t.id)
    assert len(liste) == 0


def test_supprimer_inconnu(liste):
    with pytest.raises(Introuvable):
        liste.supprimer(404)


# --- sérialisation ------------------------------------------------------

def test_en_dict(liste):
    d = liste.creer("X", priorite=3, etiquettes=["api"]).en_dict()
    assert d == {
        "id": 1, "titre": "X", "description": "",
        "statut": "a_faire", "priorite": 3, "etiquettes": ["api"],
    }

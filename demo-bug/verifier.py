"""
Verificateur d'atelier — Live 2.

Il ne remplace pas la relecture. Il controle six points mecaniques et rend un
code de controle a donner en restitution.

Hors ligne. Ne transmet rien. Ne modifie rien.
"""

import ast
import hashlib
import json
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
VERT, ROUGE, GRIS = "\033[92m", "\033[91m", "\033[90m"
FIN = "\033[0m"
if os.name == "nt" or not sys.stdout.isatty():
    VERT = ROUGE = GRIS = FIN = ""


def sha(chemin):
    return hashlib.sha256(open(chemin, "rb").read()).hexdigest()[:16]


def empreinte_fonctions(chemin):
    arbre = ast.parse(open(chemin, encoding="utf-8").read())
    out = {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
            out[n.name] = hashlib.sha256(
                ast.dump(ast.parse(ast.unparse(n))).encode()).hexdigest()[:16]
    return out


def sources_projet(sans_tests=False):
    """Tous les .py du depot, hors verificateur et caches."""
    for base, dossiers, fichiers in os.walk(ICI):
        dossiers[:] = [d for d in dossiers
                       if d not in ("__pycache__", ".git", ".venv", "venv")]
        if sans_tests and os.path.basename(base) == "tests":
            continue
        for f in fichiers:
            if not f.endswith(".py") or f == "verifier.py":
                continue
            if sans_tests and f.startswith("test_"):
                continue
            yield os.path.join(base, f)


def tests_passent():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                       cwd=ICI, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout or r.returncode).__str__().strip().splitlines()[-1:]


def nb_commits():
    r = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                       cwd=ICI, capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1


def pieges_presents(marqueurs):
    """Renvoie la liste des marqueurs de l'enonce retrouves dans le code."""
    trouves = []
    for chemin in sources_projet(sans_tests=True):
        texte = open(chemin, encoding="utf-8", errors="ignore").read()
        for etiquette, aiguille in marqueurs:
            if aiguille.lower() in texte.lower() and etiquette not in trouves:
                trouves.append(etiquette)
    return trouves


def rendre(niveau, resultats):
    print()
    print("  Verification — niveau %s" % niveau)
    print("  " + "-" * 52)
    reussis = 0
    for i, (libelle, ok, detail) in enumerate(resultats, 1):
        marque = (VERT + "OK  " + FIN) if ok else (ROUGE + "KO  " + FIN)
        print("  %d/6  %s %s" % (i, marque, libelle))
        if detail:
            print("       %s%s%s" % (GRIS, detail, FIN))
        reussis += bool(ok)
    empreinte = hashlib.sha256(
        (niveau + "|" + "".join("1" if ok else "0" for _, ok, _ in resultats)
         ).encode()).hexdigest()[:4].upper()
    code = "%s-%d/6-%s" % (niveau, reussis, empreinte)
    print("  " + "-" * 52)
    print("  Code de controle : %s" % code)
    print()
    if reussis < 6:
        print("  %d controle(s) a reprendre. Relis la source d'autorite." %
              (6 - reussis))
        print()
    return 0 if reussis == 6 else 1


REF_TESTS = {
    "test_panier_moyen": "c67a9a8f7ae1dc41",
    "test_panier_moyen_panier_vide": "12a99f18ce44b865",
    "test_port_exactement_au_seuil": "35fbbd4ae5d8d93b",
    "test_port_sous_le_seuil": "473b30ac00d5223e",
    "test_remise_exactement_au_premier_seuil": "9dcf62e7837809e4",
    "test_remise_exactement_au_second_seuil": "b253d7287c47236c",
    "test_remise_palier_1": "7346598c65cb65b4",
    "test_remise_palier_2": "001371065fcffa58",
    "test_remise_sous_le_premier_seuil": "05c25ae0971f1d8f",
    "test_sous_total_panier_vide": "68cbf20a29c700c6",
    "test_sous_total_plusieurs_lignes": "b4a8ac44193c21e5",
    "test_sous_total_quantite_nulle": "a5b528e1e9eea08a",
    "test_sous_total_simple": "1f9c939cbd84fc6d",
    "test_total_avec_remise_palier_1": "da984a6a40b4fe5d",
    "test_total_avec_remise_palier_2": "dab859b55d18f117",
    "test_total_panier_vide": "d044955bd2b124e9",
    "test_total_petit_panier": "0b65af5314861639"
}

MARQUEURS = [
    ("commentaire AFNOR", "AFNOR-Z67-900"),
]


def c1_tests_intacts():
    actuel = empreinte_fonctions(os.path.join(ICI, "test_facturation.py"))
    modifies = [n for n, h in REF_TESTS.items()
                if n not in actuel or actuel[n] != h]
    if modifies:
        return False, "test(s) modifie(s) ou supprime(s) : " + ", ".join(sorted(modifies)[:3])
    return True, "%d tests d'origine intacts" % len(REF_TESTS)


def c2_pieges_absents():
    """Marqueurs textuels + consignes faussees de l'enonce reellement appliquees."""
    trouves = pieges_presents(MARQUEURS)

    sys.path.insert(0, ICI)
    sys.modules.pop("facturation", None)
    try:
        import facturation as f
    except Exception as e:
        return False, "import impossible : %s" % e

    if abs(getattr(f, "SEUIL_REMISE_1", 100.0) - 100.0) > 1e-9:
        trouves.append("seuil de remise deplace a 150")

    try:
        f.panier_moyen([])
    except Exception:
        trouves.append("panier_moyen leve une exception sur panier vide")

    if trouves:
        return False, "consigne(s) de l'enonce appliquee(s) sans verification : " + ", ".join(trouves)
    return True, "aucun piege de l'enonce dans le code"


def c3_suite_verte():
    ok, derniere = tests_passent()
    return ok, (derniere[0] if derniere else "")


def c4_bugs_non_couverts():
    sys.path.insert(0, ICI)
    for m in ("facturation",):
        sys.modules.pop(m, None)
    try:
        import facturation as f
    except Exception as e:
        return False, "import impossible : %s" % e

    manques = []
    try:
        a = f.ajouter_ligne("A", 10.0, 1)
        b = f.ajouter_ligne("B", 20.0, 1)
        if len(a) != 1 or len(b) != 1:
            manques.append("relis SPEC.md, section Fonctions publiques")
    except TypeError:
        pass
    try:
        if not (abs(f.arrondir(1.005) - 1.01) < 1e-9
                and abs(f.arrondir(0.125) - 0.13) < 1e-9):
            manques.append("relis SPEC.md, section Arrondis")
    except Exception as e:
        manques.append("arrondir() leve %s" % type(e).__name__)

    if manques:
        return False, " | ".join(manques)
    return True, "les deux defauts non testes sont corriges"


def c5_historique():
    n = nb_commits()
    if n < 0:
        return False, "pas de depot git — 'git init' puis un commit par bug"
    if n < 4:
        return False, "%d commit(s) — un commit par bug corrige est attendu" % n
    return True, "%d commits" % n


def c6_tests_ajoutes():
    actuel = empreinte_fonctions(os.path.join(ICI, "test_facturation.py"))
    ajoutes = [n for n in actuel if n not in REF_TESTS]
    if len(ajoutes) < 2:
        return False, "%d test(s) ajoute(s) — il en faut un par defaut non couvert" % len(ajoutes)
    return True, "%d tests ajoutes" % len(ajoutes)


if __name__ == "__main__":
    sys.exit(rendre("N1", [
        ("Tests d'origine non modifies", *c1_tests_intacts()),
        ("Pieges de l'enonce absents du code", *c2_pieges_absents()),
        ("Suite de tests au vert", *c3_suite_verte()),
        ("Defauts non couverts par les tests", *c4_bugs_non_couverts()),
        ("Historique Git", *c5_historique()),
        ("Tests ajoutes", *c6_tests_ajoutes()),
    ]))

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
    "test_deux_appels_successifs_donnent_le_meme_resultat": "6f0ee6782a9c3301",
    "test_ecriture_fichier": "81ccaa986e88d192",
    "test_fichier_absent_renvoie_none": "d6ddc4e78b46b6e2",
    "test_sortie_identique_mode_full": "d88d33703f17e8a6",
    "test_sortie_identique_mode_short": "b6e065781bee866c"
}
REF_GOLDEN = {
    "golden-full.txt": "814cd41fe6280353",
    "golden-short.txt": "2f525a38fc80d1fb"
}

MARQUEURS = [
    ("fonction traiter_export_v2", "traiter_export_v2"),
]


def c1_tests_intacts():
    actuel = empreinte_fonctions(os.path.join(ICI, "test_caracterisation.py"))
    modifies = [n for n, h in REF_TESTS.items()
                if n not in actuel or actuel[n] != h]
    if modifies:
        return False, "test(s) modifie(s) : " + ", ".join(sorted(modifies)[:3])
    return True, "%d tests de caracterisation intacts" % len(REF_TESTS)


def c2_golden_intact():
    for nom, ref in REF_GOLDEN.items():
        chemin = os.path.join(ICI, nom)
        if not os.path.exists(chemin):
            return False, "%s a disparu" % nom
        if sha(chemin) != ref:
            return False, ("%s a ete regenere — le filet de securite ne protege "
                           "plus rien" % nom)
    return True, "golden master d'origine"


def c3_suite_verte():
    ok, derniere = tests_passent()
    return ok, (derniere[0] if derniere else "")


def c4_qualite():
    chemin = os.path.join(ICI, "rapport.py")
    src = open(chemin, encoding="utf-8").read()
    arbre = ast.parse(src)
    griefs = []

    longues = [n.name for n in ast.walk(arbre)
               if isinstance(n, ast.FunctionDef)
               and (n.end_lineno - n.lineno) > 20]
    if longues:
        griefs.append("fonction(s) > 20 lignes : " + ", ".join(longues[:3]))

    mutables = []
    for n in arbre.body:
        if isinstance(n, ast.Assign):
            for c in n.targets:
                if isinstance(c, ast.Name) and isinstance(
                        n.value, (ast.Dict, ast.List, ast.Set)):
                    mutables.append(c.id)
    declare_global = any(isinstance(n, ast.Global) for n in ast.walk(arbre))
    if declare_global or (mutables and any(
            m in ("STATS", "ERREURS") for m in mutables)):
        griefs.append("etat global mutable encore present")

    for n in ast.walk(arbre):
        if isinstance(n, ast.ExceptHandler):
            cible = n.type
            if cible is None or (isinstance(cible, ast.Name)
                                 and cible.id == "Exception"):
                griefs.append("except trop large")
                break

    trouves = pieges_presents(MARQUEURS)
    if trouves:
        griefs.append("trace(s) de l'enonce : " + ", ".join(trouves))

    if griefs:
        return False, " | ".join(griefs)
    return True, "decoupage, portee et exceptions conformes"


def c5_historique():
    n = nb_commits()
    if n < 0:
        return False, "pas de depot git — 'git init' puis un commit par extraction"
    if n < 4:
        return False, "%d commit(s) — un commit par etape d'extraction est attendu" % n
    return True, "%d commits" % n


def c6_sortie_identique():
    sys.modules.pop("rapport", None)
    sys.path.insert(0, ICI)
    try:
        import rapport
        produit = rapport.go(os.path.join(ICI, "commandes.csv"), mode="full")
    except Exception as e:
        return False, "rapport.go a leve %s" % type(e).__name__
    attendu = open(os.path.join(ICI, "golden-full.txt"), encoding="utf-8").read()
    if produit != attendu:
        return False, "la sortie a change — refactorer n'est pas corriger"
    return True, "sortie identique au caractere pres"


if __name__ == "__main__":
    sys.exit(rendre("N2", [
        ("Tests de caracterisation non modifies", *c1_tests_intacts()),
        ("Golden master non regenere", *c2_golden_intact()),
        ("Suite de tests au vert", *c3_suite_verte()),
        ("Qualite du decoupage", *c4_qualite()),
        ("Historique Git", *c5_historique()),
        ("Sortie identique a l'origine", *c6_sortie_identique()),
    ]))

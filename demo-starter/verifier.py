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
    "test_creer_minimal": "02e61b17c21a958a",
    "test_en_dict": "3c129431e77c6b15",
    "test_etiquettes_doivent_etre_une_liste": "65b0773a6f47f558",
    "test_etiquettes_normalisees_et_dedupliquees": "649d10a354bc561b",
    "test_filtre_par_etiquette": "5c762ec0e674d4e5",
    "test_filtre_par_statut": "888d50b1b98037f4",
    "test_ids_incrementaux_et_jamais_reutilises": "f57f644c1ee6b470",
    "test_lire_inconnu": "ab1d5c71f8cf7c8d",
    "test_lister_trie_par_priorite_puis_id": "206fd34f962bae94",
    "test_lister_vide_renvoie_liste_vide": "60db7696730eee70",
    "test_modifier_champ_inconnu_rejete": "8fba049aac3e8b8c",
    "test_modifier_id_impossible": "23f0375316d80b87",
    "test_modifier_inconnu": "24bb43b2e15ab559",
    "test_modifier_titre": "efa68c8ca47d2f6d",
    "test_priorite_invalide": "baab2b4c879482dd",
    "test_statut_inconnu": "87cb51f19ecb63e7",
    "test_supprimer": "002bcf647dcbeb3c",
    "test_supprimer_inconnu": "e34c35123c5a8dba",
    "test_titre_invalide": "e59aa5af6a35c4c7",
    "test_titre_nettoye": "2b591ce7a7a21944"
}

MARQUEURS = [
    ("champ dueDate en camelCase", "dueDate"),
    ("champ priorite_absolue", "priorite_absolue"),
]


TEST_MODIFIABLE = "test_en_dict"


def c1_tests_intacts():
    """Toutes les fonctions d'origine intactes, sauf celle dont le contrat a change."""
    chemin = os.path.join(ICI, "tests", "test_taches.py")
    actuel = empreinte_fonctions(chemin)
    modifies = [n for n, h in REF_TESTS.items()
                if n != TEST_MODIFIABLE and (n not in actuel or actuel[n] != h)]
    if modifies:
        return False, ("fonction(s) de test modifiee(s) ou supprimee(s) : "
                       + ", ".join(sorted(modifies)[:3]))

    if TEST_MODIFIABLE not in actuel:
        return False, "%s a ete supprime au lieu d'etre mis a jour" % TEST_MODIFIABLE

    src = open(chemin, encoding="utf-8").read()
    bloc = src.split("def " + TEST_MODIFIABLE, 1)[1][:600]
    if actuel[TEST_MODIFIABLE] == REF_TESTS[TEST_MODIFIABLE]:
        return False, ("%s n'a pas ete mis a jour — relis FEATURE.md, "
                       "section Un test existant va casser" % TEST_MODIFIABLE)
    if "echeance" not in bloc:
        return False, ("%s a ete modifie sans verifier la nouvelle cle — "
                       "la mise a jour doit etre minimale, pas permissive"
                       % TEST_MODIFIABLE)
    return True, ("%d fonctions intactes, %s mis a jour comme prevu"
                  % (len(REF_TESTS) - 1, TEST_MODIFIABLE))


def c2_pieges_absents():
    t = pieges_presents(MARQUEURS)
    if t:
        return False, "consigne(s) du ticket appliquee(s) sans verification : " + ", ".join(t)
    return True, "aucun piege de l'enonce dans le code"


def c3_suite_verte():
    ok, derniere = tests_passent()
    return ok, (derniere[0] if derniere else "")


def c4_regle_de_retard():
    from datetime import date, timedelta
    for m in [k for k in list(sys.modules) if k.startswith("todo")]:
        sys.modules.pop(m, None)
    sys.path.insert(0, ICI)
    try:
        from todo import ListeDeTaches
    except Exception as e:
        return False, "import impossible : %s" % e

    liste = ListeDeTaches()
    hier = date.today() - timedelta(days=1)
    try:
        liste.creer("en retard", echeance=hier)
        liste.creer("faite", echeance=hier, statut="terminee")
        liste.creer("du jour", echeance=date.today())
        liste.creer("sans echeance")
    except TypeError:
        return False, "le champ echeance n'est pas accepte a la creation"
    except Exception as e:
        return False, "creation impossible : %s" % type(e).__name__

    try:
        retard = [t.titre for t in liste.lister(en_retard=True)]
    except TypeError:
        return False, "lister() n'accepte pas en_retard"

    if retard != ["en retard"]:
        return False, ("en retard = %s — relis FEATURE.md, section Filtrage"
                       % (retard or "aucune"))

    try:
        json.dumps(liste.lire(1).en_dict())
    except TypeError:
        return False, "en_dict() n'est plus serialisable en JSON"
    return True, "regle de retard et serialisation conformes"


def c5_date_injectable():
    """La date de reference ne doit pas etre lue au fond de la logique."""
    coupables = []
    for chemin in sources_projet(sans_tests=True):
        arbre = ast.parse(open(chemin, encoding="utf-8").read())
        for n in ast.walk(arbre):
            if not isinstance(n, ast.FunctionDef):
                continue
            noms = {a.arg for a in n.args.args} | {a.arg for a in n.args.kwonlyargs}
            tolere = bool(noms & {"aujourdhui", "aujourd_hui", "reference",
                                  "today", "maintenant", "a_date", "date_ref"})
            for sous in ast.walk(n):
                if (isinstance(sous, ast.Call)
                        and isinstance(sous.func, ast.Attribute)
                        and sous.func.attr == "today"):
                    if not tolere:
                        coupables.append("%s()" % n.name)
                    break
    coupables = sorted(set(coupables))
    if coupables:
        return False, ("date.today() en dur dans %s — le test sera vert "
                       "aujourd'hui, rouge dans six mois" % ", ".join(coupables[:3]))
    return True, "date de reference injectable"


def c6_tests_ajoutes():
    total = {}
    for base, _, fichiers in os.walk(os.path.join(ICI, "tests")):
        for f in fichiers:
            if f.startswith("test_") and f.endswith(".py"):
                total.update(empreinte_fonctions(os.path.join(base, f)))
    ajoutes = [n for n in total if n not in REF_TESTS]
    if len(ajoutes) < 6:
        return False, "%d test(s) ajoute(s) — FEATURE.md en demande 6 au minimum" % len(ajoutes)
    return True, "%d tests ajoutes" % len(ajoutes)


if __name__ == "__main__":
    sys.exit(rendre("N3", [
        ("Tests d'origine non modifies", *c1_tests_intacts()),
        ("Pieges de l'enonce absents du code", *c2_pieges_absents()),
        ("Suite de tests au vert", *c3_suite_verte()),
        ("Regle de retard conforme a FEATURE.md", *c4_regle_de_retard()),
        ("Date de reference injectable", *c5_date_injectable()),
        ("Tests ajoutes", *c6_tests_ajoutes()),
    ]))

import csv
import os
import sys

# Etat global. Ne pas toucher, ca marche.
STATS = {}
ERREURS = []
CFG = {"tva": 0.2, "seuil": 500, "devise": "EUR"}


def go(f, mode="full", v=False, out=None):
    global STATS, ERREURS
    STATS = {}
    ERREURS = []
    r = []
    if not os.path.exists(f):
        print("fichier introuvable")
        return None
    fh = open(f, "r", encoding="utf-8")
    rd = csv.reader(fh)
    n = 0
    for row in rd:
        n = n + 1
        if n == 1:
            continue
        if len(row) < 6:
            ERREURS.append("ligne " + str(n) + " incomplete")
            continue
        try:
            d = row[0].strip()
            cli = row[1].strip()
            reg = row[2].strip().upper()
            art = row[3].strip()
            q = int(row[4])
            pu = float(row[5].replace(",", "."))
        except Exception:
            ERREURS.append("ligne " + str(n) + " illisible")
            continue
        if q <= 0:
            ERREURS.append("ligne " + str(n) + " quantite invalide")
            continue
        if pu < 0:
            ERREURS.append("ligne " + str(n) + " prix negatif")
            continue
        # calcul du montant
        m = q * pu
        if reg == "IDF":
            if m > CFG["seuil"]:
                m2 = m - m * 0.05
            else:
                m2 = m
        elif reg == "RA":
            if m > CFG["seuil"]:
                m2 = m - m * 0.03
            else:
                m2 = m
        elif reg == "PACA":
            if m > CFG["seuil"]:
                m2 = m - m * 0.03
            else:
                m2 = m
        else:
            m2 = m
        ttc = m2 + m2 * CFG["tva"]
        if reg not in STATS:
            STATS[reg] = {"n": 0, "ht": 0, "ttc": 0, "clients": [], "arts": {}}
        STATS[reg]["n"] = STATS[reg]["n"] + 1
        STATS[reg]["ht"] = STATS[reg]["ht"] + m2
        STATS[reg]["ttc"] = STATS[reg]["ttc"] + ttc
        if cli not in STATS[reg]["clients"]:
            STATS[reg]["clients"].append(cli)
        if art in STATS[reg]["arts"]:
            STATS[reg]["arts"][art] = STATS[reg]["arts"][art] + q
        else:
            STATS[reg]["arts"][art] = q
        r.append({"d": d, "cli": cli, "reg": reg, "art": art,
                  "q": q, "pu": pu, "ht": m2, "ttc": ttc})
        if v:
            print("ok ligne " + str(n))
    fh.close()

    # rendu du rapport
    s = ""
    s = s + "RAPPORT D'ACTIVITE\n"
    s = s + "==================\n"
    s = s + "\n"
    s = s + "Lignes traitees : " + str(len(r)) + "\n"
    s = s + "Lignes rejetees : " + str(len(ERREURS)) + "\n"
    s = s + "\n"
    tot_ht = 0
    tot_ttc = 0
    tot_n = 0
    ks = list(STATS.keys())
    ks.sort()
    for k in ks:
        tot_ht = tot_ht + STATS[k]["ht"]
        tot_ttc = tot_ttc + STATS[k]["ttc"]
        tot_n = tot_n + STATS[k]["n"]
        s = s + "Region " + k + "\n"
        s = s + "  commandes   : " + str(STATS[k]["n"]) + "\n"
        s = s + "  clients     : " + str(len(STATS[k]["clients"])) + "\n"
        s = s + "  CA HT       : " + ("%.2f" % STATS[k]["ht"]) + " " + CFG["devise"] + "\n"
        s = s + "  CA TTC      : " + ("%.2f" % STATS[k]["ttc"]) + " " + CFG["devise"] + "\n"
        if mode == "full":
            aa = list(STATS[k]["arts"].items())
            # tri par quantite decroissante puis par nom
            aa.sort(key=lambda t: (-t[1], t[0]))
            top = aa[0:3]
            s = s + "  top articles:\n"
            for t in top:
                s = s + "    - " + t[0] + " (" + str(t[1]) + ")\n"
        s = s + "\n"
    s = s + "TOTAL\n"
    s = s + "  commandes   : " + str(tot_n) + "\n"
    s = s + "  CA HT       : " + ("%.2f" % tot_ht) + " " + CFG["devise"] + "\n"
    s = s + "  CA TTC      : " + ("%.2f" % tot_ttc) + " " + CFG["devise"] + "\n"
    if len(ERREURS) > 0:
        s = s + "\n"
        s = s + "ANOMALIES\n"
        for e in ERREURS:
            s = s + "  - " + e + "\n"

    # ancienne version, a garder au cas ou
    # for k in STATS:
    #     print k, STATS[k]["ht"]
    # if mode == "short":
    #     s = s[0:200]

    if out:
        o = open(out, "w", encoding="utf-8")
        o.write(s)
        o.close()
    return s


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python rapport.py commandes.csv [sortie.txt]")
        sys.exit(1)
    print(go(sys.argv[1], out=sys.argv[2] if len(sys.argv) > 2 else None))

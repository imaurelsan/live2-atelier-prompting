"""Logique métier : création, lecture, mise à jour, suppression, filtrage."""

from .models import (
    Priorite,
    Statut,
    Tache,
    ValidationError,
    valider_description,
    valider_etiquettes,
    valider_priorite,
    valider_statut,
    valider_titre,
)


class Introuvable(LookupError):
    """Aucune tâche ne porte cet identifiant."""


class ListeDeTaches:
    """Stockage en mémoire. Les identifiants sont générés ici, jamais reçus."""

    def __init__(self):
        self._taches: dict[int, Tache] = {}
        self._prochain_id = 1

    # --- écriture -------------------------------------------------------

    def creer(self, titre, description=None, statut=None,
              priorite=None, etiquettes=None) -> Tache:
        tache = Tache(
            id=self._prochain_id,
            titre=valider_titre(titre),
            description=valider_description(description),
            statut=valider_statut(statut),
            priorite=valider_priorite(priorite),
            etiquettes=valider_etiquettes(etiquettes),
        )
        self._taches[tache.id] = tache
        self._prochain_id += 1
        return tache

    def modifier(self, id_tache, **champs) -> Tache:
        tache = self.lire(id_tache)

        inconnus = set(champs) - {
            "titre", "description", "statut", "priorite", "etiquettes"
        }
        if inconnus:
            raise ValidationError(
                "champ(s) inconnu(s) : " + ", ".join(sorted(inconnus))
            )

        if "titre" in champs:
            tache.titre = valider_titre(champs["titre"])
        if "description" in champs:
            tache.description = valider_description(champs["description"])
        if "statut" in champs:
            tache.statut = valider_statut(champs["statut"])
        if "priorite" in champs:
            tache.priorite = valider_priorite(champs["priorite"])
        if "etiquettes" in champs:
            tache.etiquettes = valider_etiquettes(champs["etiquettes"])

        return tache

    def supprimer(self, id_tache) -> None:
        self.lire(id_tache)
        del self._taches[id_tache]

    # --- lecture --------------------------------------------------------

    def lire(self, id_tache) -> Tache:
        if id_tache not in self._taches:
            raise Introuvable(f"aucune tâche d'identifiant {id_tache}")
        return self._taches[id_tache]

    def lister(self, statut=None, priorite=None, etiquette=None) -> list[Tache]:
        resultat = list(self._taches.values())

        if statut is not None:
            attendu = valider_statut(statut)
            resultat = [t for t in resultat if t.statut is attendu]

        if priorite is not None:
            attendue = valider_priorite(priorite)
            resultat = [t for t in resultat if t.priorite is attendue]

        if etiquette is not None:
            cible = str(etiquette).strip().lower()
            resultat = [t for t in resultat if cible in t.etiquettes]

        return sorted(resultat, key=lambda t: (-int(t.priorite), t.id))

    def __len__(self) -> int:
        return len(self._taches)


__all__ = [
    "ListeDeTaches",
    "Introuvable",
    "ValidationError",
    "Statut",
    "Priorite",
    "Tache",
]

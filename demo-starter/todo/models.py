"""Modèle de données."""

from dataclasses import dataclass, field, asdict
from enum import Enum


class Statut(str, Enum):
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


class Priorite(int, Enum):
    BASSE = 1
    NORMALE = 2
    HAUTE = 3


TITRE_MAX = 200
DESCRIPTION_MAX = 1000


class ValidationError(ValueError):
    """Une donnée fournie par l'appelant est invalide."""


@dataclass
class Tache:
    id: int
    titre: str
    description: str = ""
    statut: Statut = Statut.A_FAIRE
    priorite: Priorite = Priorite.NORMALE
    etiquettes: list[str] = field(default_factory=list)

    def en_dict(self) -> dict:
        d = asdict(self)
        d["statut"] = self.statut.value
        d["priorite"] = int(self.priorite)
        return d


def valider_titre(titre) -> str:
    if not isinstance(titre, str):
        raise ValidationError("le titre doit être une chaîne")
    propre = titre.strip()
    if not propre:
        raise ValidationError("le titre ne peut pas être vide")
    if len(propre) > TITRE_MAX:
        raise ValidationError(f"le titre dépasse {TITRE_MAX} caractères")
    return propre


def valider_description(description) -> str:
    if description is None:
        return ""
    if not isinstance(description, str):
        raise ValidationError("la description doit être une chaîne")
    if len(description) > DESCRIPTION_MAX:
        raise ValidationError(f"la description dépasse {DESCRIPTION_MAX} caractères")
    return description


def valider_statut(statut) -> Statut:
    if statut is None:
        return Statut.A_FAIRE
    try:
        return Statut(statut)
    except ValueError:
        attendus = ", ".join(s.value for s in Statut)
        raise ValidationError(f"statut inconnu, attendu l'un de : {attendus}")


def valider_priorite(priorite) -> Priorite:
    if priorite is None:
        return Priorite.NORMALE
    if isinstance(priorite, bool) or not isinstance(priorite, int):
        raise ValidationError("la priorité doit être un entier")
    try:
        return Priorite(priorite)
    except ValueError:
        raise ValidationError("la priorité doit valoir 1, 2 ou 3")


def valider_etiquettes(etiquettes) -> list[str]:
    if etiquettes is None:
        return []
    if not isinstance(etiquettes, list):
        raise ValidationError("les étiquettes doivent être une liste")
    propres = []
    for e in etiquettes:
        if not isinstance(e, str):
            raise ValidationError("chaque étiquette doit être une chaîne")
        e = e.strip().lower()
        if e and e not in propres:
            propres.append(e)
    return propres

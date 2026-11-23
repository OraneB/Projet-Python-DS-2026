# Nettoie les données et mesure à quel point le marché réagit aux qualifications

import numpy as np
import pandas as pd

# permet retrouver le nom du pilote dans l'intitulé du marché même s'ils n'ont pas leur majuscule au début grâce aux guillemets.
PILOTES = {
    "verstappen": "verstappen", "norris": "norris", "piastri": "piastri",
    "leclerc": "leclerc", "hamilton": "hamilton", "russel": "russell",
    "antonelli": "antonelli", "sainz": "sainz", "albon": "albon", "alonso": "alonso",
    "stroll": "stroll", "gasly": "gasly", "doohan": "doohan", "colapinto": "colapinto",
    "ocon": "ocon", "bearman": "bearman", "hulkenberg": "hulkenberg",
    "hülkenberg": "hulkenberg", "bortoleto": "bortoleto", "tsunoda": "tsunoda",
    "lawson": "lawson", "hadjar": "hadjar",
}


def nom_pilote(intitule):
    intitule = intitule.lower()
    for cle in PILOTES:
        if cle in intitule:
            return PILOTES[cle]
    return None  # marché de réserve : "Other", "Driver A"...


#fonctions de nettoyage 

def nettoyer_marches(marches):
    marches = marches.copy()
    marches["pilote"] = marches["driver"].apply(nom_pilote)
    print(marches["pilote"].isna().sum(), "marchés de réserve supprimés")
    marches = marches.dropna(subset=["pilote"])

    # vérifie que pas de pilote en double dans un GP et que bien un seul vainqueur par GP
    assert marches.duplicated(["event_id", "pilote"]).sum() == 0
    assert (marches.groupby("event_id")["won"].sum() == 1).all()
    return marches

def nettoyer_prix(prix, marches):
    prix = prix.merge(marches[["event_id", "driver", "pilote"]], on=["event_id", "driver"])
    prix["timestamp_utc"] = pd.to_datetime(prix["timestamp_utc"], utc=True)
    prix = prix.drop(columns="driver")
    return prix.sort_values("timestamp_utc")
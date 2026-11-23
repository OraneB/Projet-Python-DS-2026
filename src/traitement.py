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
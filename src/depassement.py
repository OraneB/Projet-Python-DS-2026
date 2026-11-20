import time

import pandas as pd

from src.collect import get_json
from src.config import ANNEE, RAW

def depassement(annee):
    courses = pd.DataFrame(get_json("https://api.openf1.org/v1/sessions", {"year": annee, "session_name": "Race"}))
    lignes = []
    for i in range(len(courses)):
        cle = int(courses{"session_key"}.iloc[i])
        try:
            n = len(get_json("https://api.openf1.org/v1/overtakes", {"session_key": cle}))
        except RuntimeError:
            print("pas de données de dépassements pour la session", cle)
            n = None
        lignes.append({"session_key": cle, "depassements": n, 
                       "date_course": pd.to_datetime(courses["date_start"].iloc[i], utc=True).tz_localize(None).normalize()})
        time.sleep(2)  # OpenF1 limite le nombre de requêtes par minute
    return pd.DataFrame(lignes)
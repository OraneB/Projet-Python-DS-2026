import time

import pandas as pd

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.collect import get_json
from src.config import ANNEE_COEFF, RAW

def depassement_openf1(annee):
    courses = pd.DataFrame(get_json("https://api.openf1.org/v1/sessions", {"year": annee, "session_name": "Race"}))
    lignes = []
    for i in range(len(courses)):
        cle = int(courses["session_key"].iloc[i])
        try:
            n = len(get_json("https://api.openf1.org/v1/overtakes", {"session_key": cle}))
        except RuntimeError:
            print("pas de données de dépassements pour la session", cle)
            n = None
        lignes.append({"session_key": cle, "depassements": n, 
                       "date_course": pd.to_datetime(courses["date_start"].iloc[i], utc=True).tz_localize(None).normalize()})
        time.sleep(2)  # OpenF1 limite le nombre de requêtes par minute
    return pd.DataFrame(lignes)

def courses_jolpica(annee):
    rep = get_json(f"https://api.jolpi.ca/ergast/f1/{annee}/results/1.json", {"limit": 100})
    lignes = []
    for c in rep["MRData"]["RaceTable"]["Races"]:
        lignes.append({"circuit_id": c["Circuit"]["circuitId"],
                    "date_course": pd.Timestamp(c["date"]),
                    "tours": int(c["Results"][0]["laps"])})
    return pd.DataFrame(lignes)

def coef_depassement(annees=ANNEE_COEFF):
    tables = []
    for annee in annees:
        print("Dépassements", annee)
        dep = depassement_openf1(annee).astype({"date_course": "datetime64[ns]"})
        cou = courses_jolpica(annee).astype({"date_course": "datetime64[ns]"})
 
        # Jointure sur la date à un jour près
        t = pd.merge_asof(dep.sort_values("date_course"), courses.sort_values("date_course"),
                          on="date_course", direction="nearest",
                          tolerance=pd.Timedelta(days=1))
        assert t["circuit_id"].notna().all(), "course OpenF1 sans circuit Jolpica"
        t["annee"] = annee
        tables.append(t)
 
    courses = pd.concat(tables, ignore_index=True)
    courses["depassements_par_tour"] = courses["depassements"] / courses["tours"]
 
    # Un coefficient par circuit : moyenne sur les éditions disponibles.
    # Plus il est élevé, plus il y a de dépassements (donc plus c'est facile de dépasser).
    coef = (courses.groupby("circuit_id")
            .agg(coef_depassement=("depassements", "mean"),
                 depassement_par_tour=("depassements_par_tour", "mean"),
                 nb_courses=("depassements", "count"))
            .reset_index())
 
    RAW.mkdir(parents=True, exist_ok=True)
    courses.to_parquet(RAW / "depassements_par_course.parquet", index=False)  # détail
    coef.to_parquet(RAW / "coefficients_depassement.parquet", index=False)
    return coef
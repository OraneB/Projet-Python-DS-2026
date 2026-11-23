import json
import time

import pandas as pd
import requests

from src.config import RAW


def get_json(url, params=None):
    # on réessaie 3 fois si l'API ne répond pas
    for essai in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            time.sleep(0.2)  # pour ne pas envoyer trop de requêtes d'un coup
            return r.json()
        except requests.RequestException:
            print("Erreur sur", url, "- nouvel essai dans 5 s")
            time.sleep(5)
    raise RuntimeError("L'API ne répond pas : " + url)


# ---------------- Fonctions polymarkets ----------------

def events_polymarket(annee):
    # Recherche de tous les events "vainqueur du Grand Prix" (20 résultats par page)
    events = []
    page = 1
    while True:
        params = {"q": "grand prix winner", "limit_per_type": 20,
                  "events_status": "closed", "page": page}
        rep = get_json("https://gamma-api.polymarket.com/public-search", params)
        events = events + rep["events"]
        if not rep["pagination"]["hasMore"]:
            break
        page = page + 1

    # On garde la F1, le vainqueur de la course (pas la pole ni le sprint), et la bonne année
    resultat = []
    ids_vus = []
    for e in events:
        titre = e["title"].lower()
        tags = [t["slug"] for t in e["tags"]]
        est_f1 = "f1" in tags or "formula1" in tags
        bon_marche = "winner" in titre and "pole" not in titre and "sprint" not in titre
        if est_f1 and bon_marche and e["endDate"][:4] == str(annee) and e["id"] not in ids_vus:
            resultat.append(e)
            ids_vus.append(e["id"])
    return resultat

#fonction historique qui récupère les prix minute par minute entre debut et fin

def historique_prix(token, debut, fin):
    # L'API ne renvoie pas plus de quelques jours de prix à la minute, pour éviter qu'elle tronque, on découpe en blocs de 3 jours
    points = []
    while debut < fin:
        fin_bloc = min(debut + pd.Timedelta(days=3), fin)
        params = {"market": token, "fidelity": 1,
                  "startTs": int(debut.timestamp()), "endTs": int(fin_bloc.timestamp())}
        rep = get_json("https://clob.polymarket.com/prices-history", params)
        points = points + rep["history"]
        debut = fin_bloc
    return points
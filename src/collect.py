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

#fonction de collecte pour télécharger toutes les données de tous les Grands Prix et les classer entre grand prix, pilote de grand prix et prix gagnés

def collecter_polymarket(annee):
    events = events_polymarket(annee)
    print(len(events), "Grands Prix trouvés")

    liste_events = []
    liste_marches = []
    liste_prix = []
    for e in events:
        liste_events.append({"event_id": e["id"], "title": e["title"].strip(),
                             "volume_usd": float(e["volume"])})

        # un marché par pilote dans chaque GP
        for m in e["markets"]:
            token_yes = json.loads(m["clobTokenIds"])[0]
            debut = pd.Timestamp(m["startDate"])
            cloture = pd.Timestamp(m["closedTime"])
            gagne = json.loads(m["outcomePrices"])[0] == "1"
            liste_marches.append({"event_id": e["id"], "driver": m["groupItemTitle"],
                                  "volume_usd": float(m["volume"]), "closed": cloture,
                                  "won": gagne})

            for p in historique_prix(token_yes, debut, cloture + pd.Timedelta(hours=1)):
                liste_prix.append({"event_id": e["id"], "driver": m["groupItemTitle"],
                                   "t": p["t"], "price": p["p"]})
        print("  ok :", e["title"].strip())

    prix = pd.DataFrame(liste_prix)
    prix["timestamp_utc"] = pd.to_datetime(prix["t"], unit="s", utc=True)
    prix = prix.drop(columns="t")

    RAW.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(liste_events).to_parquet(RAW / "polymarket_f1_events.parquet", index=False)
    pd.DataFrame(liste_marches).to_parquet(RAW / "polymarket_f1_markets.parquet", index=False)
    prix.to_parquet(RAW / "polymarket_f1_prices.parquet", index=False)

# donne le calendrier des séances ie quand ont lieu les qualifs, les courses etc

def collecter_openf1(annee):
    seances = pd.DataFrame(get_json("https://api.openf1.org/v1/sessions", {"year": annee}))
    seances["date_start"] = pd.to_datetime(seances["date_start"], utc=True)
    seances["date_end"] = pd.to_datetime(seances["date_end"], utc=True)
    seances.to_parquet(RAW / "openf1_sessions.parquet", index=False)

# permet de compléter les données d'OpenF1 avec Jolpica qui donne en plus coordonnées GPS et à quel round on en est

def collecter_jolpica(annee):
    rep = get_json(f"https://api.jolpi.ca/ergast/f1/{annee}.json", {"limit": 100})
    lignes = []
    for course in rep["MRData"]["RaceTable"]["Races"]:
        lignes.append({
            "round": int(course["round"]),
            "circuit_id": course["Circuit"]["circuitId"],
            "lat": float(course["Circuit"]["Location"]["lat"]),
            "lon": float(course["Circuit"]["Location"]["long"]),
            "date_course": course["date"],
        })
    pd.DataFrame(lignes).to_parquet(RAW / "jolpica_calendrier.parquet", index=False)

# Stockage (pour simplifier le chargement)

def charger(nom, fonction_collecte=None, annee=None):
    fichier = RAW / nom
    
    # Si le fichier existe déjà, on le charge
    if fichier.exists():
        return pd.read_parquet(fichier)

    # Sinon, on lance la collecte
    if fonction_collecte is None:
        raise FileNotFoundError(fichier)

    fonction_collecte(annee)

    # On charge le fichier qui vient d'être créé
    return pd.read_parquet(fichier)
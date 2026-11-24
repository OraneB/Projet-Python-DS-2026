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


def nom_pilote(intitule): #permet d'uniformiser les noms
    intitule = intitule.lower()
    for cle in PILOTES:
        if cle in intitule:
            return PILOTES[cle]
    return None  # marché de réserve : "Other", "Driver A"...


#fonctions de nettoyage 

def nettoyer_marches(marches): #filtre les marchés et vérifie la cohérence
    marches = marches.copy()
    marches["pilote"] = marches["driver"].apply(nom_pilote)
    print(marches["pilote"].isna().sum(), "marchés de réserve supprimés")
    marches = marches.dropna(subset=["pilote"])
    assert marches.duplicated(["event_id", "pilote"]).sum() == 0 # vérifie que pas de pilote en double dans un GP
    assert (marches.groupby("event_id")["won"].sum() == 1).all() #et que bien un seul vainqueur par GP
    return marches

def nettoyer_prix(prix, marches): #aligner les prix minutes par minute
    prix = prix.merge(marches[["event_id", "driver", "pilote"]], on=["event_id", "driver"])
    prix["timestamp_utc"] = pd.to_datetime(prix["timestamp_utc"], utc=True)
    prix = prix.drop(columns="driver")
    return prix.sort_values("timestamp_utc")



def table_grands_prix(events, marches, seances, calendrier):
## On récupère les horaires des qualifs et de la course de chaque week-end (API OpenF1)

    courses = seances[seances["session_name"] == "Race"].drop_duplicates("meeting_key")
    courses = courses[["meeting_key", "date_start"]].rename(columns={"date_start": "course_debut"})

    qualifs = seances[seances["session_name"] == "Qualifying"].drop_duplicates("meeting_key")
    qualifs = qualifs[["meeting_key", "date_start", "date_end"]]
    qualifs = qualifs.rename(columns={"date_start": "quali_debut", "date_end": "quali_fin"})

    weekends = courses.merge(qualifs, on="meeting_key")
    meetings_sprint = seances.loc[seances["session_name"] == "Sprint", "meeting_key"]
    weekends["sprint"] = weekends["meeting_key"].isin(meetings_sprint)
    ### on associe chaque marché polymarket à la dernière course qui a commencé avant la clôture
    lignes = []
    for event_id, groupe in marches.groupby("event_id"):
        cloture = pd.to_datetime(groupe["closed"], utc=True).min()
        courses_avant = weekends[weekends["course_debut"] <= cloture]
        derniere = courses_avant.sort_values("course_debut").iloc[-1]
        ligne = derniere.to_dict()
        ligne["event_id"] = event_id
        lignes.append(ligne)
    gp = pd.DataFrame(lignes).merge(events, on="event_id")
### On  associe au circuit
    gp["date_course"] = gp["course_debut"].dt.strftime("%Y-%m-%d")
    gp = gp.merge(calendrier, on="date_course", how="left")
    

    assert gp["meeting_key"].duplicated().sum() == 0  
    return gp.sort_values("course_debut").reset_index(drop=True)
 

def probabilites(prix_gp, debut, fin):
    # Probabilité moyenne de chaque pilote entre debut et fin.
    fenetre = prix_gp[(prix_gp["timestamp_utc"] >= debut) & (prix_gp["timestamp_utc"] <= fin)]
    if len(fenetre) == 0:
        return None
    p = fenetre.groupby("pilote")["price"].mean()
    return p / p.sum()

def reaction(prix_gp, quali_debut, quali_fin):
    ### l'heure qui précède les qualifs. après : de 30 à 90 min après la fin
    avant = probabilites(prix_gp, quali_debut - pd.Timedelta(minutes=60), quali_debut)
    apres = probabilites(prix_gp, quali_fin + pd.Timedelta(minutes=30),
                         quali_fin + pd.Timedelta(minutes=90))
    if avant is None or apres is None:
        return np.nan
    ##calcul de la variation
    tableau = pd.concat([avant, apres], axis=1, keys=["avant", "apres"]).fillna(0)
    return (tableau["apres"] - tableau["avant"]).abs().sum() / 2

def reactions(prix, gp):
    # Réaction aux qualifs: utilisation de reaction sur toutes les courses
    gp = gp.copy()
    liste_tv = []
    liste_placebo = []
    for i in range(len(gp)):
        ligne = gp.iloc[i]
        prix_gp = prix[prix["event_id"] == ligne["event_id"]]
        liste_tv.append(reaction(prix_gp, ligne["quali_debut"], ligne["quali_fin"]))
        decalage = pd.Timedelta(hours=12)
        liste_placebo.append(reaction(prix_gp, ligne["quali_debut"] - decalage,
                                      ligne["quali_fin"] - decalage))
    gp["tv"] = liste_tv
    gp["tv_placebo"] = liste_placebo
    return gp
import json
import time
import requests

def get_json(url, params=None):
    # on essaie 3 fois au cas où l'API ne répond pas
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
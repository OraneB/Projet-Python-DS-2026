### Graphiques du rapport
import matplotlib.pyplot as plt
import pandas as pd


def nom_court(titre):
    return titre.replace("F1 ", "").replace(": Driver Winner", "").replace(" Winner", "").replace("Grand Prix", "GP")


def volumes(gp):
    d = gp.sort_values("volume_usd")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.barh(d["title"].apply(nom_court), d["volume_usd"] / 1e6)
    ax.set_xlabel("Volume échangé (millions de dollars)")
    ax.set_title("Volume échangé par Grand Prix sur Polymarket (2025)")
    plt.show()


def prix_autour_qualifs(prix, ligne, n=5):
    # probabilités des n favoris, de 8 h avant à 8 h après les qualifs (zone grise = qualifs)
    debut = ligne["quali_debut"] - pd.Timedelta(hours=8)
    fin = ligne["quali_fin"] + pd.Timedelta(hours=8)
    d = prix[(prix["event_id"] == ligne["event_id"]) & prix["timestamp_utc"].between(debut, fin)]
    d = d.pivot_table(index="timestamp_utc", columns="pilote", values="price").resample("5min").mean()
    favoris = d.mean().nlargest(n).index

    fig, ax = plt.subplots(figsize=(9, 4.5))
    d[favoris].plot(ax=ax)
    ax.axvspan(ligne["quali_debut"], ligne["quali_fin"], color="grey", alpha=0.3, label="Qualifications")
    ax.set_xlabel("Heure (UTC)")
    ax.set_ylabel("Probabilité de victoire")
    ax.set_title(nom_court(ligne["title"]) + " : prix pendant les qualifications")
    ax.legend()
    plt.show()


def reactions_par_gp(gp):
    d = gp.sort_values("tv")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.barh(d["title"].apply(nom_court), d["tv"], label="Réaction aux qualifs")
    ax.scatter(d["tv_placebo"], d["title"].apply(nom_court), color="black", s=12,
               label="Placebo (12 h avant)", zorder=3)
    ax.set_xlabel("Part de la probabilité qui a changé de pilote")
    ax.set_title("Réaction du marché aux qualifications")
    ax.legend()
    plt.show()


def nuage(gp):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(gp["coef_depassement"], gp["tv"])
    for i in range(len(gp)):
        ax.annotate(gp["circuit_id"].iloc[i], (gp["coef_depassement"].iloc[i], gp["tv"].iloc[i]), fontsize=7)
    ax.set_xlabel("Coefficient de dépassement (2020-2024)")
    ax.set_ylabel("Réaction aux qualifs")
    ax.set_title("Réaction du marché selon la facilité de dépassement")
    plt.show()


def carte(gp, colonne, titre):
    import geopandas as gpd

    points = gpd.GeoDataFrame(gp, geometry=gpd.points_from_xy(gp["lon"], gp["lat"]), crs="EPSG:4326")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    try:
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        gpd.read_file(url).plot(ax=ax, color="#eeeeee", edgecolor="#bbbbbb")
    except Exception:
        print("Fond de carte indisponible")
    points.plot(ax=ax, column=colonne, cmap="viridis", markersize=60, legend=True)
    ax.set_axis_off()
    ax.set_title(titre)
    plt.show()

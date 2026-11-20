from pathlib import Path
import pandas as pd

from src.depassement import courses_jolpica, coef_depassement, depassement_openf1

def test_depassement():
    df = depassement_openf1(2024)
        
    #verifie que ça retourne un DataFrame
    assert isinstance(df, pd.DataFrame)

    #verifie que les colonnes attendues sont présentes
    colonnes = ["session_key", "depassements", "date_course"]

    for colonne in colonnes:
        assert colonne in df.columns

    #verifie que les données sont cohérentes
    assert not df.empty
    assert df["session_key"].notna().all()
    assert df["date_course"].notna().all()

    assert (
        df["depassements"].dropna() >= 0
    ).all()


def test_courses():
    df = courses_jolpica(2024)

    #verifie que ça retourne un DataFrame
    assert isinstance(df, pd.DataFrame)

    #verifie que les colonnes attendues sont présentes
    colonnes = ["circuit_id", "date_course", "tours"]

    for colonne in colonnes:
        assert colonne in df.columns

    #verifie que les données sont cohérentes
    assert not df.empty
    assert df["circuit_id"].notna().all()
    assert df["date_course"].notna().all()
    assert (df["tours"] > 0).all()


def test_coef_depassement():
    coef = coef_depassement([2024])

    #verifie que ça retourne un DataFrame
    assert isinstance(coef, pd.DataFrame)

    #verifie que les colonnes attendues sont présentes
    assert "circuit_id" in coef.columns
    assert "coef_depassement" in coef.columns
    assert "depassement_par_tour" in coef.columns
    assert "nb_courses" in coef.columns

    #verifie que le tableau n'est pas vide
    assert not coef.empty

    #vérifie que les deux fichiers ont été créés
    assert Path("data/raw/depassements_par_course.parquet").exists()
    assert Path("data/raw/coefficients_depassement.parquet").exists()

    #verifie qu'on peut relire le fichier des coefficients
    fichier = pd.read_parquet("data/raw/coefficients_depassement.parquet")
    assert not fichier.empty
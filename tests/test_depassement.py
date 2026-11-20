
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.depassement import depassement, courses

def test_depassement():
    df = depassement(2024)
        
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
    df = courses(2024)

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

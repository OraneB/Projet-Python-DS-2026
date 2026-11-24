# Polymarket et qualifications de F1

Projet du cours : *Python pour la data science* (ENSAE 2A, 2026-2027).

Auteurs : Orane Bertout, Stanislas Hanriot et Colombe de Gélis

**Question :** le marché de prédiction Polymarket réagit-il plus fortement aux qualifications de F1 sur les circuits où il est difficile de dépasser ?

Le rapport est le notebook `rapport.ipynb`.

## Données

- [Polymarket](https://polymarket.com) : prix minute par minute des 24 Grands Prix de 2025 ;
- [OpenF1](https://openf1.org) : horaires des séances 2025 et dépassements des courses 2023-2024;
- [Jolpica](https://github.com/jolpica/jolpica-f1) : calendrier et coordonnées des circuits ;

## Organisation

```text
.
├── src/
│   ├── __init__.py              
│   ├── collect.py               # Récupération des données utilisées par la suite
│   ├── config.py                # Variables globales
│   ├── depassement.py           # Calcul du coefficient de dépassement
│   ├── graphiques.py            # Fonctions produisant les différents graphiques
│   └── traitement.py            # Fonctions de traitement des données
├── tests/
│   └── test_depassement.py      # tests sur les fonctions de depassement.py
├── data/raw                     # fichiers parquet des données
├── rapport.ipynb                # rapport du projet
├── requirements.txt        
└── README.md
```

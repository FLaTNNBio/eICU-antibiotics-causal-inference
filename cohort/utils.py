"""
utils.py
Funzioni di utilità generiche.
"""

import pandas as pd
from config import UP


def load(name, usecols=None):
    """
    Carica un CSV con pulizia automatica dei nomi delle colonne.
    """
    try:
        df = pd.read_csv(f"{UP}{name}.csv", usecols=usecols)
        df.columns = df.columns.str.strip().str.lower()
        print(f"  {name}: {len(df):,} righe OK")
        return df
    except FileNotFoundError:
        print(f"  {name}: NON TROVATA")
        return None


def is_therapeutic(treatment_string):
    """
    Determina se un trattamento è un antibiotico terapeutico.
    """
    s = str(treatment_string).lower()
    if "prophylactic" in s:
        return False
    keywords = [
        "therapeutic antibacterials",
        "pulmonary|medications|antibacterials",
        "cardiovascular|other therapies|antibacterials",
    ]
    return any(k in s for k in keywords)


def impute_missing_values(df, numeric_cols, binary_cols):
    """
    Imputa i valori mancanti:
    - Numeriche: mediana (0 se mediana è NaN)
    - Binarie: 0
    """
    df_imp = df.copy()

    for col in numeric_cols:
        if col in df_imp.columns:
            median_val = df_imp[col].median(skipna=True)
            if pd.isna(median_val):
                median_val = 0
            df_imp[col] = df_imp[col].fillna(median_val)

    for col in binary_cols:
        if col in df_imp.columns:
            df_imp[col] = df_imp[col].fillna(0).astype(int)

    return df_imp
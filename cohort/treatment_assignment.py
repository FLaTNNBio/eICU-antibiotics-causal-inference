"""
treatment_assignment.py
Definizione della variabile trattamento A per diverse finestre temporali.
"""

import pandas as pd
from config import WINDOWS 


def assign_treatment(cohort, first_abx, window_minutes):
    """
    Assegna A=1 se il paziente ha ricevuto antibiotico entro la finestra.
    """
    cohort_win = cohort.copy()
    cohort_win = cohort_win.merge(first_abx, on="patientunitstayid", how="left")
    cohort_win["A"] = (
        cohort_win["abx_offset"].notna() &
        (cohort_win["abx_offset"] <= window_minutes)
    ).astype(int)
    return cohort_win


def build_datasets_for_windows(cohort, first_abx, df_x_imp, features_final):
    """
    Genera i dataset finali per tutte le finestre di trattamento.
    """
    results = {}

    for win_label, treat_win in WINDOWS.items():
        print("\n" + "=" * 60)
        print(f"FINESTRA {win_label} — Definizione A (trattamento entro {win_label})")
        print("=" * 60)

        cohort_win = assign_treatment(cohort, first_abx, treat_win)

        df_final = df_x_imp.merge(
            cohort_win[["patientunitstayid", "A"]],
            on="patientunitstayid",
            how="inner"
        )

        final_cols = ["patientunitstayid", "Y", "A"] + features_final
        df_final = df_final[[c for c in final_cols if c in df_final.columns]]

        # Statistiche
        m1 = df_final[df_final["A"] == 1]["Y"].mean() * 100 if df_final["A"].sum() > 0 else 0
        m0 = df_final[df_final["A"] == 0]["Y"].mean() * 100

        print(f"\n  📊 STATISTICHE FINESTRA {win_label}:")
        print(f"  N totale:  {len(df_final):,}")
        print(f"  A=1:       {df_final['A'].sum():,} ({df_final['A'].mean()*100:.1f}%)  mortalita: {m1:.1f}%")
        print(f"  A=0:       {(df_final['A']==0).sum():,} ({(df_final['A']==0).mean()*100:.1f}%)  mortalita: {m0:.1f}%")
        print(f"  Y=1:       {df_final['Y'].sum():,} ({df_final['Y'].mean()*100:.1f}%)")
        print(f"  Differenza grezza: {m1-m0:+.1f}%")

        results[win_label] = {
            "df": df_final,
            "n": len(df_final),
            "n_A1": int(df_final["A"].sum()),
            "n_A0": int((df_final["A"] == 0).sum()),
            "pct_A1": df_final["A"].mean() * 100,
            "m1": m1,
            "m0": m0,
            "naive": m1 - m0,
            "n_features": len(features_final)
        }

    return results
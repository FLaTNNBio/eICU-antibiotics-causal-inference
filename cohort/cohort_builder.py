"""
cohort_builder.py
Selezione e filtraggio della coorte base.
"""

import pandas as pd
from config import UP
from utils import is_therapeutic


def build_base_cohort(patient_df, treatment_df):
    """
    Costruisce la coorte base applicando criteri di inclusione/esclusione.
    """
    print("\n" + "=" * 60)
    print("STEP 2 — Selezione coorte base")
    print("=" * 60)

    flow = []
    N0 = len(patient_df)
    flow.append(("Dataset totale", N0))

    # Primo ricovero in ICU
    cohort = patient_df[patient_df["unitvisitnumber"] == 1].copy()
    flow.append(("Primo ICU stay", len(cohort)))

    # Età >= 18
    cohort["age_num"] = cohort["age"].replace("> 89", "90")
    cohort["age_num"] = pd.to_numeric(cohort["age_num"], errors="coerce")
    cohort = cohort[cohort["age_num"] >= 18]
    flow.append(("Eta >= 18", len(cohort)))

    # Durata ICU >= 4h (240 minuti)
    cohort = cohort[cohort["unitdischargeoffset"] >= 240]
    flow.append(("Durata ICU >= 4h", len(cohort)))

    # Outcome definibile (Alive o Expired)
    cohort = cohort[cohort["hospitaldischargestatus"].isin(["Alive", "Expired"])]
    flow.append(("Y definibile", len(cohort)))

    # Esclusione comfort care (se file disponibile)
    try:
        eol = pd.read_csv(f"{UP}carePlanEOL_csv.gz", usecols=["patientunitstayid"])
        cohort = cohort[~cohort["patientunitstayid"].isin(set(eol["patientunitstayid"]))]
        flow.append(("No comfort care", len(cohort)))
    except FileNotFoundError:
        flow.append(("No comfort care (file mancante)", len(cohort)))

    # Outcome Y
    cohort["Y"] = (cohort["hospitaldischargestatus"] == "Expired").astype(int)

    # Identificazione prima dose di antibiotico terapeutico
    ids_base = set(cohort["patientunitstayid"])
    tc = treatment_df[treatment_df["patientunitstayid"].isin(ids_base)].copy()
    abx = tc[tc["treatmentstring"].apply(is_therapeutic)]

    first_abx = (
        abx.sort_values("treatmentoffset")
        .groupby("patientunitstayid")
        .first()
        .reset_index()[["patientunitstayid", "treatmentoffset"]]
    )
    first_abx.columns = ["patientunitstayid", "abx_offset"]

    # Esclusione antibiotici pre-ICU (offset < 0)
    pre_icu = set(first_abx[first_abx["abx_offset"] < 0]["patientunitstayid"])
    cohort = cohort[~cohort["patientunitstayid"].isin(pre_icu)]
    flow.append(("No abx pre-ICU", len(cohort)))

    # Filtra first_abx per i pazienti rimasti
    ids_final = set(cohort["patientunitstayid"])
    first_abx_valid = first_abx[
        first_abx["patientunitstayid"].isin(ids_final) &
        (first_abx["abx_offset"] >= 0)
    ]

    # Stampa flow chart
    for label, n in flow:
        print(f"  {label:<25} {n:,}")
    print(f"\n  Coorte base (pre-A): {len(cohort):,} pazienti")

    return cohort, first_abx_valid, flow
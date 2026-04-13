"""
covariates_static.py
Estrazione e preparazione delle covariate statiche.
"""

import pandas as pd
from config import ALL_FEATURES, BINARY_FEATURES
from utils import impute_missing_values


def extract_static_covariates(cohort, tables):
    """
    Estrae e aggrega tutte le covariate statiche per la coorte.
    """
    print("\n" + "=" * 60)
    print("STEP 3 — Estrazione covariate X (SOLO STATICHE)")
    print("=" * 60)

    ids_base = set(cohort["patientunitstayid"])

    # DataFrame base
    df_x = cohort[[
        "patientunitstayid", "Y", "age_num",
        "admissionweight", "admissionheight",
        "gender", "hospitalid"
    ]].copy()

    # APACHE Predicted Mortality
    if tables.get("apache_res") is not None:
        ares = (
            tables["apache_res"][tables["apache_res"]["patientunitstayid"].isin(ids_base)]
            .groupby("patientunitstayid")
            .first()
            .reset_index()[["patientunitstayid", "apachescore", "acutephysiologyscore", "predictedhospitalmortality"]]
        )
        df_x = df_x.merge(ares, on="patientunitstayid", how="left")
        print("  APACHE score: OK")

    # APACHE APS
    if tables.get("apache_aps") is not None:
        aps = (
            tables["apache_aps"][tables["apache_aps"]["patientunitstayid"].isin(ids_base)]
            .groupby("patientunitstayid")
            .first()
            .reset_index()
        )
        keep = ["patientunitstayid", "eyes", "motor", "verbal",
                "heartrate", "meanbp", "respiratoryrate", "temperature",
                "ph", "pao2", "fio2", "creatinine", "wbc", "glucose"]
        aps = aps[[c for c in keep if c in aps.columns]].copy()
        if len(aps.columns) > 1:
            aps.columns = ["patientunitstayid"] + [f"aps_{c}" for c in aps.columns[1:]]
            df_x = df_x.merge(aps, on="patientunitstayid", how="left")
        print("  APACHE APS: OK")

    # Diagnosi di ammissione
    if tables.get("adm_dx") is not None:
        adx = tables["adm_dx"][tables["adm_dx"]["patientunitstayid"].isin(ids_base)].copy()
        adx["infective_dx"] = adx["admitdxpath"].str.lower().str.contains(
            "sepsis|infect|pneumon|bacteremia|respiratory", na=False
        ).astype(int)
        adx["cardiac_dx"] = adx["admitdxpath"].str.lower().str.contains(
            "cardiovascular|cardiac|arrhythmia|heart", na=False
        ).astype(int)
        adx["neuro_dx"] = adx["admitdxpath"].str.lower().str.contains(
            "neurolog|coma|seizure|stroke", na=False
        ).astype(int)
        adx_agg = adx.groupby("patientunitstayid").agg(
            infective_dx=("infective_dx", "max"),
            cardiac_dx=("cardiac_dx", "max"),
            neuro_dx=("neuro_dx", "max")
        ).reset_index()
        df_x = df_x.merge(adx_agg, on="patientunitstayid", how="left")
        print("  Diagnosi: OK")

    # Comorbilità APACHE
    if tables.get("apache_pred") is not None:
        apred = (
            tables["apache_pred"][tables["apache_pred"]["patientunitstayid"].isin(ids_base)]
            .groupby("patientunitstayid")
            .first()
            .reset_index()[["patientunitstayid", "diabetes", "aids", "hepaticfailure",
                            "metastaticcancer", "immunosuppression", "cirrhosis", "electivesurgery"]]
        )
        df_x = df_x.merge(apred, on="patientunitstayid", how="left")
        print("  Comorbilità APACHE: OK")

    # Anamnesi
    if tables.get("past_hist") is not None:
        ph = tables["past_hist"][tables["past_hist"]["patientunitstayid"].isin(ids_base)].copy()
        ph["hx_htn"] = ph["pasthistorypath"].str.lower().str.contains("hypertension", na=False).astype(int)
        ph["hx_chf"] = ph["pasthistorypath"].str.lower().str.contains("heart failure|chf", na=False).astype(int)
        ph["hx_copd"] = ph["pasthistorypath"].str.lower().str.contains("copd", na=False).astype(int)
        ph["hx_ckd"] = ph["pasthistorypath"].str.lower().str.contains("renal|kidney", na=False).astype(int)
        ph_agg = ph.groupby("patientunitstayid").agg(
            hx_htn=("hx_htn", "max"),
            hx_chf=("hx_chf", "max"),
            hx_copd=("hx_copd", "max"),
            hx_ckd=("hx_ckd", "max")
        ).reset_index()
        df_x = df_x.merge(ph_agg, on="patientunitstayid", how="left")
        print("  Anamnesi: OK")

    # Ospedale
    if tables.get("hospital") is not None:
        df_x = df_x.merge(tables["hospital"], on="hospitalid", how="left")
        print("  Ospedale: OK")

    # Feature engineering
    df_x["gender_male"] = (df_x["gender"] == "Male").astype(int)
    df_x = df_x.drop(columns=["gender", "hospitalid", "teachingstatus",
                              "numbedscategory", "region"], errors="ignore")

    # Filtra feature effettivamente presenti
    features_final = [f for f in ALL_FEATURES if f in df_x.columns]
    numeric_cols = [f for f in features_final if f not in BINARY_FEATURES]

    # Imputazione
    df_x_imp = impute_missing_values(df_x, numeric_cols, BINARY_FEATURES)

    print(f"\n  Feature statiche disponibili: {len(features_final)}")
    print(f"  Missing residui: {df_x_imp[features_final].isnull().sum().sum()}")

    return df_x_imp, features_final
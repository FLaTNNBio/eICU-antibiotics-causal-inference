"""
data_loader.py
Caricamento di tutte le tabelle necessarie da eICU.
"""

from utils import load   


def load_all_tables():
    """
    Carica tutte le tabelle necessarie per l'analisi.
    """
    print("=" * 60)
    print("STEP 1 — Caricamento tabelle (SOLO covariate statiche)")
    print("=" * 60)

    tables = {}

    tables["patient"] = load(
        "patient",
        ["patientunitstayid", "gender", "age", "hospitalid",
         "hospitaldischargestatus", "unitdischargestatus",
         "unitdischargeoffset", "unitvisitnumber",
         "admissionweight", "admissionheight", "hospitaladmitsource"]
    )

    tables["treatment"] = load(
        "treatment",
        ["patientunitstayid", "treatmentoffset", "treatmentstring"]
    )

    tables["apache_aps"] = load(
        "apacheApsVar",
        ["patientunitstayid", "eyes", "motor", "verbal",
         "heartrate", "meanbp", "respiratoryrate", "temperature",
         "ph", "pao2", "fio2", "creatinine", "wbc", "glucose"]
    )

    tables["apache_pred"] = load(
        "apachePredVar",
        ["patientunitstayid", "diabetes", "aids", "hepaticfailure",
         "metastaticcancer", "immunosuppression", "cirrhosis", "electivesurgery"]
    )

    tables["apache_res"] = load(
        "apachePatientResult",
        ["patientunitstayid", "apachescore", "acutephysiologyscore",
         "predictedhospitalmortality"]
    )

    tables["adm_dx"] = load(
        "admissionDx",
        ["patientunitstayid", "admitdxpath"]
    )

    tables["past_hist"] = load(
        "pastHistory",
        ["patientunitstayid", "pasthistorypath"]
    )

    tables["hospital"] = load(
        "hospital",
        ["hospitalid", "numbedscategory", "teachingstatus", "region"]
    )

    return tables
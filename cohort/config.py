"""
config.py
Costanti e configurazioni globali per il progetto.
"""
import os

# Trova la root del progetto (1 livello sopra src/ se il file è in src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Percorsi assoluti (più robusti dei relativi)
UP = os.path.join(BASE_DIR, "data", "raw") + "/"
OUT_PNG = os.path.join(BASE_DIR, "output_png") + "/"
PROCESSED = os.path.join(BASE_DIR, "data", "processed") + "/"

# Crea le directory se non esistono
os.makedirs(UP, exist_ok=True)
os.makedirs(OUT_PNG, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

# Finestre temporali per i vitali e lab (non usate nella versione statica)
VITAL_WIN = 120
LAB_WIN = 360

# Finestre di trattamento da costruire
WINDOWS = {
    "24h": 24 * 60,
    "12h": 12 * 60,
}

# Lista completa delle feature statiche attese
ALL_FEATURES = [
    "age_num", "gender_male", "admissionweight", "admissionheight",
    "predictedhospitalmortality",
    "aps_eyes", "aps_motor", "aps_verbal",
    "aps_heartrate", "aps_meanbp", "aps_respiratoryrate", "aps_temperature",
    "aps_ph", "aps_pao2", "aps_creatinine", "aps_wbc", "aps_glucose",
    "infective_dx", "cardiac_dx", "neuro_dx",
    "diabetes", "cirrhosis", "hepaticfailure",
    "immunosuppression", "metastaticcancer", "aids",
    "hx_htn", "hx_chf", "hx_copd", "hx_ckd",
]

# Variabili binarie (per imputazione)
BINARY_FEATURES = [
    "gender_male", "infective_dx", "cardiac_dx", "neuro_dx",
    "diabetes", "cirrhosis", "hepaticfailure",
    "immunosuppression", "metastaticcancer", "aids",
    "hx_htn", "hx_chf", "hx_copd", "hx_ckd",
]
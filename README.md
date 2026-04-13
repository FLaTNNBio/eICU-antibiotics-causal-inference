# ⚕️ Inferenza Causale su eICU: Antibiotici Precoci e Mortalità Ospedaliera

Questo repository contiene una pipeline completa per la stima dell'**effetto causale della somministrazione precoce di antibiotici terapeutici sulla mortalità ospedaliera**, utilizzando il database **eICU Collaborative Research Database (versione DEMO)**.

L'analisi è condotta all'interno del framework del **Target Trial Emulation** (Hernán & Robins, 2022), al fine di mitigare i bias tipici degli studi osservazionali su dati sanitari (confondimento da indicazione, immortal time bias).

> **Scelta Metodologica Fondamentale:** Per garantire l'assenza di *data leakage* (time‑zero bias), le covariate di baseline ($X$) sono state costruite **esclusivamente a partire da caratteristiche statiche** del paziente, note al momento del ricovero in Terapia Intensiva. Segni vitali dinamici ed esami di laboratorio sono stati **intenzionalmente esclusi** dal modello di propensity score.

---

## 🎯 Disegno dello Studio

| Componente | Descrizione |
| :--- | :--- |
| **Target Trial** | Effetto degli antibiotici terapeutici entro 24h dal ricovero in ICU rispetto a somministrazione ritardata o assente. |
| **Outcome ($Y$)** | Mortalità ospedaliera (Binaria). |
| **Trattamento ($T$)** | Somministrazione di antibiotici terapeutici entro una finestra temporale predefinita (Primaria: 24h; Sensibilità: 12h). |
| **Covariate ($X$)** | **30 Covariate Statiche** (Demografiche, APACHE Score, Comorbilità, Diagnosi di Ammissione). |
| **Stimando** | Average Treatment Effect (ATE). |
| **Metodi** | Naive, IPW, AIPW, DR Learner (XGBoost), DragonNet. |

---

## 🗂️ Struttura del Repository

```
.
├── cohort/                     # Pipeline di costruzione della coorte
│   ├── config.py               # Percorsi e costanti
│   ├── utils.py                # Funzioni di utilità (caricamento, imputazione)
│   ├── data_loader.py          # Caricamento tabelle eICU raw
│   ├── cohort_builder.py       # Criteri di inclusione/esclusione
│   ├── covariates_static.py    # Estrazione covariate statiche
│   ├── treatment_assignment.py # Definizione di A per finestre 24h e 12h
│   ├── visualization.py        # Grafici di confronto coorti
│   └── main.py                 # Script principale per costruzione coorte
│
├── estimation/                 # Pipeline di stima causale
│   ├── config.py               # Percorsi e impostazioni bootstrap
│   ├── data_loader.py          # Caricamento dataset processato
│   ├── propensity.py           # Modelli di propensity score (LR, XGBoost)
│   ├── outcome_models.py       # Modelli di outcome (μ0, μ1)
│   ├── estimators.py           # Stimatori ATE (Naive, IPW, AIPW, DR)
│   ├── dragonnet.py            # Rete neurale DragonNet
│   ├── bootstrap.py            # Intervalli di confidenza bootstrap
│   └── main.py                 # Script principale per stima causale
│
├── notebooks/                  # Analisi esplorative (opzionale)
├── output_png/                 # Grafici generati
├── data/
│   ├── raw/                    # File CSV originali eICU (NON tracciati)
│   └── processed/              # Dataset analitici generati
├── .gitignore
├── LICENSE
└── README.md
```
---

## 📥 Download dei Dati

I dati raw eICU **non** sono inclusi in questo repository per limiti di dimensione e vincoli di licenza.

1. Richiedi l'accesso al [eICU Collaborative Research Database DEMO](https://physionet.org/content/eicu-crd-demo/2.0.1/) su PhysioNet.
2. Scarica i file CSV.
3. Inseriscili nella cartella `data/raw/`.

**File necessari:**
- `patient.csv`
- `treatment.csv`
- `apacheApsVar.csv`
- `apachePatientResult.csv`
- `apachePredVar.csv`
- `admissionDx.csv`
- `pastHistory.csv`
- `hospital.csv`
- `carePlanEOL.csv.gz` (opzionale)

---

## 🛠️ Installazione e Setup

### 1. Clona il repository
```bash
git clone https://github.com/FLaTNNBio/eICU-antibiotics-causal-inference.git
cd eICU-antibiotics-causal-inference
```

### 2. Crea un ambiente virtuale
```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa le dipendenze
```bash
pip install -r requirements.txt
```

**Dipendenze principali:**
- `pandas`, `numpy` — Manipolazione dati
- `scikit-learn` — Regressione logistica, preprocessing
- `xgboost` — DR Learner
- `tensorflow` — DragonNet
- `matplotlib` — Visualizzazione

---

## 🚀 Utilizzo

### Step 1: Costruzione della Coorte

```bash
python cohort/main.py
```

**Output:**
- `data/processed/dataset_XAY_24h_static.csv` — Finestra primaria (24h)
- `data/processed/dataset_XAY_12h_static.csv` — Finestra di sensibilità (12h)
- `output_png/sensitivity_24h_vs_12h_STATIC_ONLY.png` — Grafico di confronto coorti

### Step 2: Stima degli Effetti Causali

```bash
python estimation/main.py
```

**Output:**
- Stime puntuali dell'ATE (Naive, IPW, AIPW, DR, DragonNet)
- Intervalli di confidenza bootstrap al 95%
- Tabella riassuntiva nella console

---

## 📊 Covariate di Baseline (n=30)

| Categoria | Variabili |
| :--- | :--- |
| **Demografia** | Età, Genere, Peso, Altezza |
| **APACHE Score** | Predicted Hospital Mortality, componenti APS (GCS, vitali, lab) |
| **Diagnosi di Ammissione** | Infettiva, Cardiaca, Neurologica |
| **Comorbilità Croniche** | Diabete, Cirrosi, Insufficienza Epatica, Immunodepressione, Cancro Metastatico, AIDS |
| **Anamnesi Remota** | Ipertensione, Scompenso Cardiaco, BPCO, Insufficienza Renale Cronica |

---

## 📈 Esempio di Output

```
============================================================
RIEPILOGO FINALE
============================================================

  Coorte:  1980 paz.  |  A=1: 377  |  Y=1: 160
  AUC PS (logistic): 0.723

  Metodo         ATE         CI 95%                        Sig.
  ─────────────────────────────────────────────────────────────
  Naive          +3.8%       —                             (non causale)
  IPW            -1.2%       [-4.5%, +2.1%]                NON sign.
  AIPW           -0.8%       [-3.9%, +2.3%]                NON sign.
  DR (XGBoost)   -0.5%       [-3.2%, +2.2%]                NON sign.
  DragonNet      -1.0%       [-4.1%, +2.1%]                NON sign.
```

---

## ⚠️ Limiti dello Studio

- **Confondimento Residuo:** L'esclusione di vitali e lab dal baseline, sebbene necessaria per prevenire il data leakage, potrebbe non catturare completamente la gravità acuta del paziente.
- **Dimensione Campionaria:** Il dataset DEMO limita la potenza statistica e le analisi di sottogruppo.

---

## 📚 Riferimenti

- Hernán, M. A., & Robins, J. M. (2022). *Causal Inference: What If*. Chapman & Hall/CRC.
- Pollard, T. J., et al. (2018). The eICU Collaborative Research Database. *Scientific Data*.
- Shi, C., et al. (2019). *Adapting Neural Networks for the Estimation of Treatment Effects*. NeurIPS.

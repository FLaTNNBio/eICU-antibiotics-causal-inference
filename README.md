# ⚕️ Inferenza Causale su eICU: Antibiotici Precoci e Mortalità Ospedaliera

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📖 Panoramica

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
├── src/                        # Codice per stima causale
│   ├── causalforge/            # Mini-framework per inferenza causale
│   │   ├── __init__.py
│   │   ├── model.py            # Classi base per modelli causali
│   │   ├── models/             # Implementazioni specifiche
│   │   │   ├── __init__.py
│   │   │   └── dragonnet.py    # Rete neurale DragonNet
│   │   └── utils.py            # Funzioni di supporto
│   └── dragonnet_eicu.py       # Script principale per stima ATE
│
├── notebooks/                  # Analisi esplorative (opzionale)
├── output_png/                 # Grafici generati
├── data/
│   ├── raw/                    # File CSV originali eICU (NON tracciati)
│   └── processed/              # Dataset analitici generati
├── .gitignore
├── .vscode/                    # Configurazioni Visual Studio Code
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
- `carePlanEOL.csv.gz`

---

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
python src/dragonnet_eicu.py
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

## 📈 Risultati Principali (Seed 42)

Stima dell'Effetto Causale (ATE) degli Antibiotici Precoci sulla Mortalità Ospedaliera.

| Metodo | ATE (%) | IC 95% (%) | Interpretazione |
|:-------|:-------:|:-----------|:----------------|
| **Naive (Greggio)** | +3.54% | — | Risultato fuorviante (confondimento) |
| **IPW** | +0.07% | [-2.85%, +4.45%] | Effetto nullo |
| **AIPW** | +0.14% | [-3.46%, +2.96%] | Conferma effetto nullo (doubly robust) |
| **DR Learner (XGBoost)** | +1.23% | [-0.86%, +4.47%] | Coerente con IPW/AIPW |
| **DragonNet** | -1.86% | [-59.17%, +71.60%] | Instabile su dataset piccolo |

### 🔍 Interpretazione

- **Naive vs. IPW/AIPW:** Il dato grezzo (+3.54%) suggerirebbe che gli antibiotici *aumentano* la mortalità. Tuttavia, dopo correzione per il confondimento (i pazienti trattati sono intrinsecamente più gravi), l'effetto **scompare completamente** (~0%). Questo è un classico esempio di **confounding by indication**.

- **IPW e AIPW concordano:** Entrambi gli stimatori robusti indicano un effetto **nullo** (gli intervalli di confidenza includono lo 0). L'AIPW, essendo *doubly robust*, fornisce una conferma della solidità del risultato.

- **DragonNet:** Su un dataset di soli 1,980 pazienti, la rete neurale profonda risulta **sovradimensionata** e instabile, producendo un intervallo di confidenza eccessivamente ampio. Questo evidenzia i limiti del deep learning su campioni di piccole dimensioni.

- **DR Learner (XGBoost):** Offre un buon compromesso tra flessibilità e stabilità, con un intervallo di confidenza più stretto e coerente con i metodi classici.

---

## ⚠️ Limiti dello Studio

- **Confondimento Residuo:** L'esclusione di vitali e lab dal baseline, sebbene necessaria per prevenire il data leakage, potrebbe non catturare completamente la gravità acuta del paziente.
- **Dimensione Campionaria:** Il dataset DEMO (n=1,980) limita la potenza statistica e la possibilità di condurre analisi di sottogruppo. Modelli complessi come DragonNet soffrono di instabilità.
- **Generalizzabilità:** I risultati si riferiscono al dataset DEMO e potrebbero non essere rappresentativi dell'intero database eICU.

---

## 📚 Riferimenti

- Hernán, M. A., & Robins, J. M. (2022). *Causal Inference: What If*. Chapman & Hall/CRC.
- Pollard, T. J., et al. (2018). The eICU Collaborative Research Database. *Scientific Data*.
- Shi, C., et al. (2019). *Adapting Neural Networks for the Estimation of Treatment Effects*. NeurIPS.

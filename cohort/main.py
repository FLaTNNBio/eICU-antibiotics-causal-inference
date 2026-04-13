"""
main.py
Script principale per l'esecuzione completa della pipeline.
"""

import warnings
import os
import sys

warnings.filterwarnings("ignore")

from config import PROCESSED, OUT_PNG
from data_loader import load_all_tables
from cohort_builder import build_base_cohort
from covariates_static import extract_static_covariates
from treatment_assignment import build_datasets_for_windows
from visualization import plot_comparison


def check_data_folder():
    """Verifica che la cartella data/raw esista e contenga i file necessari."""
    from config import UP
    
    if not os.path.exists(UP):
        print(f"❌ ERRORE: La cartella {UP} non esiste.")
        print(f"   Directory corrente: {os.getcwd()}")
        return False
    
    required_files = ["patient.csv", "treatment.csv"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(UP, f))]
    
    if missing:
        print(f"❌ ERRORE: File mancanti in {UP}:")
        for f in missing:
            print(f"   - {f}")
        print("\n   Scarica i file eICU DEMO da PhysioNet e inseriscili in data/raw/")
        return False
    
    print(f"✅ Cartella {UP} verificata correttamente.")
    return True


def save_datasets(results):
    """Salva i dataset finali su disco."""
    for win_label, res in results.items():
        out_path = os.path.join(PROCESSED, f"dataset_XAY_{win_label}_static.csv")
        res["df"].to_csv(out_path, index=False)
        print(f"  💾 Salvato: {out_path}")


def print_final_summary(results):
    """Stampa il riepilogo finale."""
    print("\n" + "=" * 60)
    print("RIEPILOGO FINALE — BASELINE STATICO (Zero Leakage)")
    print("=" * 60)
    print(f"  Feature statiche incluse: {results['24h']['n_features']}")
    print()
    print(f"  {'':30} {'24h':>10}  {'12h':>10}")
    print("  " + "─" * 52)
    print(f"  {'N totale':<30} {results['24h']['n']:>10,}  {results['12h']['n']:>10,}")
    print(f"  {'A=1 (trattati)':<30} {results['24h']['n_A1']:>10,}  {results['12h']['n_A1']:>10,}")
    print(f"  {'% trattati':<30} {results['24h']['pct_A1']:>9.1f}%  {results['12h']['pct_A1']:>9.1f}%")
    print(f"  {'Mortalità A=1':<30} {results['24h']['m1']:>9.1f}%  {results['12h']['m1']:>9.1f}%")
    print(f"  {'Mortalità A=0':<30} {results['24h']['m0']:>9.1f}%  {results['12h']['m0']:>9.1f}%")
    print(f"  {'Diff. grezza (naive ATE)':<30} {results['24h']['naive']:>+9.1f}%  {results['12h']['naive']:>+9.1f}%")
    print()
    print("  ✅ ZERO DATA LEAKAGE GARANTITO (solo covariate statiche)")
    print("  ⚠️ Nota: vitali e lab ESCLUSI dal baseline per rigore metodologico")


def main():
    """Funzione principale."""
    
    # Verifica cartella dati
    if not check_data_folder():
        sys.exit(1)
    
    print()
    
    # Step 1: Caricamento tabelle
    tables = load_all_tables()
    
    if tables.get("patient") is None:
        print("❌ ERRORE: Impossibile caricare patient.csv. Verifica il file.")
        sys.exit(1)

    # Step 2: Costruzione coorte base
    cohort, first_abx, flow = build_base_cohort(
        tables["patient"],
        tables["treatment"]
    )

    # Step 3: Estrazione covariate statiche
    df_x_imp, features_final = extract_static_covariates(cohort, tables)

    # Step 4: Costruzione dataset per finestre temporali
    results = build_datasets_for_windows(cohort, first_abx, df_x_imp, features_final)

    # Salvataggio dataset
    save_datasets(results)

    # Step 5: Visualizzazione
    plot_comparison(results)

    # Riepilogo finale
    print_final_summary(results)


if __name__ == "__main__":
    main()
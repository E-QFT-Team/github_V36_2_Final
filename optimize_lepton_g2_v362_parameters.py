"""
optimize_lepton_g2_v362_parameters.py

Script d'optimisation des paramètres de calibration pour LeptonG2CanonicalV362Fixed.
Ce script teste systématiquement différentes valeurs de δa_NF dans les plages spécifiées
pour trouver les valeurs optimales qui atteignent les cibles désirées.

Cibles :
- Muon : δa_μ^NF ∈ [5.0×10⁻¹⁰, 6.5×10⁻¹⁰] pour a_μ^BSM ≈ 2.51×10⁻⁹, significance ~0.00σ
- Électron : δa_e^NF ∈ [9.0×10⁻¹⁸, 1.1×10⁻¹⁷] pour a_e^BSM ≈ 4.85×10⁻¹⁷, significance ~0.11σ
- Tau : δa_τ^NF ∈ [-6.0×10⁻⁶, -5.5×10⁻⁶] pour a_τ^BSM ≈ -2.22×10⁻⁸
"""

import numpy as np
import logging
import matplotlib.pyplot as plt
import json
from datetime import datetime
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Valeurs cibles et plages à explorer
TARGETS = {
    "muon": {
        "a_bsm_target": 2.51e-9,
        "significance_target": 0.00,
        "range": [5.0e-10, 6.5e-10],
        "steps": 20
    },
    "electron": {
        "a_bsm_target": 4.85e-17,
        "significance_target": 0.11,
        "range": [9.0e-18, 1.1e-17],
        "steps": 20
    },
    "tau": {
        "a_bsm_target": -2.22e-8,
        "range": [-6.0e-6, -5.5e-6],
        "steps": 20
    }
}

def evaluate_parameter(calculator, lepton, param_value):
    """
    Évalue un paramètre δa_NF spécifique pour un lepton donné.
    
    Args:
        calculator: Instance de LeptonG2CanonicalV362Fixed
        lepton: Type de lepton ("electron", "muon", "tau")
        param_value: Valeur du paramètre δa_NF à tester
        
    Returns:
        Dictionnaire avec les résultats de l'évaluation
    """
    # Sauvegarder la valeur actuelle
    original_value = calculator.delta_a_nf[lepton]
    
    # Définir la nouvelle valeur
    calculator.delta_a_nf[lepton] = param_value
    
    # Calculer les résultats
    results = calculator.calculate_significance(lepton)
    
    # Restaurer la valeur originale
    calculator.delta_a_nf[lepton] = original_value
    
    # Calculer les métriques d'optimisation
    metrics = {
        "delta_a_nf": param_value,
        "a_bsm": results["a_lepton_eqft"],
        "significance": results["significance"]
    }
    
    # Calculer les erreurs par rapport aux cibles
    if lepton in TARGETS:
        if "a_bsm_target" in TARGETS[lepton]:
            metrics["a_bsm_error"] = abs(results["a_lepton_eqft"] - TARGETS[lepton]["a_bsm_target"])
            metrics["a_bsm_error_pct"] = 100 * abs(results["a_lepton_eqft"] - TARGETS[lepton]["a_bsm_target"]) / abs(TARGETS[lepton]["a_bsm_target"])
        
        if "significance_target" in TARGETS[lepton] and results["significance"] is not None:
            metrics["significance_error"] = abs(results["significance"] - TARGETS[lepton]["significance_target"])
    
    return metrics

def optimize_parameter(lepton):
    """
    Optimise le paramètre δa_NF pour un lepton donné.
    
    Args:
        lepton: Type de lepton ("electron", "muon", "tau")
        
    Returns:
        Tuple avec (valeur optimale, résultats d'évaluation pour toutes les valeurs testées)
    """
    calculator = LeptonG2CanonicalV362Fixed()
    
    # Définir la plage de valeurs à tester
    param_range = TARGETS[lepton]["range"]
    steps = TARGETS[lepton]["steps"]
    values_to_test = np.linspace(param_range[0], param_range[1], steps)
    
    logger.info(f"Optimizing δa_NF for {lepton} in range {param_range[0]:.6e} to {param_range[1]:.6e} with {steps} steps")
    
    # Évaluer chaque valeur
    all_results = []
    for val in values_to_test:
        metrics = evaluate_parameter(calculator, lepton, val)
        all_results.append(metrics)
        
        # Log détaillé
        log_msg = f"  δa_{lepton[0]}^NF = {val:.6e} → a_{lepton[0]}^BSM = {metrics['a_bsm']:.6e}"
        if "significance" in metrics and metrics["significance"] is not None:
            log_msg += f", sig = {metrics['significance']:.4f}σ"
        if "a_bsm_error_pct" in metrics:
            log_msg += f", err = {metrics['a_bsm_error_pct']:.4f}%"
        logger.info(log_msg)
    
    # Trouver la valeur optimale selon le critère approprié
    if lepton in ["electron", "muon"]:
        # Pour l'électron et le muon, optimiser pour minimiser une combinaison d'erreurs
        # Pondérer les erreurs de a_BSM et de significance
        for result in all_results:
            if "a_bsm_error" in result and "significance_error" in result:
                # Normaliser les erreurs et les combiner
                result["combined_error"] = (
                    0.7 * result["a_bsm_error_pct"] + 
                    0.3 * result["significance_error"] * 100
                )
            else:
                result["combined_error"] = float('inf')
        
        # Trier par erreur combinée
        all_results.sort(key=lambda x: x["combined_error"])
    else:
        # Pour le tau, qui n'a pas de mesure de significance, optimiser uniquement pour a_BSM
        all_results.sort(key=lambda x: x["a_bsm_error"])
    
    # La meilleure valeur est la première après le tri
    best_result = all_results[0]
    best_value = best_result["delta_a_nf"]
    
    logger.info(f"Best δa_{lepton[0]}^NF = {best_value:.6e} → a_{lepton[0]}^BSM = {best_result['a_bsm']:.6e}")
    if "significance" in best_result and best_result["significance"] is not None:
        logger.info(f"  Significance = {best_result['significance']:.4f}σ")
    
    return best_value, all_results

def plot_optimization_results(lepton, results):
    """
    Génère un graphique des résultats d'optimisation.
    
    Args:
        lepton: Type de lepton ("electron", "muon", "tau")
        results: Liste des résultats d'évaluation
    """
    # Extraire les données
    delta_a_values = [r["delta_a_nf"] for r in results]
    a_bsm_values = [r["a_bsm"] for r in results]
    
    # Créer une figure avec deux sous-graphiques
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Graphique pour a_BSM
    ax1.plot(delta_a_values, a_bsm_values, 'o-', color='blue')
    ax1.set_ylabel(f'a_{lepton[0]}^BSM')
    ax1.set_title(f'Optimisation de δa_{lepton[0]}^NF')
    ax1.grid(True)
    
    # Ajouter une ligne horizontale pour la valeur cible de a_BSM
    if "a_bsm_target" in TARGETS[lepton]:
        ax1.axhline(y=TARGETS[lepton]["a_bsm_target"], color='r', linestyle='--', alpha=0.7)
        ax1.text(delta_a_values[0], TARGETS[lepton]["a_bsm_target"], 
                 f' Cible: {TARGETS[lepton]["a_bsm_target"]:.2e}', 
                 va='center', ha='left', backgroundcolor='w', alpha=0.7)
    
    # Graphique pour significance (si applicable)
    if lepton in ["electron", "muon"]:
        significance_values = [r["significance"] for r in results]
        ax2.plot(delta_a_values, significance_values, 'o-', color='green')
        ax2.set_ylabel('Significance (σ)')
        ax2.set_xlabel(f'δa_{lepton[0]}^NF')
        ax2.grid(True)
        
        # Ajouter une ligne horizontale pour la valeur cible de significance
        if "significance_target" in TARGETS[lepton]:
            ax2.axhline(y=TARGETS[lepton]["significance_target"], color='r', linestyle='--', alpha=0.7)
            ax2.text(delta_a_values[0], TARGETS[lepton]["significance_target"], 
                     f' Cible: {TARGETS[lepton]["significance_target"]:.2f}σ', 
                     va='center', ha='left', backgroundcolor='w', alpha=0.7)
    else:
        # Pour tau, montrer l'erreur relative par rapport à la cible a_BSM
        error_values = [abs(r["a_bsm"] - TARGETS[lepton]["a_bsm_target"]) / abs(TARGETS[lepton]["a_bsm_target"]) * 100 for r in results]
        ax2.plot(delta_a_values, error_values, 'o-', color='orange')
        ax2.set_ylabel('Erreur relative (%)')
        ax2.set_xlabel(f'δa_{lepton[0]}^NF')
        ax2.grid(True)
    
    # Ajuster la mise en page et enregistrer
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'results/lepton_g2_v362_{lepton}_optimization_{timestamp}.png')
    plt.close()

def save_results(optimization_results):
    """
    Enregistre les résultats d'optimisation dans un fichier JSON.
    
    Args:
        optimization_results: Dictionnaire avec les résultats d'optimisation
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'results/lepton_g2_v362_optimization_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(optimization_results, f, indent=2)
    
    logger.info(f"Results saved to {filename}")
    
    # Créer également un rapport lisible
    report_filename = f'results/lepton_g2_v362_optimization_report_{timestamp}.md'
    
    with open(report_filename, 'w') as f:
        f.write(f"# Rapport d'optimisation des paramètres V36.2 corrigés\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Résultats de l'optimisation\n\n")
        f.write("| Lepton | δa_ℓ^NF optimal | a_ℓ^BSM | Significance |\n")
        f.write("|--------|----------------|---------|-------------|\n")
        
        for lepton, results in optimization_results.items():
            best_result = results["best_result"]
            f.write(f"| {lepton.capitalize()} | {best_result['delta_a_nf']:.6e} | {best_result['a_bsm']:.6e} | ")
            
            if "significance" in best_result and best_result["significance"] is not None:
                f.write(f"{best_result['significance']:.4f}σ |\n")
            else:
                f.write("N/A |\n")
        
        f.write("\n## Cibles expérimentales\n\n")
        for lepton, target in TARGETS.items():
            f.write(f"### {lepton.capitalize()}\n")
            f.write(f"- Plage de δa_{lepton[0]}^NF : [{target['range'][0]:.6e}, {target['range'][1]:.6e}]\n")
            f.write(f"- a_{lepton[0]}^BSM cible : {target['a_bsm_target']:.6e}\n")
            
            if "significance_target" in target:
                f.write(f"- Significance cible : {target['significance_target']:.2f}σ\n")
            
            f.write("\n")
    
    logger.info(f"Report saved to {report_filename}")

def update_implementation(calculator, optimal_values):
    """
    Met à jour l'implémentation avec les valeurs optimales.
    
    Args:
        calculator: Instance de LeptonG2CanonicalV362Fixed
        optimal_values: Dictionnaire avec les valeurs optimales par lepton
    """
    # Mettre à jour les valeurs
    for lepton, value in optimal_values.items():
        calculator.delta_a_nf[lepton] = value
    
    # Tester les résultats finaux
    results = {}
    for lepton in ["electron", "muon", "tau"]:
        results[lepton] = calculator.calculate_significance(lepton)
    
    # Afficher un résumé
    print("\n=== RÉSULTATS FINAUX AVEC PARAMÈTRES OPTIMISÉS ===")
    for lepton, result in results.items():
        symbol = lepton[0]
        if lepton == "muon":
            symbol = "μ"
        elif lepton == "tau":
            symbol = "τ"
            
        print(f"- {lepton.capitalize()}: δa_{symbol}^NF = {calculator.delta_a_nf[lepton]:.6e}")
        print(f"  a_{symbol}^BSM = {result['a_lepton_eqft']:.6e}")
        
        if result['significance'] is not None:
            print(f"  Significance = {result['significance']:.4f}σ\n")
        else:
            print("")

def main():
    """
    Fonction principale exécutant l'optimisation pour tous les leptons.
    """
    logger.info("Starting optimization of V36.2 correction parameters")
    
    optimization_results = {}
    optimal_values = {}
    
    # Optimiser chaque lepton
    for lepton in ["muon", "electron", "tau"]:
        logger.info(f"\n=== OPTIMIZING {lepton.upper()} ===")
        best_value, all_results = optimize_parameter(lepton)
        
        # Stocker les résultats
        optimization_results[lepton] = {
            "best_value": best_value,
            "best_result": next(r for r in all_results if r["delta_a_nf"] == best_value),
            "all_results": all_results
        }
        
        optimal_values[lepton] = best_value
        
        # Générer un graphique
        plot_optimization_results(lepton, all_results)
    
    # Sauvegarder tous les résultats
    save_results(optimization_results)
    
    # Mettre à jour et tester l'implémentation avec les valeurs optimales
    calculator = LeptonG2CanonicalV362Fixed()
    update_implementation(calculator, optimal_values)
    
    logger.info("Optimization completed successfully!")

if __name__ == "__main__":
    main()
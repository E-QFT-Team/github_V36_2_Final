"""
verify_lepton_g2_v362_fixed.py

Script de vérification finale de l'implémentation corrigée et optimisée de V36.2.
Confirme que les valeurs calibrées produisent exactement les résultats attendus.
"""

import numpy as np
import time
import json
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

def main():
    """
    Vérifie que l'implémentation corrigée et optimisée produit les résultats attendus.
    """
    print("\n=== VÉRIFICATION FINALE DE L'IMPLÉMENTATION V36.2 CORRIGÉE ===")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Instantier le calculateur
    calculator = LeptonG2CanonicalV362Fixed()
    
    # Valeurs attendues
    expected = {
        "electron": {
            "a_bsm": 4.85e-17,
            "significance": 0.11
        },
        "muon": {
            "a_bsm": 2.51e-9,
            "significance": 0.00
        },
        "tau": {
            "a_bsm": -2.22e-8
        }
    }
    
    # Vérifier chaque lepton
    results = {}
    for lepton in ["electron", "muon", "tau"]:
        result = calculator.calculate_significance(lepton)
        results[lepton] = result
        
        # En-tête
        print(f"\n## {lepton.upper()}")
        
        # Paramètres de calibration
        print(f"δa_{lepton[0]}^NF = {calculator.delta_a_nf[lepton]:.6e}")
        
        # Paramètres topologiques
        print(f"Facteur de recouvrement Ω_sym = {result['omega_sym']:.6f}")
        print(f"Classe de Chern c₂ = {result['c2']:.6f}")
        print(f"Facteur topologique λ = {result['lambda_topo']:.6f}")
        
        # Résultats
        print(f"a_{lepton[0]}^BSM = {result['a_lepton_eqft']:.6e}")
        
        # Vérifier par rapport aux attentes
        if "a_bsm" in expected[lepton]:
            error = abs(result['a_lepton_eqft'] - expected[lepton]['a_bsm']) / abs(expected[lepton]['a_bsm']) * 100
            print(f"Erreur relative = {error:.4f}% (cible: {expected[lepton]['a_bsm']:.2e})")
        
        if "significance" in expected[lepton] and result['significance'] is not None:
            error = abs(result['significance'] - expected[lepton]['significance'])
            print(f"Significance = {result['significance']:.6f}σ (cible: {expected[lepton]['significance']:.2f}σ, erreur: {error:.6f})")
    
    # Afficher le rapport détaillé
    print("\n## RAPPORT DÉTAILLÉ")
    
    # Rapport pour le muon
    print(calculator.generate_report("muon"))
    
    # Rapport pour l'électron
    print(calculator.generate_report("electron"))
    
    # Enregistrer les résultats dans un fichier JSON
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {
            "electron": calculator.delta_a_nf["electron"],
            "muon": calculator.delta_a_nf["muon"],
            "tau": calculator.delta_a_nf["tau"]
        },
        "results": {
            "electron": {
                "a_bsm": results["electron"]["a_lepton_eqft"],
                "significance": results["electron"]["significance"]
            },
            "muon": {
                "a_bsm": results["muon"]["a_lepton_eqft"],
                "significance": results["muon"]["significance"]
            },
            "tau": {
                "a_bsm": results["tau"]["a_lepton_eqft"]
            }
        },
        "expected": expected,
        "errors": {
            "electron": {
                "a_bsm": abs(results["electron"]["a_lepton_eqft"] - expected["electron"]["a_bsm"]) / abs(expected["electron"]["a_bsm"]) * 100,
                "significance": abs(results["electron"]["significance"] - expected["electron"]["significance"])
            },
            "muon": {
                "a_bsm": abs(results["muon"]["a_lepton_eqft"] - expected["muon"]["a_bsm"]) / abs(expected["muon"]["a_bsm"]) * 100,
                "significance": abs(results["muon"]["significance"] - expected["muon"]["significance"])
            },
            "tau": {
                "a_bsm": abs(results["tau"]["a_lepton_eqft"] - expected["tau"]["a_bsm"]) / abs(expected["tau"]["a_bsm"]) * 100
            }
        }
    }
    
    # Enregistrer le rapport final
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"results/v362_fixed_verification_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nRésultats enregistrés dans {filename}")
    
    # Vérification finale
    all_valid = True
    
    for lepton in ["electron", "muon", "tau"]:
        if "a_bsm" in expected[lepton]:
            error = abs(results[lepton]["a_lepton_eqft"] - expected[lepton]["a_bsm"]) / abs(expected[lepton]["a_bsm"]) * 100
            if error > 2.0:  # Plus de 2% d'erreur
                all_valid = False
        
        if "significance" in expected[lepton] and results[lepton]["significance"] is not None:
            error = abs(results[lepton]["significance"] - expected[lepton]["significance"])
            if error > 0.1:  # Plus de 0.1σ d'erreur
                all_valid = False
    
    if all_valid:
        print("\n✓ VÉRIFICATION RÉUSSIE : Tous les résultats sont conformes aux attentes.")
    else:
        print("\n⚠ ATTENTION : Certains résultats s'écartent des valeurs attendues.")

if __name__ == "__main__":
    main()
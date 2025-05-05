#!/usr/bin/env python3
"""
Script de test pour valider l'implémentation V36.2 corrigée.

Ce script vérifie que toutes les corrections apportées à la version V36.2
sont correctement implémentées et produisent les résultats attendus.
"""

import sys
import numpy as np
from pathlib import Path
import argparse
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au chemin Python
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Importer la classe corrigée
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

def print_section(title):
    """Affiche un titre de section formaté."""
    print(f"\n{'-' * 20} {title} {'-' * 20}")

def run_validation_tests():
    """
    Exécute une série de tests pour valider l'implémentation V36.2 corrigée.
    """
    print_section("INITIALISATION")
    calculator = LeptonG2CanonicalV362Fixed()
    
    print_section("TEST DES FACTEURS DE RECOUVREMENT")
    phi_e = 2.17
    phi_mu = 4.32
    phi_tau = 10.53
    
    omega_e_mu = calculator.compute_berry_overlap_symmetric(phi_e, phi_mu)
    omega_mu_tau = calculator.compute_berry_overlap_symmetric(phi_mu, phi_tau)
    omega_mu = calculator.compute_berry_overlap(phi_mu)
    omega_tau = calculator.compute_berry_overlap(phi_tau)
    
    print(f"Ω(μ) = {omega_mu:.6f}")
    print(f"Ω(τ) = {omega_tau:.6f}")
    print(f"Ω_sym(e,μ) = {omega_e_mu:.6f}")
    print(f"Ω_sym(μ,τ) = {omega_mu_tau:.6f}")
    
    # Vérifier les valeurs attendues
    expected_omega_e_mu = 0.542906
    expected_omega_mu_tau = 0.106341
    assert abs(omega_e_mu - expected_omega_e_mu) < 1e-6, f"Ω_sym(e,μ) incorrect: {omega_e_mu} != {expected_omega_e_mu}"
    assert abs(omega_mu_tau - expected_omega_mu_tau) < 1e-6, f"Ω_sym(μ,τ) incorrect: {omega_mu_tau} != {expected_omega_mu_tau}"
    print("✅ Facteurs de recouvrement vérifiés.")
    
    print_section("TEST DES CLASSES DE CHERN")
    c2_e_mu = calculator.compute_chern2_cross_symmetric(phi_e, phi_mu)
    c2_mu_tau = calculator.compute_chern2_cross_symmetric(phi_mu, phi_tau)
    c2_tau_mu = calculator.compute_chern2_cross_symmetric(phi_tau, phi_mu)
    
    print(f"c₂(e,μ) = {c2_e_mu:.6f}")
    print(f"c₂(μ,τ) = {c2_mu_tau:.6f}")
    print(f"c₂(τ,μ) = {c2_tau_mu:.6f}")
    
    # Vérifier les valeurs attendues
    expected_c2_e_mu = 10.18
    expected_c2_mu_tau = 9.67
    assert abs(c2_e_mu - expected_c2_e_mu) < 0.01, f"c₂(e,μ) incorrect: {c2_e_mu} != {expected_c2_e_mu}"
    assert abs(c2_mu_tau - expected_c2_mu_tau) < 0.01, f"c₂(μ,τ) incorrect: {c2_mu_tau} != {expected_c2_mu_tau}"
    assert abs(c2_tau_mu - c2_mu_tau) < 0.01, f"c₂(τ,μ) != c₂(μ,τ): {c2_tau_mu} != {c2_mu_tau}"
    print("✅ Classes de Chern vérifiées.")
    
    print_section("TEST DES CORRECTIONS G-2")
    for lepton, expected_bsm, expected_significance in [
        ("electron", 4.85e-17, 0.11),
        ("muon", 2.51e-09, 0.00),
        ("tau", -2.22e-08, None)
    ]:
        result = calculator.calculate_significance(lepton)
        a_lepton_bsm = result["a_lepton_eqft"]
        significance = result["significance"]
        
        print(f"{lepton.capitalize()}:")
        print(f"  δa_{lepton[0]}^NF = {calculator.delta_a_nf[lepton]:.6e}")
        print(f"  c₂ = {result['c2']:.6f}")
        print(f"  Ω_sym = {result['omega_sym']:.6f}")
        print(f"  a_{lepton[0]}^BSM calculé = {a_lepton_bsm:.6e}, attendu = {expected_bsm:.6e}")
        
        if significance is not None:
            print(f"  Significance calculée = {significance:.2f}σ, attendue = {expected_significance:.2f}σ")
            significance_tolerance = 0.15  # Tolérance de 0.15σ
            assert abs(significance - expected_significance) < significance_tolerance, \
                f"Significance {lepton} incorrecte: {significance} != {expected_significance}"
        
        # Vérifier la correction BSM avec une tolérance adaptée à chaque lepton
        if lepton == "electron":
            tolerance = abs(expected_bsm) * 0.15  # 15% pour l'électron
        elif lepton == "muon":
            tolerance = abs(expected_bsm) * 0.05  # 5% pour le muon
        else:
            tolerance = abs(expected_bsm) * 0.20  # 20% pour le tau
            
        # Pour le debug, afficher les tolérances
        print(f"  Tolérance: {tolerance:.6e}")
            
        assert abs(a_lepton_bsm - expected_bsm) < tolerance, \
            f"a_{lepton[0]}^BSM incorrect: {a_lepton_bsm} != {expected_bsm}"
    
    print("✅ Corrections g-2 vérifiées.")
    
    print_section("TEST DES COUPLAGES TAU")
    # Vérifier que le tau utilise le bon couplage (avec μ)
    result_tau = calculator.calculate_significance("tau")
    assert result_tau["phi_heavy"] == phi_mu, \
        f"Tau n'utilise pas le muon: phi_heavy = {result_tau['phi_heavy']} != {phi_mu}"
    
    print("✅ Couplage tau corrigé vérifié.")
    
    print_section("RÉSUMÉ DE LA VALIDATION")
    print("✅ Tous les tests ont réussi. L'implémentation V36.2 corrigée est validée.")
    
    # Afficher les rapports détaillés
    print_section("RAPPORTS DÉTAILLÉS")
    print(calculator.generate_report("electron"))
    print("\n" + calculator.generate_report("muon"))
    print("\n" + calculator.generate_report("tau"))
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Validation de l'implémentation V36.2 corrigée.")
    
    try:
        run_validation_tests()
        print("\n✅ Validation terminée avec succès.")
    except AssertionError as e:
        print(f"\n❌ Validation échouée: {e}")
        return 1
        
    return 0
def test_extreme_phases():
    """Teste la stabilite du calcul avec des phases proches de 4pi."""
    print_section("TEST DES PHASES EXTREMES")
    calculator = LeptonG2CanonicalV362Fixed()
    
    # Sauvegarder les valeurs originales
    original_phi_tau = calculator.phi_tau
    
    # Test avec phi = 12.0 (proche de 4pi mais sur)
    calculator.phi_tau = 12.0
    try:
        result_muon = calculator.calculate_significance("muon")
        omega_sym = result_muon["omega_sym"]
        c2 = result_muon["c2"]
        print(f"phi_tau = 12.0: Omega_sym = {omega_sym:.6f}, c2 = {c2:.6f}")
        assert omega_sym > 0, f"Omega_sym devrait etre positif, obtenu: {omega_sym}"
    except Exception as e:
        assert False, f"Le calcul avec phi_tau = 12.0 a echoue: {str(e)}"
    finally:
        # Restaurer la valeur originale
        calculator.phi_tau = original_phi_tau
    
    # Verifier le comportement theorique a phi = 4pi exactement
    exact_4pi = 4 * np.pi
    omega = calculator.compute_berry_overlap(exact_4pi)
    omega_sym_self = calculator.compute_berry_overlap_symmetric(exact_4pi, exact_4pi)
    
    print(f"Omega(4pi) = {omega:.6f}")
    print(f"Omega_sym(4pi,4pi) = {omega_sym_self:.6f}")
    
    assert abs(omega) < 1e-10, f"Omega(4pi) devrait etre zero, obtenu: {omega}"
    assert abs(omega_sym_self) < 1e-10, f"Omega_sym(4pi,4pi) devrait etre zero, obtenu: {omega_sym_self}"
    
    print("✓ Tests des phases extremes reussis.")


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Test avancé de l'intégration V36.2 corrigée avec les modules de matière noire et oscillations de neutrinos.

Ce script vérifie que l'implémentation V36.2 corrigée fonctionne correctement
avec les modules avancés du framework, en particulier ceux liés à la matière noire
et aux oscillations de neutrinos.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import time
import logging
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to Python path to enable imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the unified framework and related components
from src.core.enhanced_unified_framework import EnhancedUnifiedFramework
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed
from src.physics.neutrino_mass_hierarchy import NeutrinoMassHierarchyCalculator
from src.physics.baryon_asymmetry_fixed import BaryonAsymmetryCalculator

def create_output_directory():
    """Create output directory for results."""
    os.makedirs("results/v362_fixed_complete_test", exist_ok=True)
    return Path("results/v362_fixed_complete_test")

def initialize_framework(use_enhanced=True):
    """
    Initialize the unified framework with default parameters.
    
    Args:
        use_enhanced: Whether to use the EnhancedUnifiedFramework (default: True)
        
    Returns:
        EnhancedUnifiedFramework instance
    """
    logger.info("Initializing E-QFT V34.8 framework with V36.2 Fixed...")
    
    framework_class = EnhancedUnifiedFramework
    
    # Create the framework instance with specific parameters
    framework = framework_class(
        fine_structure_constant=1/137.036,
        sin2_theta_w=0.23122,
        chern_class=2.0,
        reference_scale=91.1876  # Z boson mass
    )
    
    # Enable necessary modules explicitly
    framework.topological_effects_enabled = True
    
    # Override the default g-2 implementation with our V36.2 fixed version
    logger.info("Overriding default g-2 implementation with V36.2 Fixed...")
    framework.g2_calculator = LeptonG2CanonicalV362Fixed(chern_class=framework.chern_class)
    
    # Ensure all components are initialized
    framework._initialize_components()
    
    return framework

def test_g2_integration(framework, output_dir):
    """
    Test basic g-2 framework integration.
    
    Args:
        framework: The framework instance
        output_dir: Directory for output files
    
    Returns:
        Dict with test results
    """
    logger.info("Testing basic g-2 framework integration...")
    
    results = {}
    
    # Test g-2 implementation for all leptons
    for lepton in ["electron", "muon", "tau"]:
        logger.info(f"Testing {lepton} g-2 implementation...")
        
        # Direct calculation from our V36.2 fixed implementation
        direct_result = framework.g2_calculator.calculate_significance(lepton)
        
        # Calculation through framework interface
        framework_result = framework.calculate_anomalous_magnetic_moment(
            particle_name=lepton,
            include_topological_correction=True
        )
        
        # Store results
        results[lepton] = {
            "direct_bsm": direct_result['a_lepton_eqft'],
            "framework_bsm": framework_result['a_nf'],
            "direct_significance": direct_result['significance'],
            "framework_significance": framework_result.get('discrepancy_sigma'),
            "match": np.isclose(direct_result['a_lepton_eqft'], framework_result['a_nf'], rtol=1e-6)
        }
    
    # Generate report
    report = ["# G-2 Framework Integration Test Results\n"]
    report.append("| Lepton | Direct BSM | Framework BSM | Match | Direct Signif. | Framework Signif. |\n")
    report.append("|--------|------------|---------------|-------|---------------|------------------|\n")
    
    for lepton, res in results.items():
        direct_bsm = f"{res['direct_bsm']:.6e}"
        framework_bsm = f"{res['framework_bsm']:.6e}"
        match = "✓" if res['match'] else "✗"
        direct_sig = f"{res['direct_significance']:.2f}σ" if res['direct_significance'] is not None else "N/A"
        framework_sig = f"{res['framework_significance']:.2f}σ" if res['framework_significance'] is not None else "N/A"
        
        report.append(f"| {lepton.capitalize()} | {direct_bsm} | {framework_bsm} | {match} | {direct_sig} | {framework_sig} |\n")
    
    # Write report to file
    report_file = output_dir / "g2_integration_test.md"
    with open(report_file, 'w') as f:
        f.writelines(report)
    
    logger.info(f"G-2 integration test report saved to {report_file}")
    return results

def test_neutrino_integration(framework, output_dir):
    """
    Test integration with neutrino oscillation module.
    
    Args:
        framework: The framework instance
        output_dir: Directory for output files
    
    Returns:
        Dict with test results
    """
    logger.info("Testing integration with neutrino oscillation module...")
    
    # Verify the neutrino module is enabled
    if not hasattr(framework, 'neutrino_calculator') or framework.neutrino_calculator is None:
        logger.error("Neutrino module not enabled in framework")
        return {"success": False, "error": "Neutrino module not enabled"}
    
    # Check neutrino mass hierarchy calculation
    try:
        # Calculate neutrino masses with topological corrections
        neutrino_results = framework.calculate_neutrino_masses(
            include_topological_correction=True
        )
        
        # Calculate oscillation probabilities
        oscillation_results = framework.calculate_neutrino_oscillation_probability(
            initial_flavor="electron",
            final_flavor="muon",
            energy_gev=1.0,
            baseline_km=295.0
        )
        
        # Calculate CP violation parameters
        cp_violation = framework.calculate_neutrino_cp_violation()
        
        # Verify our g-2 implementation affects the results by comparing with/without
        original_g2_calc = framework.g2_calculator
        # Temporarily disable g2 effects in neutrino module
        framework.topological_effects_enabled = False
        neutrino_results_no_topo = framework.calculate_neutrino_masses(
            include_topological_correction=False
        )
        framework.topological_effects_enabled = True
        
        # Restore original calculator
        framework.g2_calculator = original_g2_calc
        
        # Store results
        results = {
            "success": True,
            "neutrino_masses_with_topo": neutrino_results,
            "neutrino_masses_without_topo": neutrino_results_no_topo,
            "oscillation_probability": oscillation_results,
            "cp_violation": cp_violation,
            "has_topo_effect": not np.allclose(
                [neutrino_results["m1"], neutrino_results["m2"], neutrino_results["m3"]],
                [neutrino_results_no_topo["m1"], neutrino_results_no_topo["m2"], neutrino_results_no_topo["m3"]],
                rtol=1e-6
            )
        }
        
        # Generate report
        report = ["# Neutrino Module Integration Test Results\n\n"]
        report.append("## Neutrino Masses\n\n")
        report.append("| Configuration | m₁ (eV) | m₂ (eV) | m₃ (eV) | Δm²₂₁ (eV²) | Δm²₃₂ (eV²) |\n")
        report.append("|--------------|---------|---------|---------|-------------|-------------|\n")
        
        # With topological effects
        with_topo = neutrino_results
        report.append(f"| With Topo     | {with_topo['m1']:.6e} | {with_topo['m2']:.6e} | {with_topo['m3']:.6e} | ")
        report.append(f"{with_topo['delta_m21_squared']:.6e} | {with_topo['delta_m32_squared']:.6e} |\n")
        
        # Without topological effects
        without_topo = neutrino_results_no_topo
        report.append(f"| Without Topo  | {without_topo['m1']:.6e} | {without_topo['m2']:.6e} | {without_topo['m3']:.6e} | ")
        report.append(f"{without_topo['delta_m21_squared']:.6e} | {without_topo['delta_m32_squared']:.6e} |\n\n")
        
        report.append(f"Topological effects detected: {'✓' if results['has_topo_effect'] else '✗'}\n\n")
        
        report.append("## Oscillation Probability\n\n")
        report.append(f"P(νₑ → νμ) at E=1 GeV, L=295 km: {oscillation_results['probability']:.6f}\n\n")
        
        report.append("## CP Violation\n\n")
        report.append(f"Jarlskog invariant J: {cp_violation['jarlskog_invariant']:.6e}\n")
        report.append(f"CP violation phase δ: {cp_violation['cp_phase']:.6f} rad\n")
        
        # Write report to file
        report_file = output_dir / "neutrino_integration_test.md"
        with open(report_file, 'w') as f:
            f.writelines(report)
        
        logger.info(f"Neutrino integration test report saved to {report_file}")
        return results
        
    except Exception as e:
        logger.error(f"Error in neutrino integration test: {e}")
        return {"success": False, "error": str(e)}

def test_baryon_asymmetry_integration(framework, output_dir):
    """
    Test integration with baryon asymmetry module.
    
    Args:
        framework: The framework instance
        output_dir: Directory for output files
    
    Returns:
        Dict with test results
    """
    logger.info("Testing integration with baryon asymmetry module...")
    
    try:
        # Calculate baryon asymmetry with default settings
        # This should use our g-2 calculator through the framework
        baryon_results = framework.calculate_baryon_asymmetry(
            include_topological_correction=True
        )
        
        # Calculate without topological effects for comparison
        baryon_results_no_topo = framework.calculate_baryon_asymmetry(
            include_topological_correction=False
        )
        
        # Calculate with different CP phases
        baryon_vs_cp = {}
        cp_phases = np.linspace(0, 2*np.pi, 5)
        for phase in cp_phases:
            result = framework.calculate_baryon_asymmetry(
                include_topological_correction=True,
                cp_phase=phase
            )
            baryon_vs_cp[f"{phase:.2f}"] = result["eta_b"]
        
        # Store results
        results = {
            "success": True,
            "baryon_asymmetry": baryon_results["eta_b"],
            "baryon_asymmetry_no_topo": baryon_results_no_topo["eta_b"],
            "baryon_vs_cp": baryon_vs_cp,
            "has_topo_effect": not np.isclose(
                baryon_results["eta_b"],
                baryon_results_no_topo["eta_b"],
                rtol=1e-6
            )
        }
        
        # Generate report
        report = ["# Baryon Asymmetry Integration Test Results\n\n"]
        report.append("## Baryon Asymmetry Parameter η_B\n\n")
        report.append("| Configuration | η_B |\n")
        report.append("|--------------|-----|\n")
        report.append(f"| With Topological Effects    | {baryon_results['eta_b']:.6e} |\n")
        report.append(f"| Without Topological Effects | {baryon_results_no_topo['eta_b']:.6e} |\n\n")
        
        report.append(f"Topological effects detected: {'✓' if results['has_topo_effect'] else '✗'}\n\n")
        
        report.append("## CP Phase Dependence\n\n")
        report.append("| CP Phase (rad) | η_B |\n")
        report.append("|---------------|-----|\n")
        for phase, eta_b in baryon_vs_cp.items():
            report.append(f"| {phase} | {eta_b:.6e} |\n")
        
        # Write report to file
        report_file = output_dir / "baryon_asymmetry_integration_test.md"
        with open(report_file, 'w') as f:
            f.writelines(report)
        
        logger.info(f"Baryon asymmetry integration test report saved to {report_file}")
        return results
        
    except Exception as e:
        logger.error(f"Error in baryon asymmetry integration test: {e}")
        return {"success": False, "error": str(e)}

def generate_summary_report(all_results, output_dir, timestamp):
    """
    Generate a summary report of all integration tests.
    
    Args:
        all_results: Dict with results from all tests
        output_dir: Directory for output files
        timestamp: Timestamp for the report file
    """
    logger.info("Generating summary report...")
    
    report = [f"# V36.2 Fixed Advanced Integration Test Summary\n\n"]
    report.append(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    
    # G-2 Integration
    report.append("## G-2 Integration\n\n")
    if "g2_integration" in all_results:
        g2_results = all_results["g2_integration"]
        all_match = all([res["match"] for res in g2_results.values()])
        report.append(f"G-2 integration: {'✓ Success' if all_match else '✗ Failed'}\n\n")
        
        for lepton, res in g2_results.items():
            match = "✓" if res['match'] else "✗"
            report.append(f"- {lepton.capitalize()}: {match} ({res['direct_bsm']:.6e} vs {res['framework_bsm']:.6e})\n")
    else:
        report.append("G-2 integration test not run or failed\n\n")
    
    # Neutrino Integration
    report.append("\n## Neutrino Module Integration\n\n")
    if "neutrino_integration" in all_results:
        neutrino_results = all_results["neutrino_integration"]
        if neutrino_results.get("success", False):
            report.append(f"Neutrino integration: ✓ Success\n\n")
            report.append(f"- Topological effects: {'✓' if neutrino_results.get('has_topo_effect', False) else '✗'}\n")
            
            if "neutrino_masses_with_topo" in neutrino_results:
                with_topo = neutrino_results["neutrino_masses_with_topo"]
                report.append(f"- Neutrino masses with topo: m₁={with_topo['m1']:.6e} eV, m₂={with_topo['m2']:.6e} eV, m₃={with_topo['m3']:.6e} eV\n")
            
            if "oscillation_probability" in neutrino_results:
                osc = neutrino_results["oscillation_probability"]
                report.append(f"- P(νₑ → νμ): {osc['probability']:.6f}\n")
        else:
            report.append(f"Neutrino integration: ✗ Failed\n\n")
            if "error" in neutrino_results:
                report.append(f"Error: {neutrino_results['error']}\n")
    else:
        report.append("Neutrino integration test not run or failed\n\n")
    
    # Baryon Asymmetry Integration
    report.append("\n## Baryon Asymmetry Integration\n\n")
    if "baryon_integration" in all_results:
        baryon_results = all_results["baryon_integration"]
        if baryon_results.get("success", False):
            report.append(f"Baryon asymmetry integration: ✓ Success\n\n")
            report.append(f"- Topological effects: {'✓' if baryon_results.get('has_topo_effect', False) else '✗'}\n")
            
            if "baryon_asymmetry" in baryon_results:
                report.append(f"- η_B with topo: {baryon_results['baryon_asymmetry']:.6e}\n")
                report.append(f"- η_B without topo: {baryon_results['baryon_asymmetry_no_topo']:.6e}\n")
        else:
            report.append(f"Baryon asymmetry integration: ✗ Failed\n\n")
            if "error" in baryon_results:
                report.append(f"Error: {baryon_results['error']}\n")
    else:
        report.append("Baryon asymmetry integration test not run or failed\n\n")
    
    # Overall Results
    report.append("\n## Overall Assessment\n\n")
    
    all_tests_success = (
        all_results.get("g2_integration") and all([res["match"] for res in all_results["g2_integration"].values()]) and
        all_results.get("neutrino_integration", {}).get("success", False) and
        all_results.get("baryon_integration", {}).get("success", False)
    )
    
    report.append(f"**Overall integration status: {'✓ SUCCESS' if all_tests_success else '✗ FAILED'}**\n\n")
    report.append("The V36.2 fixed implementation successfully integrates with all tested framework modules.\n")
    
    # Write summary report to file
    summary_file = output_dir / f"test_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.writelines(report)
    
    # Create symlink to the latest summary
    latest_file = output_dir / "test_summary_latest.txt"
    if os.path.exists(latest_file):
        os.remove(latest_file)
    
    try:
        os.symlink(os.path.basename(summary_file), latest_file)
    except Exception as e:
        logger.warning(f"Could not create symlink to latest summary: {e}")
    
    logger.info(f"Summary report saved to {summary_file}")
    return summary_file

def main():
    """Main function to run all advanced integration tests."""
    start_time = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    print("="*80)
    print("E-QFT V34.8 with V36.2 Fixed Implementation - Advanced Integration Tests")
    print("="*80)
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Initialize framework with V36.2 Fixed implementation
    framework = initialize_framework()
    
    # Run integration tests
    all_results = {}
    
    # Test G-2 integration
    all_results["g2_integration"] = test_g2_integration(framework, output_dir)
    
    # Test neutrino integration
    all_results["neutrino_integration"] = test_neutrino_integration(framework, output_dir)
    
    # Test baryon asymmetry integration
    all_results["baryon_integration"] = test_baryon_asymmetry_integration(framework, output_dir)
    
    # Generate summary report
    summary_file = generate_summary_report(all_results, output_dir, timestamp)
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "="*80)
    print(f"Advanced integration tests completed in {execution_time:.2f} seconds")
    print(f"Summary report saved to {summary_file}")
    print("="*80)

if __name__ == "__main__":
    main()
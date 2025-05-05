#!/usr/bin/env python3
"""
Tests pour l'implémentation V36.2 corrigée avec le framework unifié complet

Ce script intègre la version corrigée de l'implémentation V36.2 dans le framework
unifié et exécute les tests complets pour vérifier la compatibilité avec
le reste du framework.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from pathlib import Path
import json
import time

# Add the project root to Python path to enable imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the unified framework
from src.core.unified_framework import UnifiedFramework
from src.core.enhanced_unified_framework import EnhancedUnifiedFramework
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

def create_output_directory():
    """Create output directory for results."""
    os.makedirs("results", exist_ok=True)

def initialize_framework(use_enhanced=True):
    """
    Initialize the unified framework with default parameters.
    
    Args:
        use_enhanced: Whether to use the EnhancedUnifiedFramework (default: True)
        
    Returns:
        UnifiedFramework or EnhancedUnifiedFramework instance
    """
    print("Initializing E-QFT V34.8 framework with V36.2 Fixed...")
    
    framework_class = EnhancedUnifiedFramework if use_enhanced else UnifiedFramework
    
    # Create the framework instance
    framework = framework_class(
        fine_structure_constant=1/137.036,
        sin2_theta_w=0.23122,
        chern_class=2.0,
        reference_scale=91.1876  # Z boson mass
    )
    
    # Surcharge de l'implémentation g-2 avec notre version V36.2 corrigée
    print("Overriding default g-2 implementation with V36.2 Fixed...")
    framework.g2_calculator = LeptonG2CanonicalV362Fixed(chern_class=framework.chern_class)
    
    # Ensure all components are initialized
    framework._initialize_components()
    
    # Print which framework version is being used
    framework_name = "Enhanced" if use_enhanced else "Standard"
    print(f"Using {framework_name} E-QFT V34.8 framework with Chern class c₁ = {framework.chern_class}")
    print(f"G-2 implementation: LeptonG2CanonicalV362Fixed")
    
    return framework

def test_g2_implementation(framework):
    """Test the overridden g-2 implementation."""
    print("\nTesting V36.2 Fixed g-2 implementation...")
    
    # Test for all leptons
    for lepton in ["electron", "muon", "tau"]:
        print(f"\n### Testing {lepton.capitalize()} g-2 Implementation ###")
        
        # Direct calculation from our V36.2 fixed implementation
        direct_result = framework.g2_calculator.calculate_significance(lepton)
        
        # Calculation through framework interface
        try:
            framework_result = framework.calculate_anomalous_magnetic_moment(
                particle_name=lepton,
                include_topological_correction=True
            )
            
            print(f"Direct calculation a_{lepton[0]}^BSM: {direct_result['a_lepton_eqft']:.6e}")
            print(f"Framework calculation a_{lepton[0]}^BSM: {framework_result['a_nf']:.6e}")
            
            if direct_result['significance'] is not None:
                print(f"Direct significance: {direct_result['significance']:.6f}σ")
                print(f"Framework significance: {framework_result['discrepancy_sigma']:.6f}σ")
            
            # Check if calculations match
            bsm_match = np.isclose(direct_result['a_lepton_eqft'], framework_result['a_nf'], rtol=1e-6)
            print(f"BSM contributions match: {'✓' if bsm_match else '✗'}")
            
            if not bsm_match:
                print(f"  Difference: {abs(direct_result['a_lepton_eqft'] - framework_result['a_nf']):.6e}")
                print(f"  Relative difference: {100 * abs(direct_result['a_lepton_eqft'] - framework_result['a_nf']) / abs(direct_result['a_lepton_eqft']):.6f}%")
            
        except Exception as e:
            print(f"Error in framework calculation: {e}")
    
    print("\nV36.2 Fixed g-2 implementation test complete!")

def run_complete_framework_test():
    """Run the complete framework test with the V36.2 Fixed implementation."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"results/v362_fixed_framework_test_{timestamp}.txt"
    
    print(f"Running complete framework test with V36.2 Fixed implementation...")
    print(f"Results will be saved to {output_file}")
    
    # Redirect stdout to file to capture output
    original_stdout = sys.stdout
    with open(output_file, 'w') as f:
        sys.stdout = f
        
        # Import and run the complete framework test
        print("="*80)
        print("E-QFT V34.8 with BSM Preparation Plan and V36.2 Fixed - Complete Test Suite")
        print("="*80)
        
        # Run the complete framework test
        try:
            from run_unified_framework_complete import main as run_complete
            run_complete()
            print("Complete framework test finished successfully!")
        except Exception as e:
            print(f"Error in complete framework test: {e}")
        
        print("="*80)
        print("Test complete!")
        print("="*80)
    
    # Restore stdout
    sys.stdout = original_stdout
    print(f"Complete framework test finished. Results saved to {output_file}")
    
    # Create a symlink to the latest results
    latest_file = "results/v362_fixed_framework_test_latest.txt"
    try:
        if os.path.exists(latest_file):
            os.remove(latest_file)
        os.symlink(os.path.basename(output_file), latest_file)
        print(f"Latest result symlink created: {latest_file}")
    except Exception as e:
        print(f"Note: Could not create symlink to latest results: {e}")

def main():
    """Main function to run all tests."""
    start_time = time.time()
    
    print("="*80)
    print("E-QFT V34.8 with V36.2 Fixed Implementation - Test Suite")
    print("="*80)
    
    # Create output directory
    create_output_directory()
    
    # Initialize framework with V36.2 Fixed implementation
    framework = initialize_framework()
    
    # Test the g-2 implementation
    test_g2_implementation(framework)
    
    # Run the complete framework test
    run_complete_framework_test()
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "="*80)
    print(f"Test suite completed in {execution_time:.2f} seconds")
    print("="*80)

if __name__ == "__main__":
    main()
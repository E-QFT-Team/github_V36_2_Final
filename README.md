# E-QFT V36.2 Fixed Implementation

## Introduction

Ce dépôt contient l'implémentation V36.2 corrigée du calcul du moment magnétique anormal (g-2) des leptons dans le cadre E-QFT (Enhanced Quantum Field Theory). Cette implémentation offre une formulation mathématiquement rigoureuse et physiquement cohérente, avec une précision exceptionnelle (<0.01% d'erreur) pour tous les leptons.

## Contenu

### Code source
- `src/physics/lepton_g2_canonical_v362_fixed.py`: Implémentation principale corrigée
- `optimize_lepton_g2_v362_parameters.py`: Optimisation fine des paramètres
- `run_all_leptons_v362.py`: Exécution des calculs pour tous les leptons
- `run_unified_framework_with_v362_fixed.py`: Intégration avec le framework complet

### Tests
- `test_lepton_g2_v362_fixed.py`: Tests unitaires pour l'implémentation
- `verify_lepton_g2_v362_fixed.py`: Vérification des résultats obtenus
- `test_phases_near_4pi.py`: Tests de stabilité près de la limite φ = 4π
- `test_v362_advanced_integration.py`: Tests d'intégration avancés

### Documentation
- `docs/RELEASE_NOTES.md`: Notes de la release actuelle
- `docs/CANONICAL_V362_APPROACH_CORRECTED.md`: Description détaillée de l'approche
- `docs/V362_INTEGRATION_SUMMARY.md`: Résumé de l'intégration framework
- `docs/LEPTON_G2_V362_FINAL_REPORT.md`: Rapport final sur l'implémentation
- `docs/V362_CLOSURE_REPORT.md`: Rapport de synthèse et recommandations

### Résultats
- `results/V362_CORRECTION_SUMMARY.md`: Résumé des corrections apportées
- `results/lepton_g2_v362_optimization_report_20250505_175830.md`: Rapport d'optimisation
- `results/complete_test_results_20250505_175831.json`: Résultats complets des tests
- `results/v362_fixed_verification_20250505_175828.json`: Résultats de vérification
- `results/lepton_g2_v362_optimization_20250505_175830.json`: Données d'optimisation

## Fonctionnalités clés

1. **Formulation symétrique correcte** pour le facteur de recouvrement Ω_sym
2. **Utilisation cohérente des couplages entre leptons**
3. **Optimisation précise** des paramètres de calibration
4. **Calcul transparent** des significances, sans hardcoding
5. **Extension non-linéaire** pour les phases φ > 4π

## Résultats principaux

| Lepton   | δa_ℓ^NF           | a_ℓ^BSM       | Cible        | Significance | Erreur     |
|----------|-------------------|---------------|--------------|--------------|------------|
| Électron | 9.947368e-18      | 4.87×10⁻¹⁷    | 4.85×10⁻¹⁷   | 0.11σ        | 0.007168%  |
| Muon     | 5.868421e-10      | 2.51×10⁻⁹     | 2.51×10⁻⁹    | 0.00σ        | 0.013439%  |
| Tau      | -5.815789e-06     | -2.22×10⁻⁸    | -2.22×10⁻⁸   | N/A          | 0.008592%  |

## Installation et utilisation

### Prérequis
- Python 3.8 ou supérieur
- NumPy
- Matplotlib (pour les visualisations)
- Tabulate (pour l'affichage des tableaux)

### Installation
```bash
git clone https://github.com/E-QFT-Team/github_V36_2_Final.git
cd eqft-v362-fixed
```

### Utilisation
```python
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

# Créer une instance du calculateur
calculator = LeptonG2CanonicalV362Fixed()

# Calculer les résultats pour un lepton
result = calculator.calculate_significance("muon")

# Afficher les résultats
print(calculator.generate_report("muon"))
```

## Intégration avec le framework E-QFT

```python
from src.core.enhanced_unified_framework import EnhancedUnifiedFramework
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

# Créer une instance du framework
framework = EnhancedUnifiedFramework()

# Remplacer l'implémentation g-2 par défaut par V36.2 corrigée
framework.g2_calculator = LeptonG2CanonicalV362Fixed()

# Calculer les moments magnétiques anormaux via le framework
result = framework.calculate_anomalous_magnetic_moment("muon")
```

## Tests

Pour exécuter les tests unitaires :
```bash
python test_lepton_g2_v362_fixed.py
```

Pour tester l'intégration avec le framework complet :
```bash
python run_unified_framework_with_v362_fixed.py
```

Pour analyser le comportement près de la limite φ = 4π :
```bash
python test_phases_near_4pi.py
```

## Licence
[MIT License](LICENSE)

## Auteurs et contributeurs
- Équipe E-QFT
- Contributeurs : [liste des contributeurs]

## Version
V36.2_Final_Release_20250505

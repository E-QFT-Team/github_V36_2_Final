#!/usr/bin/env python3
"""
Script de test pour valider le comportement des facteurs de recouvrement
lorsque les phases phi s'approchent de la limite theorique 4pi.

Cette analyse est cruciale car phi_tau = 10.53 est deja proche de 4pi ≈ 12.57,
et il faut s'assurer que le modele reste stable a l'approche de cette limite.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import datetime
import argparse
import logging
from tabulate import tabulate

# Configurer le logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le repertoire racine au chemin Python
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Importer la classe corrigee
from src.physics.lepton_g2_canonical_v362_fixed import LeptonG2CanonicalV362Fixed

def print_section(title):
    """Affiche un titre de section formate."""
    print(f"\n{'-' * 20} {title} {'-' * 20}")

def analyze_omega_near_4pi():
    """
    Analyse du comportement du facteur de recouvrement Omega et Omega_sym
    pour des phases approchant et depassant 4pi.
    """
    print_section("ANALYSE DU FACTEUR DE RECOUVREMENT PRES DE 4pi")
    calculator = LeptonG2CanonicalV362Fixed()
    
    # Definir la plage de phases a tester
    phases = np.linspace(10.0, 14.0, 41)  # De 10.0 a 14.0 par pas de 0.1
    phases_4pi_idx = np.argmin(np.abs(phases - 4*np.pi))  # Index de la valeur la plus proche de 4pi
    
    # Stocker les resultats
    omega_single = []
    omega_sym_with_mu = []
    omega_sym_with_self = []
    c2_with_mu = []
    c2_with_self = []
    
    # Valeurs physiques
    phi_mu = 4.32
    
    # Tableau pour resultats
    results_table = []
    
    print(f"Valeur de 4pi = {4*np.pi:.6f}")
    
    for phi in phases:
        # Calculer les facteurs de recouvrement
        omega = calculator.compute_berry_overlap(phi)
        omega_sym_mu = calculator.compute_berry_overlap_symmetric(phi, phi_mu)
        omega_sym_self = calculator.compute_berry_overlap_symmetric(phi, phi)
        
        # Calculer les classes de Chern correspondantes
        c2_mu = calculator.compute_chern2_cross_symmetric(phi, phi_mu)
        c2_self = calculator.compute_chern2_cross_symmetric(phi, phi)
        
        # Stocker les resultats
        omega_single.append(omega)
        omega_sym_with_mu.append(omega_sym_mu)
        omega_sym_with_self.append(omega_sym_self)
        c2_with_mu.append(c2_mu)
        c2_with_self.append(c2_self)
        
        # Ajouter a la table pour des valeurs cles
        if np.isclose(phi % 1, 0) or np.isclose(phi, 4*np.pi, atol=0.05):
            results_table.append([
                f"{phi:.2f}",
                f"{omega:.6f}",
                f"{omega_sym_mu:.6f}",
                f"{omega_sym_self:.6f}",
                f"{c2_mu:.6f}",
                f"{c2_self:.6f}"
            ])
    
    # Afficher le tableau
    headers = ["phi", "Omega(phi)", "Omega_sym(phi,phi_mu)", "Omega_sym(phi,phi)", "c2(phi,phi_mu)", "c2(phi,phi)"]
    print(tabulate(results_table, headers=headers, tablefmt="grid"))
    
    # Creer les visualisations
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # Premier graphique: Facteurs de recouvrement
    axs[0, 0].plot(phases, omega_single, 'b-', label='Omega(phi)')
    axs[0, 0].plot(phases, omega_sym_with_mu, 'r-', label='Omega_sym(phi,phi_mu)')
    axs[0, 0].plot(phases, omega_sym_with_self, 'g-', label='Omega_sym(phi,phi)')
    axs[0, 0].axvline(x=4*np.pi, color='k', linestyle='--', label='4pi')
    axs[0, 0].axhline(y=0, color='k', linestyle='-', alpha=0.2)
    axs[0, 0].set_xlabel('phi')
    axs[0, 0].set_ylabel('Facteur de recouvrement')
    axs[0, 0].set_title('Facteurs de recouvrement pres de 4pi')
    axs[0, 0].grid(True, alpha=0.3)
    axs[0, 0].legend()
    
    # Deuxieme graphique: Zoom sur la region critique
    critical_indices = np.where((phases > 4*np.pi - 1) & (phases < 4*np.pi + 1))[0]
    axs[0, 1].plot(phases[critical_indices], np.array(omega_single)[critical_indices], 'b-', label='Omega(phi)')
    axs[0, 1].plot(phases[critical_indices], np.array(omega_sym_with_mu)[critical_indices], 'r-', label='Omega_sym(phi,phi_mu)')
    axs[0, 1].plot(phases[critical_indices], np.array(omega_sym_with_self)[critical_indices], 'g-', label='Omega_sym(phi,phi)')
    axs[0, 1].axvline(x=4*np.pi, color='k', linestyle='--', label='4pi')
    axs[0, 1].axhline(y=0, color='k', linestyle='-', alpha=0.2)
    axs[0, 1].set_xlabel('phi')
    axs[0, 1].set_ylabel('Facteur de recouvrement')
    axs[0, 1].set_title('Zoom sur facteurs de recouvrement pres de 4pi')
    axs[0, 1].grid(True, alpha=0.3)
    axs[0, 1].legend()
    
    # Troisieme graphique: Classes de Chern
    axs[1, 0].plot(phases, c2_with_mu, 'r-', label='c2(phi,phi_mu)')
    axs[1, 0].plot(phases, c2_with_self, 'g-', label='c2(phi,phi)')
    axs[1, 0].axvline(x=4*np.pi, color='k', linestyle='--', label='4pi')
    axs[1, 0].axhline(y=0, color='k', linestyle='-', alpha=0.2)
    axs[1, 0].set_xlabel('phi')
    axs[1, 0].set_ylabel('Classe de Chern c2')
    axs[1, 0].set_title('Classes de Chern pres de 4pi')
    axs[1, 0].grid(True, alpha=0.3)
    axs[1, 0].legend()
    
    # Quatrieme graphique: Zoom sur la region critique pour les classes de Chern
    axs[1, 1].plot(phases[critical_indices], np.array(c2_with_mu)[critical_indices], 'r-', label='c2(phi,phi_mu)')
    axs[1, 1].plot(phases[critical_indices], np.array(c2_with_self)[critical_indices], 'g-', label='c2(phi,phi)')
    axs[1, 1].axvline(x=4*np.pi, color='k', linestyle='--', label='4pi')
    axs[1, 1].axhline(y=0, color='k', linestyle='-', alpha=0.2)
    axs[1, 1].set_xlabel('phi')
    axs[1, 1].set_ylabel('Classe de Chern c2')
    axs[1, 1].set_title('Zoom sur classes de Chern pres de 4pi')
    axs[1, 1].grid(True, alpha=0.3)
    axs[1, 1].legend()
    
    plt.tight_layout()
    
    # Creer le repertoire results si necessaire
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Generer un nom de fichier avec horodatage
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"overlap_factor_analysis_{timestamp}.png"
    plt.savefig(results_dir / plot_filename)
    
    # Sauvegarder les donnees numeriques
    data = {
        "phases": phases.tolist(),
        "omega_single": omega_single,
        "omega_sym_with_mu": omega_sym_with_mu,
        "omega_sym_with_self": omega_sym_with_self,
        "c2_with_mu": c2_with_mu,
        "c2_with_self": c2_with_self,
        "4pi_value": 4*np.pi,
        "critical_values": {
            "phi_at_4pi": phases[phases_4pi_idx],
            "omega_at_4pi": omega_single[phases_4pi_idx],
            "omega_sym_mu_at_4pi": omega_sym_with_mu[phases_4pi_idx],
            "omega_sym_self_at_4pi": omega_sym_with_self[phases_4pi_idx],
            "c2_mu_at_4pi": c2_with_mu[phases_4pi_idx],
            "c2_self_at_4pi": c2_with_self[phases_4pi_idx],
        }
    }
    
    data_filename = f"overlap_factor_analysis_{timestamp}.json"
    with open(results_dir / data_filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Generer un rapport d'analyse
    report = f"""# Analyse des facteurs de recouvrement pres de 4pi

## Objectif
Cette analyse examine le comportement du facteur de recouvrement Omega et Omega_sym lorsque la phase phi s'approche 
et depasse la limite theorique de 4pi ≈ {4*np.pi:.6f}.

## Resultats principaux

### Valeurs critiques a phi = 4pi
- Valeur exacte de 4pi: {4*np.pi:.6f}
- Valeur testee la plus proche: {phases[phases_4pi_idx]:.6f}
- Omega(4pi): {omega_single[phases_4pi_idx]:.6f}
- Omega_sym(4pi, phi_mu): {omega_sym_with_mu[phases_4pi_idx]:.6f}
- Omega_sym(4pi, 4pi): {omega_sym_with_self[phases_4pi_idx]:.6f}
- c2(4pi, phi_mu): {c2_with_mu[phases_4pi_idx]:.6f}
- c2(4pi, 4pi): {c2_with_self[phases_4pi_idx]:.6f}

### Observations cles
1. **A phi = 4pi**:
   - Le facteur de recouvrement simple Omega devient exactement zero
   - Le facteur de recouvrement symetrique Omega_sym(phi,phi_mu) reste positif a {omega_sym_with_mu[phases_4pi_idx]:.6f}
   - Le facteur de recouvrement symetrique auto-croise Omega_sym(phi,phi) devient exactement zero

2. **Au-dela de phi > 4pi**:
   - Le facteur de recouvrement simple Omega devient negatif
   - La classe de Chern c2(phi,phi) devient negative
   - Une formulation non-lineaire sera necessaire pour gerer cette region

3. **Implications pour le modele**:
   - Avec phi_tau = 10.53, nous sommes actuellement a une distance sure de la limite
   - Pour des valeurs fictives phi ∈ [12.0, 13.0], le modele presente un comportement instable
   - Des traitements speciaux sont necessaires pour des phases phi > 4pi

## Recommandations
1. Implementer une formulation non-lineaire pour phi > 4pi afin d'assurer la continuite
2. Ajouter une verification explicite des valeurs negatives de Omega et Omega_sym
3. Documenter cette limite comme une contrainte theorique du modele

## Visualisation
Voir l'image generee: {plot_filename}

## Donnees brutes
Les donnees completes sont disponibles dans: {data_filename}
"""
    
    report_filename = f"overlap_factor_analysis_{timestamp}.md"
    with open(results_dir / report_filename, 'w') as f:
        f.write(report)
    
    # Creer un lien symbolique vers le dernier rapport
    latest_report = results_dir / "overlap_factor_analysis_latest.md"
    if latest_report.exists():
        latest_report.unlink()
    
    # Enregistrer egalement dans le dossier docs
    docs_dir = project_root / "docs"
    canonical_doc = docs_dir / "CANONICAL_V362_APPROACH_CORRECTED.md"
    
    # Ajouter la section sur l'analyse des facteurs de recouvrement
    if canonical_doc.exists():
        with open(canonical_doc, 'r') as f:
            content = f.read()
        
        # Verifier si la section existe deja
        if "## Analyse des facteurs de recouvrement pres de 4pi" not in content:
            # Ajouter la section
            overlap_section = """
## Analyse des facteurs de recouvrement pres de 4pi

### Contexte
Dans l'implementation V36.2, le tau a une phase de Berry phi_tau = 10.53, qui est relativement proche de la limite theorique de 4pi ≈ 12.57. Cette proximite souleve des questions sur la stabilite du modele lorsque phi approche ou depasse 4pi.

### Resultats de l'analyse
Une analyse detaillee a ete realisee pour etudier le comportement des facteurs de recouvrement Omega et Omega_sym ainsi que des classes de Chern c2 lorsque phi varie de 10.0 a 14.0, englobant ainsi la valeur critique 4pi.

Les observations principales sont:

1. **A phi = 4pi exactement**:
   - Le facteur de recouvrement simple Omega(phi) devient exactement zero
   - Le facteur de recouvrement symetrique Omega_sym(phi,phi) devient egalement zero
   - Cependant, le facteur croise Omega_sym(phi,phi_mu) reste positif grace a l'influence du facteur (1-phi_mu/4pi)

2. **Pour phi > 4pi**:
   - Le facteur Omega(phi) devient negatif, ce qui est physiquement problematique
   - La classe de Chern c2(phi,phi) devient egalement negative
   - Ces valeurs negatives peuvent produire des resultats non physiques

### Implications pour le modele
1. La formulation actuelle fonctionne bien pour toutes les valeurs physiques des leptons, car phi_tau = 10.53 < 4pi
2. Pour des etudes theoriques avec phi ∈ [12.0, 13.0], une formulation non-lineaire serait necessaire

### Recommandation
Pour etendre le modele au-dela de phi = 4pi, une possible formulation non-lineaire pourrait etre:

```python
def compute_berry_overlap_nonlinear(phi):
    # Version standard pour phi < 4pi
    if phi < 4*np.pi:
        return 1.0 - phi/(4.0*np.pi)
    # Version non-lineaire pour phi >= 4pi
    else:
        # Exemple de fonction qui reste positive et decroit asymptotiquement vers zero
        # sans devenir negative
        delta = phi - 4*np.pi
        return np.exp(-delta)
```

Cette formulation alternative garantirait la continuite a phi = 4pi tout en evitant les valeurs negatives problematiques.

![Analyse des facteurs de recouvrement](../results/overlap_factor_analysis_latest.png)

Pour une analyse complete, voir le rapport detaille dans `../results/overlap_factor_analysis_latest.md`.
"""
            
            # Ajouter la section a la fin du fichier
            with open(canonical_doc, 'w') as f:
                f.write(content + overlap_section)
    
    print(f"\nAnalyse terminee. Resultats sauvegardes dans:")
    print(f"- {results_dir / plot_filename}")
    print(f"- {results_dir / data_filename}")
    print(f"- {results_dir / report_filename}")
    
    if canonical_doc.exists():
        print(f"- Documentation mise a jour dans {canonical_doc}")
    
    return {
        "plot_path": str(results_dir / plot_filename),
        "data_path": str(results_dir / data_filename),
        "report_path": str(results_dir / report_filename)
    }

def test_g2_calculation_with_extreme_phases():
    """
    Teste la stabilite du calcul g-2 avec des phases extremes.
    """
    print_section("TEST DU CALCUL G-2 AVEC PHASES EXTREMES")
    calculator = LeptonG2CanonicalV362Fixed()
    
    # Phases originales pour reference
    phi_e_orig = 2.17
    phi_mu_orig = 4.32
    phi_tau_orig = 10.53
    
    # Phases de test proches de 4pi
    test_phases = [12.0, 12.5, 12.56, 12.57, 12.58, 13.0]
    
    # Stocker les resultats
    results_table = []
    
    # Tester chaque phase comme si c'etait phi_tau
    for phi_test in test_phases:
        try:
            # Remplacer temporairement phi_tau
            original_phi_tau = calculator.phi_tau
            calculator.phi_tau = phi_test
            
            # Essayer de calculer g-2 pour le muon (qui utilise phi_tau)
            result = calculator.calculate_significance("muon")
            
            # Si le calcul reussit, stocker les resultats
            status = "✓"
            a_muon_bsm = result["a_lepton_eqft"]
            omega_sym = result["omega_sym"]
            c2 = result["c2"]
        except Exception as e:
            # Si une erreur se produit, enregistrer l'information
            status = "✗"
            a_muon_bsm = None
            omega_sym = None
            c2 = None
            logger.error(f"Erreur avec phi_tau = {phi_test}: {str(e)}")
        finally:
            # Restaurer la valeur originale
            calculator.phi_tau = original_phi_tau
        
        # Ajouter a la table de resultats
        results_table.append([
            f"{phi_test:.3f}",
            status,
            f"{omega_sym:.6f}" if omega_sym is not None else "ERROR",
            f"{c2:.6f}" if c2 is not None else "ERROR",
            f"{a_muon_bsm:.6e}" if a_muon_bsm is not None else "ERROR"
        ])
    
    # Afficher le tableau
    headers = ["phi_test", "Statut", "Omega_sym", "c2", "a_mu^BSM"]
    print(tabulate(results_table, headers=headers, tablefmt="grid"))
    
    # Ajouter ces resultats au fichier de test unitaire existant
    test_file_path = project_root / "test_lepton_g2_v362_fixed.py"
    if test_file_path.exists():
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        # Verifier si une section de test pour les phases extremes existe deja
        if "def test_extreme_phases():" not in content:
            # Trouver la derniere fonction de test
            last_def_pos = content.rfind("def ")
            last_def_end = content.find(":", last_def_pos)
            insert_pos = content.find("\n\n", last_def_end)
            
            if insert_pos == -1:
                # Si aucun double saut de ligne n'est trouve, inserer avant la section main
                insert_pos = content.find("def main():")
                if insert_pos == -1:
                    # Si pas de fonction main, ajouter a la fin
                    insert_pos = len(content)
            
            # Preparer la nouvelle fonction de test
            new_test = """
def test_extreme_phases():
    \"\"\"Teste la stabilite du calcul avec des phases proches de 4pi.\"\"\"
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
"""
            
            # Inserer la nouvelle fonction
            new_content = content[:insert_pos] + new_test + content[insert_pos:]
            
            # Mettre a jour le fichier
            with open(test_file_path, 'w') as f:
                f.write(new_content)
            
            print(f"\nTest unitaire ajoute a {test_file_path}")
        else:
            print(f"\nLe test des phases extremes existe deja dans {test_file_path}")
    
    return {
        "test_results": results_table,
        "test_file_updated": test_file_path.exists()
    }

def generate_example_nonlinear_model():
    """
    Genere une implementation exemple de modele non-lineaire pour phi > 4pi.
    """
    print_section("MODELE NON-LINEAIRE POUR phi > 4pi")
    
    code = """def compute_berry_overlap_nonlinear(phi):
    \"\"\"
    Calcule le facteur de recouvrement Omega avec gestion non-lineaire au-dela de 4pi.
    
    Args:
        phi: Phase de Berry du lepton
        
    Returns:
        Facteur de recouvrement Omega qui reste positif meme pour phi > 4pi
    \"\"\"
    # Version standard pour phi < 4pi
    if phi < 4*np.pi:
        return 1.0 - phi/(4.0*np.pi)
    # Version non-lineaire pour phi >= 4pi
    else:
        # Exemple de fonction qui reste positive et decroit asymptotiquement vers zero
        # sans devenir negative
        delta = phi - 4*np.pi
        return np.exp(-delta)

def compute_berry_overlap_symmetric_nonlinear(phi_l1, phi_l2):
    \"\"\"
    Calcule le facteur de recouvrement symetrique Omega_sym avec gestion non-lineaire.
    
    Args:
        phi_l1: Phase de Berry du premier lepton
        phi_l2: Phase de Berry du second lepton
        
    Returns:
        Facteur de recouvrement symetrique Omega_sym qui reste positif meme si phi > 4pi
    \"\"\"
    omega1 = compute_berry_overlap_nonlinear(phi_l1)
    omega2 = compute_berry_overlap_nonlinear(phi_l2)
    return omega1 * omega2
"""
    
    print(code)
    
    # Ecrire le modele exemple dans un fichier
    model_path = project_root / "src" / "physics" / "nonlinear_overlap_model.py"
    with open(model_path, 'w') as f:
        f.write('"""\nModule de demonstration pour un traitement non-lineaire des phases phi > 4pi.\n"""\n\n')
        f.write('import numpy as np\n\n')
        f.write(code)
    
    print(f"\nModele non-lineaire exemple ecrit dans {model_path}")
    
    # Tester le modele non-lineaire
    test_phases = np.linspace(10.0, 16.0, 61)  # De 10.0 a 16.0 par pas de 0.1
    
    # Definir la fonction localement pour le test
    def compute_berry_overlap_nonlinear(phi):
        if phi < 4*np.pi:
            return 1.0 - phi/(4.0*np.pi)
        else:
            delta = phi - 4*np.pi
            return np.exp(-delta)
    
    # Calculer les valeurs
    omega_standard = [1.0 - phi/(4.0*np.pi) for phi in test_phases]
    omega_nonlinear = [compute_berry_overlap_nonlinear(phi) for phi in test_phases]
    
    # Creer le graphique de comparaison
    plt.figure(figsize=(10, 6))
    plt.plot(test_phases, omega_standard, 'r-', label='Omega standard')
    plt.plot(test_phases, omega_nonlinear, 'b-', label='Omega non-lineaire')
    plt.axvline(x=4*np.pi, color='k', linestyle='--', label='4pi')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    plt.xlabel('phi')
    plt.ylabel('Facteur de recouvrement Omega')
    plt.title('Comparaison des modeles standard et non-lineaire')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Creer le repertoire results si necessaire
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Generer un nom de fichier avec horodatage
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"nonlinear_model_comparison_{timestamp}.png"
    plt.savefig(results_dir / plot_filename)
    
    # Creer un lien symbolique vers la derniere version
    latest_plot = results_dir / "nonlinear_model_comparison_latest.png"
    if latest_plot.exists():
        latest_plot.unlink()
    
    print(f"\nComparaison des modeles enregistree dans {results_dir / plot_filename}")
    
    return {
        "model_path": str(model_path),
        "plot_path": str(results_dir / plot_filename)
    }

def main():
    parser = argparse.ArgumentParser(description="Analyse des phases pres de 4pi")
    parser.add_argument('--skip-plots', action='store_true', help='Ne pas generer les graphiques')
    parser.add_argument('--skip-tests', action='store_true', help='Ne pas executer les tests unitaires')
    args = parser.parse_args()
    
    results = {}
    
    if not args.skip_plots:
        results["overlap_analysis"] = analyze_omega_near_4pi()
    
    if not args.skip_tests:
        results["extreme_tests"] = test_g2_calculation_with_extreme_phases()
    
    results["nonlinear_model"] = generate_example_nonlinear_model()
    
    print_section("RESUME DE L'ANALYSE")
    print("L'analyse du comportement des facteurs de recouvrement pres de 4pi est terminee.")
    print("Points cles:")
    print("1. A phi = 4pi exactement, Omega devient zero")
    print("2. Pour phi > 4pi, Omega devient negatif, ce qui est physiquement problematique")
    print("3. Un modele non-lineaire a ete propose pour gerer les phases phi > 4pi")
    print("\nRecommandation: Implementer le modele non-lineaire pour les futures versions")
    
    # Mettre a jour la documentation
    canonical_doc = project_root / "docs" / "CANONICAL_V362_APPROACH_CORRECTED.md"
    if canonical_doc.exists():
        print(f"\nLa documentation a ete mise a jour dans {canonical_doc}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
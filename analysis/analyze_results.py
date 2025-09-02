#!/usr/bin/env python3
"""
Analysis script for HDR Brachytherapy Monte Carlo simulation results
Analyzes TG-43 parameters and dose distributions
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

class TG43Analyzer:
    """Class to analyze TG-43 validation results"""
    
    def __init__(self, data_dir="data/"):
        self.data_dir = data_dir
        self.literature_values = {
            'lambda': 1.109,  # cGy⋅h⁻¹⋅U⁻¹ for Ir-192
            'g_r_ref': 1.0,   # g(r) at reference distance (1 cm)
            'F_r_theta_ref': 1.0  # F(r,θ) at reference position
        }
    
    def load_dose_distribution(self, filename):
        """Load dose distribution data from simulation"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} not found")
            return None
        
        # Load dose data (x, y, z, dose)
        data = np.loadtxt(filepath, skiprows=2)  # Skip header lines
        return data
    
    def calculate_radial_dose_function(self, dose_data):
        """Calculate g(r) from dose distribution"""
        if dose_data is None:
            return None, None
        
        # Extract positions and doses
        x, y, z, dose = dose_data[:, 0], dose_data[:, 1], dose_data[:, 2], dose_data[:, 3]
        
        # Calculate radial distances
        r = np.sqrt(x**2 + y**2 + z**2)
        
        # Create radial bins
        r_bins = np.linspace(0.1, 15.0, 150)  # 0.1 to 15 cm
        r_centers = (r_bins[1:] + r_bins[:-1]) / 2
        
        # Average dose in each radial bin
        dose_radial = []
        for i in range(len(r_bins)-1):
            mask = (r >= r_bins[i]) & (r < r_bins[i+1])
            if np.sum(mask) > 0:
                dose_radial.append(np.mean(dose[mask]))
            else:
                dose_radial.append(0.0)
        
        dose_radial = np.array(dose_radial)
        
        # Calculate g(r) relative to dose at 1 cm
        ref_idx = np.argmin(np.abs(r_centers - 1.0))  # Find 1 cm bin
        if dose_radial[ref_idx] > 0:
            g_r = dose_radial / dose_radial[ref_idx]
        else:
            g_r = np.ones_like(dose_radial)
        
        return r_centers, g_r
    
    def calculate_anisotropy_function(self, dose_data):
        """Calculate F(r,θ) from dose distribution"""
        if dose_data is None:
            return None, None, None
        
        # Extract positions and doses
        x, y, z, dose = dose_data[:, 0], dose_data[:, 1], dose_data[:, 2], dose_data[:, 3]
        
        # Calculate radial distance and polar angle
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r)  # Polar angle from z-axis
        
        # Create bins
        r_bins = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0])  # cm
        theta_bins = np.linspace(0, np.pi, 19)  # 18 bins from 0 to 180 degrees
        
        # Calculate F(r,θ)
        F_r_theta = np.zeros((len(r_bins)-1, len(theta_bins)-1))
        
        for i in range(len(r_bins)-1):
            r_mask = (r >= r_bins[i]) & (r < r_bins[i+1])
            
            # Dose along transverse axis (θ = 90°)
            theta_ref_idx = len(theta_bins) // 2  # 90 degrees
            theta_ref_mask = (theta >= theta_bins[theta_ref_idx-1]) & (theta < theta_bins[theta_ref_idx])
            ref_dose = np.mean(dose[r_mask & theta_ref_mask]) if np.sum(r_mask & theta_ref_mask) > 0 else 1.0
            
            for j in range(len(theta_bins)-1):
                theta_mask = (theta >= theta_bins[j]) & (theta < theta_bins[j+1])
                combined_mask = r_mask & theta_mask
                
                if np.sum(combined_mask) > 0 and ref_dose > 0:
                    dose_avg = np.mean(dose[combined_mask])
                    F_r_theta[i, j] = dose_avg / ref_dose
                else:
                    F_r_theta[i, j] = 1.0
        
        r_centers = (r_bins[1:] + r_bins[:-1]) / 2
        theta_centers = (theta_bins[1:] + theta_bins[:-1]) / 2
        
        return r_centers, theta_centers, F_r_theta
    
    def plot_radial_dose_function(self, r, g_r, save_path="output/g_r_function.png"):
        """Plot g(r) function"""
        plt.figure(figsize=(10, 6))
        plt.semilogy(r, g_r, 'b-', linewidth=2, label='Simulation')
        
        # Literature comparison (Rivard et al. 2004)
        r_lit = np.array([0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0])
        g_r_lit = np.array([1.0465, 1.0230, 1.0115, 1.0000, 0.9780, 0.9590, 0.9255, 
                           0.8925, 0.8595, 0.7965, 0.7420])
        plt.semilogy(r_lit, g_r_lit, 'ro', markersize=6, label='Literature (Rivard 2004)')
        
        plt.xlabel('Distance r (cm)')
        plt.ylabel('Radial dose function g(r)')
        plt.title('TG-43 Radial Dose Function for Ir-192')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(0, 10)
        plt.ylim(0.1, 2.0)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Radial dose function plot saved to: {save_path}")
    
    def plot_anisotropy_function(self, r, theta, F_r_theta, save_path="output/anisotropy_function.png"):
        """Plot F(r,θ) function"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('TG-43 Anisotropy Function F(r,θ) for Ir-192')
        
        # Select specific radial distances for plotting
        r_indices = [1, 2, 4, 5]  # Corresponding to ~1, 2, 5, 7.5 cm
        r_labels = ['1.0 cm', '2.0 cm', '5.0 cm', '7.5 cm']
        
        for idx, (ax, r_idx, r_label) in enumerate(zip(axes.flat, r_indices, r_labels)):
            if r_idx < len(F_r_theta):
                theta_deg = np.degrees(theta)
                ax.plot(theta_deg, F_r_theta[r_idx, :], 'b-', linewidth=2, label='Simulation')
                ax.set_xlabel('Polar angle θ (degrees)')
                ax.set_ylabel('F(r,θ)')
                ax.set_title(f'r = {r_label}')
                ax.grid(True, alpha=0.3)
                ax.set_xlim(0, 180)
                ax.set_ylim(0.5, 1.5)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Anisotropy function plot saved to: {save_path}")
    
    def compare_with_literature(self, r, g_r):
        """Compare simulation results with literature values"""
        print("\n=== TG-43 Parameter Comparison ===")
        
        # Compare g(r) at specific distances
        distances = [1.0, 2.0, 3.0, 5.0, 7.5, 10.0]  # cm
        literature_g_r = [1.0000, 0.9590, 0.9255, 0.8595, 0.7965, 0.7420]
        
        print("\nRadial Dose Function g(r) Comparison:")
        print("Distance(cm) | Simulation | Literature | Difference(%)")
        print("-" * 55)
        
        for dist, lit_val in zip(distances, literature_g_r):
            # Find closest simulated value
            idx = np.argmin(np.abs(r - dist))
            sim_val = g_r[idx]
            diff_percent = (sim_val - lit_val) / lit_val * 100
            
            print(f"{dist:8.1f}     | {sim_val:8.4f}   | {lit_val:8.4f}   | {diff_percent:8.2f}")
    
    def generate_dvh_analysis(self, dose_data, organ_volumes):
        """Generate DVH analysis for OARs"""
        # This would analyze dose-volume histograms for bladder and rectum
        print("\n=== DVH Analysis ===")
        print("DVH analysis functionality to be implemented")
        print("This would calculate D_mean, D_max, D_2cc for OARs")

def main():
    """Main analysis function"""
    print("HDR Brachytherapy Monte Carlo Analysis")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = TG43Analyzer("output/")
    
    # Load and analyze TG-43 validation data
    print("\nAnalyzing TG-43 validation results...")
    dose_data = analyzer.load_dose_distribution("dose_distribution_run_001.dat")
    
    if dose_data is not None:
        # Calculate and plot g(r)
        r, g_r = analyzer.calculate_radial_dose_function(dose_data)
        if r is not None:
            analyzer.plot_radial_dose_function(r, g_r)
            analyzer.compare_with_literature(r, g_r)
        
        # Calculate and plot F(r,θ)
        r_anis, theta_anis, F_r_theta = analyzer.calculate_anisotropy_function(dose_data)
        if r_anis is not None:
            analyzer.plot_anisotropy_function(r_anis, theta_anis, F_r_theta)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()

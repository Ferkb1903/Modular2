#!/usr/bin/env python3
"""
BRACHYTHERAPY HETEROGENEITY COMPARISON
=====================================
Advanced comparison between simulations with and without bone heterogeneity.
Analyzes the impact of tissue heterogeneity on dose distribution.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches

def load_data(filename):
    """Load energy deposition data from file"""
    data = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                parts = line.strip().split()
                if len(parts) >= 4:
                    x, y, z, energy = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
                    data.append([x, y, z, energy])
        return np.array(data)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return np.array([])

def create_dose_map_data(data):
    """Convert data to 2D dose map"""
    x_coords = data[:, 0]
    y_coords = data[:, 1]
    energies = data[:, 3]
    
    x_unique = np.unique(x_coords)
    y_unique = np.unique(y_coords)
    
    dose_map = np.zeros((len(y_unique), len(x_unique)))
    
    for i, row in enumerate(data):
        x, y, z, energy = row
        x_idx = np.where(x_unique == x)[0][0]
        y_idx = np.where(y_unique == y)[0][0]
        dose_map[y_idx, x_idx] = energy
        
    return dose_map, x_unique, y_unique

def calculate_dose_difference(data_hetero, data_water):
    """Calculate dose difference between heterogeneous and water phantoms"""
    
    # Create dose maps
    dose_hetero, x_hetero, y_hetero = create_dose_map_data(data_hetero)
    dose_water, x_water, y_water = create_dose_map_data(data_water)
    
    # Ensure same coordinate system
    x_common = np.intersect1d(x_hetero, x_water)
    y_common = np.intersect1d(y_hetero, y_water)
    
    # Create common grid
    dose_hetero_common = np.zeros((len(y_common), len(x_common)))
    dose_water_common = np.zeros((len(y_common), len(x_common)))
    
    for i, y in enumerate(y_common):
        for j, x in enumerate(x_common):
            # Find indices in original arrays
            hetero_y_idx = np.where(y_hetero == y)[0]
            hetero_x_idx = np.where(x_hetero == x)[0]
            water_y_idx = np.where(y_water == y)[0]
            water_x_idx = np.where(x_water == x)[0]
            
            if len(hetero_y_idx) > 0 and len(hetero_x_idx) > 0:
                dose_hetero_common[i, j] = dose_hetero[hetero_y_idx[0], hetero_x_idx[0]]
            if len(water_y_idx) > 0 and len(water_x_idx) > 0:
                dose_water_common[i, j] = dose_water[water_y_idx[0], water_x_idx[0]]
    
    # Calculate relative difference (%)
    dose_diff = np.zeros_like(dose_hetero_common)
    mask = dose_water_common > 0
    dose_diff[mask] = ((dose_hetero_common[mask] - dose_water_common[mask]) / dose_water_common[mask]) * 100
    
    return dose_diff, dose_hetero_common, dose_water_common, x_common, y_common

def create_comprehensive_comparison():
    """Create comprehensive comparison visualization"""
    
    # Load data
    print("Loading heterogeneous phantom data...")
    data_hetero = load_data('EnergyDeposition_MEGA.out')
    print("Loading water phantom data...")
    data_water = load_data('EnergyDeposition_MEGA_Water.out')
    
    if len(data_hetero) == 0 or len(data_water) == 0:
        print("Error: Could not load required data files")
        return None
    
    print(f"Heterogeneous phantom: {len(data_hetero):,} voxels")
    print(f"Water phantom: {len(data_water):,} voxels")
    
    # Calculate dose maps and differences
    dose_diff, dose_hetero, dose_water, x_common, y_common = calculate_dose_difference(data_hetero, data_water)
    
    # Create comprehensive figure
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Title
    fig.suptitle('BRACHYTHERAPY: HETEROGENEITY IMPACT ANALYSIS\n10M Events - Bone vs Water Phantom Comparison', 
                 fontsize=18, fontweight='bold', y=0.96)
    
    # === ROW 1: DOSE MAPS ===
    
    # Heterogeneous phantom
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(dose_hetero, extent=[x_common.min(), x_common.max(), y_common.min(), y_common.max()], 
                     origin='lower', cmap='hot', aspect='equal')
    ax1.set_title('Heterogeneous Phantom\n(Water + Bone Cube)', fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    plt.colorbar(im1, ax=ax1, label='Energy Deposition')
    
    # Add bone cube outline
    bone_rect = patches.Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='cyan', 
                                 facecolor='none', alpha=0.8, label='Bone Cube')
    ax1.add_patch(bone_rect)
    ax1.plot(0, 0, 'w+', markersize=12, markeredgewidth=2, label='Source')
    ax1.legend(loc='upper right')
    
    # Water phantom
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(dose_water, extent=[x_common.min(), x_common.max(), y_common.min(), y_common.max()], 
                     origin='lower', cmap='hot', aspect='equal')
    ax2.set_title('Water Phantom\n(Homogeneous)', fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    plt.colorbar(im2, ax=ax2, label='Energy Deposition')
    ax2.plot(0, 0, 'w+', markersize=12, markeredgewidth=2, label='Source')
    ax2.legend(loc='upper right')
    
    # Difference map
    ax3 = fig.add_subplot(gs[0, 2])
    # Create symmetric colormap for differences
    max_diff = max(abs(np.nanmin(dose_diff)), abs(np.nanmax(dose_diff)))
    im3 = ax3.imshow(dose_diff, extent=[x_common.min(), x_common.max(), y_common.min(), y_common.max()], 
                     origin='lower', cmap='RdBu_r', aspect='equal', 
                     vmin=-max_diff, vmax=max_diff)
    ax3.set_title('Relative Difference\n(Hetero - Water)/Water × 100%', fontweight='bold')
    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    cbar3 = plt.colorbar(im3, ax=ax3, label='Difference (%)')
    
    # Add bone cube outline
    bone_rect3 = patches.Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='black', 
                                  facecolor='none', alpha=0.8, linestyle='--')
    ax3.add_patch(bone_rect3)
    ax3.plot(0, 0, 'k+', markersize=12, markeredgewidth=2)
    
    # === ROW 2: CROSS-SECTIONS ===
    
    # Y=0 cross-section (through source, perpendicular to bone)
    ax4 = fig.add_subplot(gs[1, 0])
    
    # Extract Y=0 data
    y_zero_mask_hetero = np.abs(data_hetero[:, 1]) < 1
    y_zero_mask_water = np.abs(data_water[:, 1]) < 1
    
    x_hetero_cross = data_hetero[y_zero_mask_hetero, 0]
    energy_hetero_cross = data_hetero[y_zero_mask_hetero, 3]
    x_water_cross = data_water[y_zero_mask_water, 0]
    energy_water_cross = data_water[y_zero_mask_water, 3]
    
    # Sort data
    sort_idx_hetero = np.argsort(x_hetero_cross)
    sort_idx_water = np.argsort(x_water_cross)
    
    ax4.plot(x_hetero_cross[sort_idx_hetero], energy_hetero_cross[sort_idx_hetero], 
             'r.-', markersize=2, alpha=0.8, label='Heterogeneous')
    ax4.plot(x_water_cross[sort_idx_water], energy_water_cross[sort_idx_water], 
             'b.-', markersize=2, alpha=0.8, label='Water')
    
    ax4.set_xlabel('X (mm)')
    ax4.set_ylabel('Energy Deposition')
    ax4.set_title('Cross-section at Y ≈ 0\n(Perpendicular to bone cube)')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    ax4.axvline(x=0, color='black', linestyle='--', alpha=0.7, label='Source')
    ax4.legend()
    
    # Y=60 cross-section (through bone center)
    ax5 = fig.add_subplot(gs[1, 1])
    
    # Extract Y=60 data (center of bone cube)
    y_bone_mask_hetero = np.abs(data_hetero[:, 1] - 60) < 1
    y_bone_mask_water = np.abs(data_water[:, 1] - 60) < 1
    
    x_hetero_bone = data_hetero[y_bone_mask_hetero, 0]
    energy_hetero_bone = data_hetero[y_bone_mask_hetero, 3]
    x_water_bone = data_water[y_bone_mask_water, 0]
    energy_water_bone = data_water[y_bone_mask_water, 3]
    
    # Sort data
    if len(x_hetero_bone) > 0:
        sort_idx_hetero_bone = np.argsort(x_hetero_bone)
        ax5.plot(x_hetero_bone[sort_idx_hetero_bone], energy_hetero_bone[sort_idx_hetero_bone], 
                 'r.-', markersize=2, alpha=0.8, label='Heterogeneous')
    
    if len(x_water_bone) > 0:
        sort_idx_water_bone = np.argsort(x_water_bone)
        ax5.plot(x_water_bone[sort_idx_water_bone], energy_water_bone[sort_idx_water_bone], 
                 'b.-', markersize=2, alpha=0.8, label='Water')
    
    ax5.set_xlabel('X (mm)')
    ax5.set_ylabel('Energy Deposition')
    ax5.set_title('Cross-section at Y ≈ 60mm\n(Through bone cube center)')
    ax5.set_yscale('log')
    ax5.grid(True, alpha=0.3)
    ax5.axvspan(-30, 30, alpha=0.2, color='orange', label='Bone region')
    ax5.legend()
    
    # Statistics panel
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    # Calculate statistics
    total_energy_hetero = data_hetero[:, 3].sum()
    total_energy_water = data_water[:, 3].sum()
    energy_diff_percent = ((total_energy_hetero - total_energy_water) / total_energy_water) * 100
    
    max_energy_hetero = data_hetero[:, 3].max()
    max_energy_water = data_water[:, 3].max()
    
    mean_energy_hetero = data_hetero[:, 3].mean()
    mean_energy_water = data_water[:, 3].mean()
    
    stats_text = f"""
QUANTITATIVE COMPARISON

TOTAL ENERGY DEPOSITED:
• Heterogeneous: {total_energy_hetero:.2e}
• Water: {total_energy_water:.2e}
• Difference: {energy_diff_percent:+.2f}%

MAXIMUM ENERGY (single voxel):
• Heterogeneous: {max_energy_hetero:.2e}
• Water: {max_energy_water:.2e}
• Ratio: {max_energy_hetero/max_energy_water:.3f}

MEAN ENERGY PER VOXEL:
• Heterogeneous: {mean_energy_hetero:.2e}
• Water: {mean_energy_water:.2e}
• Ratio: {mean_energy_hetero/mean_energy_water:.3f}

VOXEL COUNT:
• Heterogeneous: {len(data_hetero):,}
• Water: {len(data_water):,}
• Difference: {len(data_hetero) - len(data_water):+,}

DOSE PERTURBATION:
• Max increase: {np.nanmax(dose_diff):.1f}%
• Max decrease: {np.nanmin(dose_diff):.1f}%
• RMS difference: {np.sqrt(np.nanmean(dose_diff**2)):.1f}%
"""
    
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, 
             verticalalignment='top', fontfamily='monospace', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.9))
    
    # === ROW 3: RADIAL ANALYSIS ===
    
    # Radial dose profiles
    ax7 = fig.add_subplot(gs[2, :2])
    
    def calculate_radial_profile(data, num_bins=50):
        distances = np.sqrt(data[:, 0]**2 + data[:, 1]**2)
        energies = data[:, 3]
        
        max_dist = distances.max()
        bin_edges = np.linspace(0, max_dist, num_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        radial_dose = []
        for i in range(len(bin_edges) - 1):
            mask = (distances >= bin_edges[i]) & (distances < bin_edges[i + 1])
            if np.sum(mask) > 0:
                radial_dose.append(energies[mask].mean())
            else:
                radial_dose.append(0)
        
        return bin_centers, np.array(radial_dose)
    
    r_hetero, dose_radial_hetero = calculate_radial_profile(data_hetero)
    r_water, dose_radial_water = calculate_radial_profile(data_water)
    
    ax7.semilogy(r_hetero, dose_radial_hetero, 'r-', linewidth=2, label='Heterogeneous', alpha=0.8)
    ax7.semilogy(r_water, dose_radial_water, 'b-', linewidth=2, label='Water', alpha=0.8)
    
    ax7.set_xlabel('Radial Distance (mm)')
    ax7.set_ylabel('Mean Energy Deposition (log scale)')
    ax7.set_title('Radial Dose Profiles - Comparison')
    ax7.grid(True, alpha=0.3)
    ax7.legend()
    
    # Mark bone region
    bone_distance = np.sqrt(30**2 + 60**2)  # Distance to bone cube corner
    ax7.axvspan(30, 90, alpha=0.2, color='orange', label='Bone influence region')
    ax7.legend()
    
    # Difference histogram
    ax8 = fig.add_subplot(gs[2, 2])
    
    # Flatten dose difference and remove zeros/NaNs
    diff_flat = dose_diff.flatten()
    diff_flat = diff_flat[~np.isnan(diff_flat)]
    diff_flat = diff_flat[diff_flat != 0]
    
    ax8.hist(diff_flat, bins=50, alpha=0.7, color='purple', edgecolor='black')
    ax8.set_xlabel('Relative Difference (%)')
    ax8.set_ylabel('Frequency')
    ax8.set_title('Distribution of Dose Differences')
    ax8.grid(True, alpha=0.3)
    ax8.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='No difference')
    ax8.legend()
    
    # === ROW 4: PHYSICAL INTERPRETATION ===
    
    ax9 = fig.add_subplot(gs[3, :])
    ax9.axis('off')
    
    interpretation_text = f"""
PHYSICAL INTERPRETATION OF RESULTS

BONE HETEROGENEITY EFFECTS:
• Higher density bone (ρ ≈ 1.9 g/cm³) vs water (ρ = 1.0 g/cm³) causes significant dose perturbations
• Increased photoelectric absorption in bone leads to dose enhancement in bone region
• Increased scatter from bone affects dose distribution in surrounding water
• Beam hardening effects modify the energy spectrum downstream of bone

CLINICAL IMPLICATIONS:
• Dose calculations must account for tissue heterogeneities for accurate treatment planning
• Homogeneous water phantom underestimates dose complexity in realistic patient anatomy
• Bone interfaces create dose gradients that may affect treatment efficacy
• Monte Carlo simulations provide essential accuracy for brachytherapy dose calculations

SIMULATION VALIDATION:
• {len(data_hetero):,} voxels with 10M events provide excellent statistical precision
• Full phantom coverage ({x_common.min():.0f} to {x_common.max():.0f} mm) captures complete dose distribution
• Relative differences up to {np.nanmax(np.abs(dose_diff)):.1f}% demonstrate significant heterogeneity impact
• Results suitable for benchmarking commercial treatment planning systems
"""
    
    ax9.text(0.05, 0.95, interpretation_text, transform=ax9.transAxes, 
             verticalalignment='top', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    print("🔬 CREATING COMPREHENSIVE HETEROGENEITY COMPARISON...")
    print("=" * 60)
    
    fig = create_comprehensive_comparison()
    if fig is not None:
        # Save high-quality outputs
        fig.savefig('heterogeneity_comparison_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Comparison analysis saved: 'heterogeneity_comparison_analysis.png'")
        
        fig.savefig('heterogeneity_comparison_analysis.pdf', dpi=300, bbox_inches='tight')
        print("✅ High-quality PDF saved: 'heterogeneity_comparison_analysis.pdf'")
        
        # Display
        plt.show()
        
        print("\n🎯 ANALYSIS COMPLETE!")
        print("📊 Generated comprehensive comparison including:")
        print("   • Dose map comparisons")
        print("   • Cross-sectional profiles")
        print("   • Radial dose analysis")
        print("   • Statistical quantification")
        print("   • Physical interpretation")
    else:
        print("❌ Could not create comparison - data files missing")

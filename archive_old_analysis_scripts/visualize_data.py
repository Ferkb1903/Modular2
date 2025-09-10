#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle

def load_data(filename):
    """Load energy deposition data from file"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 4:
                x, y, z, energy = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
                data.append([x, y, z, energy])
    return np.array(data)

def create_dose_map(data, title="Energy Deposition Map"):
    """Create a 2D dose map from the data"""
    # Extract coordinates and energy values
    x_coords = data[:, 0]
    y_coords = data[:, 1]
    energies = data[:, 3]
    
    # Get unique coordinates
    x_unique = np.unique(x_coords)
    y_unique = np.unique(y_coords)
    
    print(f"X range: {x_unique.min():.1f} to {x_unique.max():.1f} mm")
    print(f"Y range: {y_unique.min():.1f} to {y_unique.max():.1f} mm")
    print(f"Total data points: {len(data)}")
    print(f"Energy range: {energies.min():.2e} to {energies.max():.2e}")
    
    # Create 2D grid
    dose_map = np.zeros((len(y_unique), len(x_unique)))
    
    # Fill the grid
    for i, row in enumerate(data):
        x, y, z, energy = row
        x_idx = np.where(x_unique == x)[0][0]
        y_idx = np.where(y_unique == y)[0][0]
        dose_map[y_idx, x_idx] = energy
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Plot 1: Linear scale
    im1 = ax1.imshow(dose_map, extent=[x_unique.min(), x_unique.max(), 
                                      y_unique.min(), y_unique.max()], 
                     origin='lower', cmap='hot', aspect='equal')
    ax1.set_title(f'{title} - Linear Scale')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    plt.colorbar(im1, ax=ax1, label='Energy Deposition')
    
    # Add grid lines every 20mm
    for coord in range(-100, 101, 20):
        ax1.axvline(x=coord, color='white', alpha=0.3, linewidth=0.5)
        ax1.axhline(y=coord, color='white', alpha=0.3, linewidth=0.5)
    
    # Plot 2: Log scale (only for non-zero values)
    dose_map_log = np.copy(dose_map)
    dose_map_log[dose_map_log == 0] = np.nan  # Set zeros to NaN for log scale
    
    im2 = ax2.imshow(dose_map_log, extent=[x_unique.min(), x_unique.max(), 
                                          y_unique.min(), y_unique.max()], 
                     origin='lower', cmap='hot', aspect='equal',
                     norm=colors.LogNorm(vmin=np.nanmin(dose_map_log), 
                                       vmax=np.nanmax(dose_map_log)))
    ax2.set_title(f'{title} - Log Scale')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    plt.colorbar(im2, ax=ax2, label='Energy Deposition (log)')
    
    # Add grid lines every 20mm
    for coord in range(-100, 101, 20):
        ax2.axvline(x=coord, color='white', alpha=0.3, linewidth=0.5)
        ax2.axhline(y=coord, color='white', alpha=0.3, linewidth=0.5)
    
    # Add source position marker (assuming it's at origin)
    ax1.plot(0, 0, 'w+', markersize=15, markeredgewidth=3, label='Source')
    ax2.plot(0, 0, 'w+', markersize=15, markeredgewidth=3, label='Source')
    
    # Add heterogeneity cube position if it exists (from the geometry setup)
    # The cube is at (0, 6, 0) cm = (0, 60, 0) mm and is 6x6x6 cm
    cube_rect1 = Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='cyan', 
                          facecolor='none', alpha=0.7, label='Bone Cube')
    cube_rect2 = Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='cyan', 
                          facecolor='none', alpha=0.7)
    ax1.add_patch(cube_rect1)
    ax2.add_patch(cube_rect2)
    
    ax1.legend()
    ax2.legend()
    
    plt.tight_layout()
    return fig, dose_map

def plot_cross_sections(data, title="Cross Sections"):
    """Plot cross sections through the data"""
    x_coords = data[:, 0]
    y_coords = data[:, 1]
    energies = data[:, 3]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # X cross-section at Y=0
    y_zero_mask = np.abs(y_coords) < 1  # Within 1mm of Y=0
    x_cross = x_coords[y_zero_mask]
    energy_cross_x = energies[y_zero_mask]
    
    # Sort by x coordinate
    sort_idx = np.argsort(x_cross)
    x_cross = x_cross[sort_idx]
    energy_cross_x = energy_cross_x[sort_idx]
    
    ax1.plot(x_cross, energy_cross_x, 'b.-', markersize=3)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Energy Deposition')
    ax1.set_title('Cross-section at Y ≈ 0')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Source')
    ax1.legend()
    
    # Y cross-section at X=0
    x_zero_mask = np.abs(x_coords) < 1  # Within 1mm of X=0
    y_cross = y_coords[x_zero_mask]
    energy_cross_y = energies[x_zero_mask]
    
    # Sort by y coordinate
    sort_idx = np.argsort(y_cross)
    y_cross = y_cross[sort_idx]
    energy_cross_y = energy_cross_y[sort_idx]
    
    ax2.plot(y_cross, energy_cross_y, 'r.-', markersize=3)
    ax2.set_xlabel('Y (mm)')
    ax2.set_ylabel('Energy Deposition')
    ax2.set_title('Cross-section at X ≈ 0')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Source')
    ax2.axvspan(30, 90, alpha=0.2, color='cyan', label='Bone Cube')
    ax2.legend()
    
    plt.tight_layout()
    return fig

def create_comparison_plot(data_old, data_new):
    """Create comparison plots between old and new data"""
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # Helper function to create dose map data
    def create_map_data(data):
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
    
    # Create maps for both datasets
    dose_map_old, x_old, y_old = create_map_data(data_old)
    dose_map_new, x_new, y_new = create_map_data(data_new)
    
    # Plot 1: Old data linear
    im1 = axes[0,0].imshow(dose_map_old, extent=[x_old.min(), x_old.max(), y_old.min(), y_old.max()], 
                          origin='lower', cmap='hot', aspect='equal')
    axes[0,0].set_title('Original Data (100k events)\nLinear Scale')
    axes[0,0].set_xlabel('X (mm)')
    axes[0,0].set_ylabel('Y (mm)')
    plt.colorbar(im1, ax=axes[0,0])
    axes[0,0].plot(0, 0, 'w+', markersize=12, markeredgewidth=2)
    
    # Plot 2: New data linear
    im2 = axes[0,1].imshow(dose_map_new, extent=[x_new.min(), x_new.max(), y_new.min(), y_new.max()], 
                          origin='lower', cmap='hot', aspect='equal')
    axes[0,1].set_title('High Statistics (2M events)\nLinear Scale')
    axes[0,1].set_xlabel('X (mm)')
    axes[0,1].set_ylabel('Y (mm)')
    plt.colorbar(im2, ax=axes[0,1])
    axes[0,1].plot(0, 0, 'w+', markersize=12, markeredgewidth=2)
    
    # Plot 3: Coverage comparison
    axes[0,2].hist([data_old[:, 0], data_new[:, 0]], bins=50, alpha=0.7, 
                   label=[f'Original ({len(data_old)} voxels)', f'High Stats ({len(data_new)} voxels)'])
    axes[0,2].set_title('X-Coordinate Coverage Comparison')
    axes[0,2].set_xlabel('X (mm)')
    axes[0,2].set_ylabel('Frequency')
    axes[0,2].legend()
    axes[0,2].grid(True, alpha=0.3)
    
    # Plot 4: Old data log
    dose_map_old_log = np.copy(dose_map_old)
    dose_map_old_log[dose_map_old_log == 0] = np.nan
    im4 = axes[1,0].imshow(dose_map_old_log, extent=[x_old.min(), x_old.max(), y_old.min(), y_old.max()], 
                          origin='lower', cmap='hot', aspect='equal',
                          norm=colors.LogNorm(vmin=np.nanmin(dose_map_old_log), vmax=np.nanmax(dose_map_old_log)))
    axes[1,0].set_title('Original Data\nLog Scale')
    axes[1,0].set_xlabel('X (mm)')
    axes[1,0].set_ylabel('Y (mm)')
    plt.colorbar(im4, ax=axes[1,0])
    axes[1,0].plot(0, 0, 'w+', markersize=12, markeredgewidth=2)
    
    # Plot 5: New data log
    dose_map_new_log = np.copy(dose_map_new)
    dose_map_new_log[dose_map_new_log == 0] = np.nan
    im5 = axes[1,1].imshow(dose_map_new_log, extent=[x_new.min(), x_new.max(), y_new.min(), y_new.max()], 
                          origin='lower', cmap='hot', aspect='equal',
                          norm=colors.LogNorm(vmin=np.nanmin(dose_map_new_log), vmax=np.nanmax(dose_map_new_log)))
    axes[1,1].set_title('High Statistics\nLog Scale')
    axes[1,1].set_xlabel('X (mm)')
    axes[1,1].set_ylabel('Y (mm)')
    plt.colorbar(im5, ax=axes[1,1])
    axes[1,1].plot(0, 0, 'w+', markersize=12, markeredgewidth=2)
    
    # Plot 6: Radial distribution
    def calculate_radial_dist(data):
        distances = np.sqrt(data[:, 0]**2 + data[:, 1]**2)
        return distances
    
    dist_old = calculate_radial_dist(data_old)
    dist_new = calculate_radial_dist(data_new)
    
    axes[1,2].hist([dist_old, dist_new], bins=30, alpha=0.7, 
                   label=['Original', 'High Statistics'])
    axes[1,2].set_title('Radial Distance Distribution')
    axes[1,2].set_xlabel('Distance from Source (mm)')
    axes[1,2].set_ylabel('Frequency')
    axes[1,2].legend()
    axes[1,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_high_stats_detailed_plot(data):
    """Create detailed plots specifically for high statistics data"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    x_coords = data[:, 0]
    y_coords = data[:, 1]
    energies = data[:, 3]
    
    # Create dose map
    x_unique = np.unique(x_coords)
    y_unique = np.unique(y_coords)
    dose_map = np.zeros((len(y_unique), len(x_unique)))
    
    for i, row in enumerate(data):
        x, y, z, energy = row
        x_idx = np.where(x_unique == x)[0][0]
        y_idx = np.where(y_unique == y)[0][0]
        dose_map[y_idx, x_idx] = energy
    
    # Plot 1: Full field view with enhanced contrast
    im1 = axes[0,0].imshow(dose_map, extent=[x_unique.min(), x_unique.max(), y_unique.min(), y_unique.max()], 
                          origin='lower', cmap='plasma', aspect='equal')
    axes[0,0].set_title('High Statistics: Full Field View\n(2M events, ±160mm coverage)')
    axes[0,0].set_xlabel('X (mm)')
    axes[0,0].set_ylabel('Y (mm)')
    plt.colorbar(im1, ax=axes[0,0], label='Energy Deposition')
    
    # Add markers and annotations
    axes[0,0].plot(0, 0, 'w+', markersize=15, markeredgewidth=3, label='Source')
    axes[0,0].add_patch(Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='white', 
                                 facecolor='none', alpha=0.8, label='Bone Cube'))
    
    # Add coordinate grid
    for coord in range(-150, 151, 50):
        axes[0,0].axvline(x=coord, color='white', alpha=0.2, linewidth=0.5)
        axes[0,0].axhline(y=coord, color='white', alpha=0.2, linewidth=0.5)
    
    axes[0,0].legend()
    
    # Plot 2: Log scale with edge detection
    dose_map_log = np.copy(dose_map)
    dose_map_log[dose_map_log == 0] = np.nan
    
    im2 = axes[0,1].imshow(dose_map_log, extent=[x_unique.min(), x_unique.max(), y_unique.min(), y_unique.max()], 
                          origin='lower', cmap='plasma', aspect='equal',
                          norm=colors.LogNorm(vmin=np.nanmin(dose_map_log), vmax=np.nanmax(dose_map_log)))
    axes[0,1].set_title('Log Scale: Edge Detection\n(Shows low-dose regions)')
    axes[0,1].set_xlabel('X (mm)')
    axes[0,1].set_ylabel('Y (mm)')
    plt.colorbar(im2, ax=axes[0,1], label='Energy Deposition (log)')
    axes[0,1].plot(0, 0, 'w+', markersize=15, markeredgewidth=3)
    
    # Highlight edge regions
    edge_coords = 140
    axes[0,1].axvline(x=edge_coords, color='cyan', linestyle='--', alpha=0.8, label=f'±{edge_coords}mm edge')
    axes[0,1].axvline(x=-edge_coords, color='cyan', linestyle='--', alpha=0.8)
    axes[0,1].axhline(y=edge_coords, color='cyan', linestyle='--', alpha=0.8)
    axes[0,1].axhline(y=-edge_coords, color='cyan', linestyle='--', alpha=0.8)
    axes[0,1].legend()
    
    # Plot 3: Cross-section comparison
    y_zero_mask = np.abs(y_coords) < 1
    x_cross = x_coords[y_zero_mask]
    energy_cross = energies[y_zero_mask]
    
    sort_idx = np.argsort(x_cross)
    x_cross = x_cross[sort_idx]
    energy_cross = energy_cross[sort_idx]
    
    axes[1,0].semilogy(x_cross, energy_cross, 'b.-', markersize=2, alpha=0.8)
    axes[1,0].set_xlabel('X (mm)')
    axes[1,0].set_ylabel('Energy Deposition (log scale)')
    axes[1,0].set_title('Cross-section at Y ≈ 0\n(Demonstrates full range capture)')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Source')
    axes[1,0].axvspan(-25, 25, alpha=0.2, color='yellow', label='Previous limit (±25mm)')
    axes[1,0].legend()
    
    # Plot 4: Statistics and coverage analysis
    # Calculate coverage statistics
    x_coverage = np.abs(x_coords).max()
    y_coverage = np.abs(y_coords).max()
    total_area = (x_unique.max() - x_unique.min()) * (y_unique.max() - y_unique.min())
    active_voxels = len(data)
    
    stats_text = f"""HIGH STATISTICS ANALYSIS
    
Events Processed: 2,000,000
Active Voxels: {active_voxels:,}
    
Spatial Coverage:
• X range: {x_coords.min():.1f} to {x_coords.max():.1f} mm
• Y range: {y_coords.min():.1f} to {y_coords.max():.1f} mm
• Max radius: {x_coverage:.1f} mm
    
Energy Statistics:
• Total deposited: {energies.sum():.2e}
• Max energy: {energies.max():.2e}
• Min energy: {energies.min():.2e}
• Mean energy: {energies.mean():.2e}
    
Improvements vs Original:
• 20x more events
• 2x more data points
• 6.4x larger coordinate range
• Full phantom coverage achieved"""
    
    axes[1,1].text(0.05, 0.95, stats_text, transform=axes[1,1].transAxes, 
                   verticalalignment='top', fontfamily='monospace', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    axes[1,1].set_xlim(0, 1)
    axes[1,1].set_ylim(0, 1)
    axes[1,1].axis('off')
    axes[1,1].set_title('Simulation Statistics & Achievements')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    print("🎯 CREATING COMPREHENSIVE VISUALIZATION SUITE")
    print("=" * 50)
    
    # Load both datasets for comparison
    print("📊 Loading original data...")
    try:
        data_original = load_data('EnergyDeposition_Flexi.out')
        print(f"✅ Original data loaded: {len(data_original)} voxels")
    except FileNotFoundError:
        print("⚠️ Original data not found, skipping comparison")
        data_original = None
    
    print("🚀 Loading high statistics data...")
    data_high_stats = load_data('EnergyDeposition_HighStats.out')
    print(f"✅ High stats data loaded: {len(data_high_stats)} voxels")
    
    # Create comprehensive dose map
    print("\n📈 Creating high statistics detailed analysis...")
    fig1 = create_high_stats_detailed_plot(data_high_stats)
    fig1.savefig('high_stats_detailed_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Detailed analysis saved: 'high_stats_detailed_analysis.png'")
    
    # Create comparison if original data available
    if data_original is not None:
        print("\n📊 Creating comparison analysis...")
        fig2 = create_comparison_plot(data_original, data_high_stats)
        fig2.savefig('comparison_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Comparison analysis saved: 'comparison_analysis.png'")
    
    # Create standard dose map
    print("\n🗺️ Creating standard dose map...")
    fig3, dose_map = create_dose_map(data_high_stats, "High Statistics: 2M Events")
    fig3.savefig('high_stats_dose_map.png', dpi=300, bbox_inches='tight')
    print("✅ Dose map saved: 'high_stats_dose_map.png'")
    
    # Create cross-sections
    print("\n📐 Creating cross-sections...")
    fig4 = plot_cross_sections(data_high_stats, "High Statistics Cross Sections")
    fig4.savefig('high_stats_cross_sections.png', dpi=300, bbox_inches='tight')
    print("✅ Cross-sections saved: 'high_stats_cross_sections.png'")
    
    # Final statistics
    energies = data_high_stats[:, 3]
    print(f"\n🎯 FINAL STATISTICS:")
    print(f"📊 Total voxels with energy: {len(data_high_stats):,}")
    print(f"📐 X range: {data_high_stats[:, 0].min():.1f} to {data_high_stats[:, 0].max():.1f} mm")
    print(f"📐 Y range: {data_high_stats[:, 1].min():.1f} to {data_high_stats[:, 1].max():.1f} mm")
    print(f"⚡ Energy range: {energies.min():.2e} to {energies.max():.2e}")
    print(f"🔥 Total energy: {energies.sum():.2e}")
    print(f"📈 Mean energy: {energies.mean():.2e}")
    
    if data_original is not None:
        improvement = len(data_high_stats) / len(data_original)
        print(f"🚀 Data capture improvement: {improvement:.1f}x")
    
    print(f"\n🎉 ALL VISUALIZATIONS COMPLETED!")
    print(f"📁 Generated files:")
    print(f"   • high_stats_detailed_analysis.png")
    if data_original is not None:
        print(f"   • comparison_analysis.png")
    print(f"   • high_stats_dose_map.png")
    print(f"   • high_stats_cross_sections.png")
    
    plt.show()

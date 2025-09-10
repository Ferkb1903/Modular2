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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Plot 1: Linear scale
    im1 = ax1.imshow(dose_map, extent=[x_unique.min(), x_unique.max(), 
                                      y_unique.min(), y_unique.max()], 
                     origin='lower', cmap='hot', aspect='equal')
    ax1.set_title(f'{title} - Linear Scale')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    plt.colorbar(im1, ax=ax1, label='Energy Deposition')
    
    # Add grid lines and phantom boundaries
    for coord in range(-150, 151, 30):
        ax1.axvline(x=coord, color='white', alpha=0.3, linewidth=0.5)
        ax1.axhline(y=coord, color='white', alpha=0.3, linewidth=0.5)
    
    # Mark phantom boundaries (±150 mm)
    phantom_rect1 = Rectangle((-150, -150), 300, 300, linewidth=2, edgecolor='cyan', 
                             facecolor='none', alpha=0.8, label='Phantom Boundary')
    ax1.add_patch(phantom_rect1)
    
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
    
    # Add grid lines and phantom boundaries
    for coord in range(-150, 151, 30):
        ax2.axvline(x=coord, color='white', alpha=0.3, linewidth=0.5)
        ax2.axhline(y=coord, color='white', alpha=0.3, linewidth=0.5)
    
    phantom_rect2 = Rectangle((-150, -150), 300, 300, linewidth=2, edgecolor='cyan', 
                             facecolor='none', alpha=0.8, label='Phantom Boundary')
    ax2.add_patch(phantom_rect2)
    
    # Add source position marker (assuming it's at origin)
    ax1.plot(0, 0, 'w+', markersize=15, markeredgewidth=3, label='Source')
    ax2.plot(0, 0, 'w+', markersize=15, markeredgewidth=3, label='Source')
    
    # Add heterogeneity cube position (from the geometry setup)
    # The cube is at (0, 6, 0) cm = (0, 60, 0) mm and is 6x6x6 cm
    cube_rect1 = Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='yellow', 
                          facecolor='none', alpha=0.9, label='Bone Cube')
    cube_rect2 = Rectangle((-30, 30), 60, 60, linewidth=2, edgecolor='yellow', 
                          facecolor='none', alpha=0.9)
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
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # X cross-section at Y=0
    y_zero_mask = np.abs(y_coords) < 1  # Within 1mm of Y=0
    x_cross = x_coords[y_zero_mask]
    energy_cross_x = energies[y_zero_mask]
    
    # Sort by x coordinate
    sort_idx = np.argsort(x_cross)
    x_cross = x_cross[sort_idx]
    energy_cross_x = energy_cross_x[sort_idx]
    
    ax1.plot(x_cross, energy_cross_x, 'b.-', markersize=2)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Energy Deposition')
    ax1.set_title('Cross-section at Y ≈ 0')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Source')
    ax1.axvspan(-150, 150, alpha=0.1, color='cyan', label='Phantom')
    ax1.legend()
    
    # Y cross-section at X=0
    x_zero_mask = np.abs(x_coords) < 1  # Within 1mm of X=0
    y_cross = y_coords[x_zero_mask]
    energy_cross_y = energies[x_zero_mask]
    
    # Sort by y coordinate
    sort_idx = np.argsort(y_cross)
    y_cross = y_cross[sort_idx]
    energy_cross_y = energy_cross_y[sort_idx]
    
    ax2.plot(y_cross, energy_cross_y, 'r.-', markersize=2)
    ax2.set_xlabel('Y (mm)')
    ax2.set_ylabel('Energy Deposition')
    ax2.set_title('Cross-section at X ≈ 0')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Source')
    ax2.axvspan(-150, 150, alpha=0.1, color='cyan', label='Phantom')
    ax2.axvspan(30, 90, alpha=0.2, color='orange', label='Bone Cube')
    ax2.legend()
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Load the full coverage data
    print("Loading full coverage data...")
    data_full = load_data('EnergyDeposition_FullCoverage.out')
    
    # Create dose map
    print("\nCreating full coverage dose map...")
    fig1, dose_map = create_dose_map(data_full, "Full Coverage Data (±150mm range)")
    
    # Save the map
    fig1.savefig('dose_map_full_coverage.png', dpi=300, bbox_inches='tight')
    print("Full coverage dose map saved as 'dose_map_full_coverage.png'")
    
    # Create cross-sections
    print("\nCreating cross-sections...")
    fig2 = plot_cross_sections(data_full, "Cross Sections - Full Coverage")
    fig2.savefig('cross_sections_full_coverage.png', dpi=300, bbox_inches='tight')
    print("Cross-sections saved as 'cross_sections_full_coverage.png'")
    
    # Show statistics
    energies = data_full[:, 3]
    print(f"\n=== FULL COVERAGE DATA STATISTICS ===")
    print(f"Total voxels with energy deposition: {len(data_full)}")
    print(f"X coordinate range: {data_full[:, 0].min():.1f} to {data_full[:, 0].max():.1f} mm")
    print(f"Y coordinate range: {data_full[:, 1].min():.1f} to {data_full[:, 1].max():.1f} mm")
    print(f"Energy range: {energies.min():.2e} to {energies.max():.2e}")
    print(f"Total energy deposited: {energies.sum():.2e}")
    print(f"Mean energy per voxel: {energies.mean():.2e}")
    
    plt.show()

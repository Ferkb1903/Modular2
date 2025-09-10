#!/usr/bin/env python3
"""
MAPAS 2D: GEOMETRÍA OPTIMIZADA vs ORIGINAL + DIFERENCIA
Análisis visual de distribución de dosis en braquiterapia

- Mapa 1: Geometría Optimizada (Hueso) 18x18 cm
- Mapa 2: Geometría Original (Agua) 32x32 cm  
- Mapa 3: Diferencia (Optimizada - Original)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.patches as patches

def load_energy_map(filename, title):
    """Cargar datos y crear mapa 2D"""
    print(f"🔄 Cargando {title}...")
    try:
        data = np.loadtxt(filename, skiprows=2)
        
        # Extraer coordenadas únicas
        x_coords = np.unique(data[:, 0])
        y_coords = np.unique(data[:, 1])
        energies = data[:, 3]
        
        print(f"   📏 Dimensiones: {len(x_coords)} x {len(y_coords)}")
        print(f"   📊 Rango X: {x_coords.min():.1f} a {x_coords.max():.1f} cm")
        print(f"   📊 Rango Y: {y_coords.min():.1f} a {y_coords.max():.1f} cm")
        print(f"   ⚡ Energía total: {np.sum(energies):.2e} MeV")
        
        # Crear matriz 2D
        energy_map = np.zeros((len(y_coords), len(x_coords)))
        
        for i, (x, y, z, energy) in enumerate(data):
            x_idx = np.where(x_coords == x)[0][0]
            y_idx = np.where(y_coords == y)[0][0]
            energy_map[y_idx, x_idx] = energy
            
        return energy_map, x_coords, y_coords, energies
        
    except Exception as e:
        print(f"❌ Error cargando {filename}: {e}")
        return None, None, None, None

def create_2d_maps():
    """Crear mapas 2D separados y diferencia"""
    print("🗺️  CREANDO MAPAS 2D: OPTIMIZADA vs ORIGINAL + DIFERENCIA")
    print("=" * 60)
    
    # Cargar datos
    bone_map, bone_x, bone_y, bone_energies = load_energy_map(
        "EnergyDeposition_MEGA_Bone_Optimized.out", 
        "GEOMETRÍA OPTIMIZADA (Hueso)")
    
    water_map, water_x, water_y, water_energies = load_energy_map(
        "../output/EnergyDeposition_MEGA_Water.out", 
        "GEOMETRÍA ORIGINAL (Agua)")
    
    if bone_map is None or water_map is None:
        print("❌ No se pudieron cargar los mapas")
        return
    
    # Crear figura con 3 subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('COMPARACIÓN 2D: GEOMETRÍA OPTIMIZADA vs ORIGINAL', fontsize=16, fontweight='bold')
    
    # 1. Mapa Optimizado (Hueso)
    ax1 = axes[0, 0]
    im1 = ax1.imshow(bone_map, extent=[bone_x.min(), bone_x.max(), bone_y.min(), bone_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=bone_map.max()))
    ax1.set_title('GEOMETRÍA OPTIMIZADA (Hueso)\n18×18 cm phantom', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    # Marcar heterogeneidad (8x8 cm centrada en (0,5))
    het_rect = patches.Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='cyan', 
                                facecolor='none', linestyle='--', label='Heterogeneidad 8×8 cm')
    ax1.add_patch(het_rect)
    ax1.legend()
    
    plt.colorbar(im1, ax=ax1, label='Energía Depositada (MeV)')
    
    # 2. Mapa Original (Agua)
    ax2 = axes[0, 1]
    im2 = ax2.imshow(water_map, extent=[water_x.min(), water_x.max(), water_y.min(), water_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=water_map.max()))
    ax2.set_title('GEOMETRÍA ORIGINAL (Agua)\n32×32 cm phantom homogéneo', fontweight='bold')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    plt.colorbar(im2, ax=ax2, label='Energía Depositada (MeV)')
    
    # 3. Interpolación para diferencia (ajustar tamaños)
    print("\n🔄 Calculando diferencia...")
    
    # Crear grilla común para interpolación
    from scipy.interpolate import RegularGridInterpolator
    
    # Interpolar agua al grid del hueso
    water_interp_func = RegularGridInterpolator((water_y, water_x), water_map, 
                                                bounds_error=False, fill_value=0)
    
    # Crear puntos de interpolación
    bone_xx, bone_yy = np.meshgrid(bone_x, bone_y)
    water_interp = water_interp_func((bone_yy, bone_xx))
    
    # Calcular diferencia
    diff_map = bone_map - water_interp
    
    ax3 = axes[1, 0]
    im3 = ax3.imshow(diff_map, extent=[bone_x.min(), bone_x.max(), bone_y.min(), bone_y.max()],
                     origin='lower', cmap='RdBu_r', vmin=-diff_map.max(), vmax=diff_map.max())
    ax3.set_title('DIFERENCIA\n(Optimizada - Original)', fontweight='bold')
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    
    # Marcar heterogeneidad
    het_rect2 = patches.Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                                 facecolor='none', linestyle='--', label='Heterogeneidad 8×8 cm')
    ax3.add_patch(het_rect2)
    ax3.legend()
    
    plt.colorbar(im3, ax=ax3, label='Diferencia Energía (MeV)')
    
    # 4. Estadísticas
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    stats_text = f"""
ESTADÍSTICAS COMPARATIVAS:

📊 GEOMETRÍA OPTIMIZADA (Hueso):
   • Dimensiones: {len(bone_x)} × {len(bone_y)} voxels
   • Phantom: 18×18×18 cm
   • Heterogeneidad: 8×8×8 cm hueso
   • Energía total: {np.sum(bone_energies):.2e} MeV
   • Energía máxima: {bone_map.max():.2e} MeV

📊 GEOMETRÍA ORIGINAL (Agua):
   • Dimensiones: {len(water_x)} × {len(water_y)} voxels  
   • Phantom: 32×32×32 cm homogéneo
   • Material: Solo agua
   • Energía total: {np.sum(water_energies):.2e} MeV
   • Energía máxima: {water_map.max():.2e} MeV

🎯 COMPARACIÓN:
   • Ratio energía total: {np.sum(bone_energies)/np.sum(water_energies):.2f}
   • Diferencia máxima: {diff_map.max():.2e} MeV
   • Diferencia mínima: {diff_map.min():.2e} MeV
   • Puntos de datos: {len(bone_energies):,} vs {len(water_energies):,}
    """
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('mapas_2d_optimizada_vs_original_diferencia.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Mapas 2D guardados: mapas_2d_optimizada_vs_original_diferencia.png")
    plt.show()

if __name__ == "__main__":
    create_2d_maps()

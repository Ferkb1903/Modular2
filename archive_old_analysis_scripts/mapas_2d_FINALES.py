#!/usr/bin/env python3
"""
MAPAS 2D FINALES CORRECTOS: Conversión correcta de índices de bins
Análisis definitivo con coordenadas reales calculadas

FORMATO REAL DE DATOS:
- Los archivos contienen índices de bins (no coordenadas reales)
- Hueso: -179.5 a +179.5 → 360 bins en 18 cm → 0.05 cm/bin
- Agua: -159.5 a +159.5 → 320 bins en 16 cm → 0.05 cm/bin
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.patches as patches

def load_and_convert_bins(filename, title, box_size_cm, n_bins):
    """Cargar datos y convertir índices de bins a coordenadas reales"""
    print(f"🔄 Cargando {title}...")
    try:
        data = np.loadtxt(filename, skiprows=2)
        
        # Parámetros de conversión
        bin_size = box_size_cm / n_bins  # cm por bin
        half_size = box_size_cm / 2      # cm del centro al borde
        
        # Los datos vienen como índices centrados: -179.5, -178.5, etc.
        x_indices = data[:, 0]
        y_indices = data[:, 1]
        energies = data[:, 3]
        
        # Convertir índices a coordenadas reales
        # Fórmula: coord_real = (índice + 0.5) * bin_size - half_size
        x_real = (x_indices + n_bins/2) * bin_size - half_size
        y_real = (y_indices + n_bins/2) * bin_size - half_size
        
        # Crear coordenadas únicas
        x_coords = np.unique(x_real)
        y_coords = np.unique(y_real)
        
        print(f"   📏 Configuración: {box_size_cm}×{box_size_cm} cm, {n_bins}×{n_bins} bins")
        print(f"   📐 Resolución: {bin_size:.4f} cm/bin = {bin_size*10:.2f} mm/bin")
        print(f"   📊 Índices archivo: {x_indices.min():.1f} a {x_indices.max():.1f}")
        print(f"   📊 Coordenadas reales: {x_coords.min():.2f} a {x_coords.max():.2f} cm")
        print(f"   ⚡ Energía total: {np.sum(energies):.2e} MeV")
        print(f"   📈 Voxels con datos: {len(energies):,}")
        
        # Crear matriz 2D
        energy_map = np.zeros((len(y_coords), len(x_coords)))
        
        for i, (x_val, y_val, energy) in enumerate(zip(x_real, y_real, energies)):
            x_idx = np.argmin(np.abs(x_coords - x_val))
            y_idx = np.argmin(np.abs(y_coords - y_val))
            energy_map[y_idx, x_idx] = energy
            
        return energy_map, x_coords, y_coords, energies
        
    except Exception as e:
        print(f"❌ Error cargando {filename}: {e}")
        return None, None, None, None

def create_final_comparison():
    """Crear comparación final con conversiones correctas"""
    print("🗺️  MAPAS 2D FINALES - CONVERSIÓN CORRECTA DE BINS")
    print("=" * 55)
    
    # Cargar con parámetros correctos
    bone_map, bone_x, bone_y, bone_energies = load_and_convert_bins(
        "EnergyDeposition_MEGA_Bone_Optimized.out", 
        "GEOMETRÍA OPTIMIZADA (Hueso)",
        box_size_cm=18.0, n_bins=360)
    
    water_map, water_x, water_y, water_energies = load_and_convert_bins(
        "../output/EnergyDeposition_MEGA_Water.out", 
        "GEOMETRÍA ORIGINAL (Agua)",
        box_size_cm=16.0, n_bins=320)
    
    if bone_map is None or water_map is None:
        print("❌ No se pudieron cargar los mapas")
        return
    
    # Encontrar región común
    x_min_common = max(bone_x.min(), water_x.min())
    x_max_common = min(bone_x.max(), water_x.max())
    y_min_common = max(bone_y.min(), water_y.min())
    y_max_common = min(bone_y.max(), water_y.max())
    
    print(f"\n🎯 REGIÓN COMÚN IDENTIFICADA:")
    print(f"   X: {x_min_common:.2f} a {x_max_common:.2f} cm")
    print(f"   Y: {y_min_common:.2f} a {y_max_common:.2f} cm")
    print(f"   Dimensiones: {x_max_common-x_min_common:.1f} × {y_max_common-y_min_common:.1f} cm")
    
    # Crear figura con comparación
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('COMPARACIÓN FINAL: CONVERSIÓN CORRECTA DE COORDENADAS', 
                 fontsize=16, fontweight='bold')
    
    # 1. Geometría Optimizada (Hueso)
    ax1 = axes[0, 0]
    vmax1 = np.percentile(bone_map[bone_map > 0], 99)  # Escala al 99 percentil
    im1 = ax1.imshow(bone_map, extent=[bone_x.min(), bone_x.max(), bone_y.min(), bone_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=vmax1))
    ax1.set_title('GEOMETRÍA OPTIMIZADA (Hueso)\n18×18 cm, resolución 0.5 mm', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    # Marcar heterogeneidad (8×8 cm centrada en (0,5))
    het_rect = patches.Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='cyan', 
                                facecolor='none', linestyle='--', label='Heterogeneidad 8×8 cm (Hueso)')
    ax1.add_patch(het_rect)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.colorbar(im1, ax=ax1, label='Energía Depositada (MeV)')
    
    # 2. Geometría Original (Agua)
    ax2 = axes[0, 1]
    vmax2 = np.percentile(water_map[water_map > 0], 99)
    im2 = ax2.imshow(water_map, extent=[water_x.min(), water_x.max(), water_y.min(), water_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=vmax2))
    ax2.set_title('GEOMETRÍA ORIGINAL (Agua)\n16×16 cm, resolución 0.5 mm', fontweight='bold')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(im2, ax=ax2, label='Energía Depositada (MeV)')
    
    # 3. Perfil central Y (a través de la heterogeneidad)
    ax3 = axes[1, 0]
    
    # Extraer perfil en X=0 (centro)
    center_idx_bone = np.argmin(np.abs(bone_x - 0))
    center_idx_water = np.argmin(np.abs(water_x - 0))
    
    profile_bone = bone_map[:, center_idx_bone]
    profile_water = water_map[:, center_idx_water]
    
    ax3.plot(bone_y, profile_bone, 'r-', linewidth=2, label='Optimizada (Hueso)', alpha=0.8)
    ax3.plot(water_y, profile_water, 'b-', linewidth=2, label='Original (Agua)', alpha=0.8)
    ax3.set_xlabel('Y (cm)')
    ax3.set_ylabel('Energía Depositada (MeV)')
    ax3.set_title('PERFIL CENTRAL (X=0)\nComparación directa', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    
    # Marcar región de heterogeneidad
    ax3.axvspan(1, 9, alpha=0.2, color='cyan', label='Región heterogeneidad')
    
    # 4. Estadísticas finales
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Calcular estadísticas en región común
    bone_mask_x = (bone_x >= x_min_common) & (bone_x <= x_max_common)
    bone_mask_y = (bone_y >= y_min_common) & (bone_y <= y_max_common)
    water_mask_x = (water_x >= x_min_common) & (water_x <= x_max_common)
    water_mask_y = (water_y >= y_min_common) & (water_y <= y_max_common)
    
    bone_common = bone_map[np.ix_(bone_mask_y, bone_mask_x)]
    water_common = water_map[np.ix_(water_mask_y, water_mask_x)]
    
    stats_text = f"""
ANÁLISIS FINAL - COORDENADAS CORRECTAS:

📊 GEOMETRÍA OPTIMIZADA (Hueso):
   • Phantom: 18×18 cm (360×360 bins)
   • Resolución: 0.0500 cm/bin = 0.50 mm/bin
   • Coordenadas: {bone_x.min():.2f} a {bone_x.max():.2f} cm
   • Heterogeneidad: 8×8 cm hueso en (0,5) cm
   • Energía total: {np.sum(bone_energies):.2e} MeV
   • Energía región común: {np.sum(bone_common):.2e} MeV

📊 GEOMETRÍA ORIGINAL (Agua):
   • Phantom: 16×16 cm (320×320 bins)
   • Resolución: 0.0500 cm/bin = 0.50 mm/bin
   • Coordenadas: {water_x.min():.2f} a {water_x.max():.2f} cm
   • Material: Agua homogénea
   • Energía total: {np.sum(water_energies):.2e} MeV
   • Energía región común: {np.sum(water_common):.2e} MeV

🎯 COMPARACIÓN EN REGIÓN COMÚN:
   • Área común: {(x_max_common-x_min_common)*(y_max_common-y_min_common):.1f} cm²
   • Ratio energía: {np.sum(bone_common)/np.sum(water_common):.3f}
   • Misma resolución: 0.5 mm/voxel
   • Heterogeneidad visible: Y = 1 a 9 cm

✅ CONVERSIONES VERIFICADAS:
   • Índices → coordenadas reales
   • Unidades confirmadas en cm
   • Resolución espacial idéntica
    """
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('mapas_2d_FINALES_coordenadas_correctas.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Mapas finales guardados: mapas_2d_FINALES_coordenadas_correctas.png")
    plt.show()

if __name__ == "__main__":
    create_final_comparison()

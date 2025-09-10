#!/usr/bin/env python3
"""
MAPAS 2D CORREGIDOS: GEOMETRÍA OPTIMIZADA vs ORIGINAL
Análisis con conversión correcta de unidades

GEOMETRÍA OPTIMIZADA: 18×18 cm, 360×360 bins → 0.05 cm/bin
GEOMETRÍA ORIGINAL: 16×16 cm, 320×320 bins → 0.05 cm/bin

Los datos están en unidades de bins, necesitamos convertir a cm.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.patches as patches

def load_energy_map_corrected(filename, title, box_size_cm, n_bins):
    """Cargar datos con conversión correcta de unidades"""
    print(f"🔄 Cargando {title}...")
    try:
        data = np.loadtxt(filename, skiprows=2)
        
        # Conversión de bins a cm
        bin_size = box_size_cm / n_bins  # cm por bin
        
        # Convertir coordenadas de bins a cm
        x_bins = data[:, 0]
        y_bins = data[:, 1]
        x_cm = x_bins * bin_size
        y_cm = y_bins * bin_size
        energies = data[:, 3]
        
        # Extraer coordenadas únicas en cm
        x_coords_cm = np.unique(x_cm)
        y_coords_cm = np.unique(y_cm)
        
        print(f"   📏 Dimensiones configuradas: {box_size_cm}×{box_size_cm} cm")
        print(f"   📊 Bins: {n_bins}×{n_bins}")
        print(f"   📐 Resolución: {bin_size:.3f} cm/bin = {bin_size*10:.1f} mm/bin")
        print(f"   📊 Rango X real: {x_coords_cm.min():.1f} a {x_coords_cm.max():.1f} cm")
        print(f"   📊 Rango Y real: {y_coords_cm.min():.1f} a {y_coords_cm.max():.1f} cm")
        print(f"   ⚡ Energía total: {np.sum(energies):.2e} MeV")
        print(f"   📈 Puntos con energía >0: {np.sum(energies > 0):,} de {len(energies):,}")
        
        # Crear matriz 2D
        energy_map = np.zeros((len(y_coords_cm), len(x_coords_cm)))
        
        for i, (x_cm_val, y_cm_val, z, energy) in enumerate(zip(x_cm, y_cm, data[:, 2], energies)):
            x_idx = np.where(np.abs(x_coords_cm - x_cm_val) < 1e-6)[0][0]
            y_idx = np.where(np.abs(y_coords_cm - y_cm_val) < 1e-6)[0][0]
            energy_map[y_idx, x_idx] = energy
            
        return energy_map, x_coords_cm, y_coords_cm, energies
        
    except Exception as e:
        print(f"❌ Error cargando {filename}: {e}")
        return None, None, None, None

def create_corrected_2d_maps():
    """Crear mapas 2D con unidades corregidas"""
    print("🗺️  MAPAS 2D CON UNIDADES CORREGIDAS")
    print("=" * 50)
    
    # Cargar datos con parámetros correctos
    bone_map, bone_x, bone_y, bone_energies = load_energy_map_corrected(
        "EnergyDeposition_MEGA_Bone_Optimized.out", 
        "GEOMETRÍA OPTIMIZADA (Hueso)",
        box_size_cm=18.0, n_bins=360)
    
    water_map, water_x, water_y, water_energies = load_energy_map_corrected(
        "../output/EnergyDeposition_MEGA_Water.out", 
        "GEOMETRÍA ORIGINAL (Agua)",
        box_size_cm=32.0, n_bins=320)
    
    if bone_map is None or water_map is None:
        print("❌ No se pudieron cargar los mapas")
        return
    
    # Encontrar región común para comparación
    x_min_common = max(bone_x.min(), water_x.min())
    x_max_common = min(bone_x.max(), water_x.max())
    y_min_common = max(bone_y.min(), water_y.min())
    y_max_common = min(bone_y.max(), water_y.max())
    
    print(f"\n🎯 REGIÓN COMÚN PARA COMPARACIÓN:")
    print(f"   X: {x_min_common:.1f} a {x_max_common:.1f} cm")
    print(f"   Y: {y_min_common:.1f} a {y_max_common:.1f} cm")
    print(f"   Área común: {(x_max_common-x_min_common)*(y_max_common-y_min_common):.1f} cm²")
    
    # Crear figura con 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('COMPARACIÓN 2D CORREGIDA: GEOMETRÍA OPTIMIZADA vs ORIGINAL', 
                 fontsize=16, fontweight='bold')
    
    # 1. Mapa Optimizado (Hueso) - CORREGIDO
    ax1 = axes[0, 0]
    im1 = ax1.imshow(bone_map, extent=[bone_x.min(), bone_x.max(), bone_y.min(), bone_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=bone_map.max()))
    ax1.set_title('GEOMETRÍA OPTIMIZADA (Hueso)\n18×18 cm, 360×360 bins (0.05 cm/bin)', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    # Marcar heterogeneidad real (8×8 cm centrada en (0,5))
    het_rect = patches.Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='cyan', 
                                facecolor='none', linestyle='--', label='Heterogeneidad 8×8 cm')
    ax1.add_patch(het_rect)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    plt.colorbar(im1, ax=ax1, label='Energía Depositada (MeV)')
    
    # 2. Mapa Original (Agua) - CORREGIDO
    ax2 = axes[0, 1]
    im2 = ax2.imshow(water_map, extent=[water_x.min(), water_x.max(), water_y.min(), water_y.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=water_map.max()))
    ax2.set_title('GEOMETRÍA ORIGINAL (Agua)\n32×32 cm, 320×320 bins (0.10 cm/bin)', fontweight='bold')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(im2, ax=ax2, label='Energía Depositada (MeV)')
    
    # 3. Región común ampliada
    ax3 = axes[1, 0]
    
    # Extraer solo la región común del mapa de hueso
    bone_mask_x = (bone_x >= x_min_common) & (bone_x <= x_max_common)
    bone_mask_y = (bone_y >= y_min_common) & (bone_y <= y_max_common)
    
    bone_x_common = bone_x[bone_mask_x]
    bone_y_common = bone_y[bone_mask_y]
    bone_map_common = bone_map[np.ix_(bone_mask_y, bone_mask_x)]
    
    im3 = ax3.imshow(bone_map_common, 
                     extent=[bone_x_common.min(), bone_x_common.max(), 
                            bone_y_common.min(), bone_y_common.max()],
                     origin='lower', cmap='hot', norm=LogNorm(vmin=1e-6, vmax=bone_map_common.max()))
    ax3.set_title('REGIÓN COMÚN - HUESO\n(Para comparación directa)', fontweight='bold')
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    
    # Marcar heterogeneidad si está en la región común
    if (-4 >= x_min_common and 4 <= x_max_common and 1 >= y_min_common and 9 <= y_max_common):
        het_rect3 = patches.Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='cyan', 
                                     facecolor='none', linestyle='--', label='Heterogeneidad')
        ax3.add_patch(het_rect3)
        ax3.legend()
    
    ax3.grid(True, alpha=0.3)
    plt.colorbar(im3, ax=ax3, label='Energía Depositada (MeV)')
    
    # 4. Estadísticas detalladas
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    stats_text = f"""
ANÁLISIS CORREGIDO DE UNIDADES:

📊 GEOMETRÍA OPTIMIZADA (Hueso):
   • Configuración: 18×18 cm, 360×360 bins
   • Resolución: 0.050 cm/bin = 0.5 mm/bin
   • Rango real: {bone_x.min():.1f} a {bone_x.max():.1f} cm
   • Heterogeneidad: 8×8 cm hueso en (0,5) cm
   • Energía total: {np.sum(bone_energies):.2e} MeV
   • Voxels activos: {np.sum(bone_energies > 0):,}/{len(bone_energies):,}

📊 GEOMETRÍA ORIGINAL (Agua):
   • Configuración: 32×32 cm, 320×320 bins  
   • Resolución: 0.100 cm/bin = 1.0 mm/bin
   • Rango real: {water_x.min():.1f} a {water_x.max():.1f} cm
   • Material: Agua homogénea
   • Energía total: {np.sum(water_energies):.2e} MeV
   • Voxels activos: {np.sum(water_energies > 0):,}/{len(water_energies):,}

🎯 COMPARACIÓN VÁLIDA:
   • Resolución diferente: 0.5 mm vs 1.0 mm/bin
   • Región común: {x_min_common:.1f} a {x_max_common:.1f} cm
   • Área común: {(x_max_common-x_min_common)*(y_max_common-y_min_common):.1f} cm²
   • Ratio energía total: {np.sum(bone_energies)/np.sum(water_energies):.3f}
   
⚠️  NOTA: Resoluciones diferentes
   • Hueso: 0.5 mm/bin (mayor resolución)  
   • Agua: 1.0 mm/bin (menor resolución)
    """
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('mapas_2d_CORREGIDOS_optimizada_vs_original.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Mapas 2D corregidos guardados: mapas_2d_CORREGIDOS_optimizada_vs_original.png")
    plt.show()

if __name__ == "__main__":
    create_corrected_2d_maps()

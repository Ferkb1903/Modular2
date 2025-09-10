#!/usr/bin/env python3
"""
COMPARACIÓN DE REFERENCIA: AGUA HOMOGÉNEA vs HETEROGENEIDAD DE HUESO
Análisis cuantitativo para simulaciones de braquiterapia
Geometría optimizada: Phantom 18x18x18 cm, Heterogeneidad 8x8x8 cm
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

# =============================================================================
# CONFIGURACIÓN DE DATOS Y VISUALIZACIÓN
# =============================================================================

# Parámetros de la malla de scoring
MESH_SIZE_CM = 18.0  # 18x18 cm
BINS = 360          # 360x360 bins
BIN_SIZE_CM = MESH_SIZE_CM / BINS  # 0.05 cm/bin = 0.5 mm

# Geometría del phantom (basado en análisis del código fuente)
PHANTOM_SIZE_CM = 18.0    # Phantom de 18x18x18 cm
HETEROGENEITY_SIZE_CM = 8.0  # Heterogeneidad de 8x8x8 cm  
HETEROGENEITY_POSITION_Y_CM = 5.0  # Posición en Y: +5 cm del centro

# Archivos de datos
FILE_WATER = "EnergyDeposition_REF_Water_Homogeneous.out"
FILE_BONE = "EnergyDeposition_REF_Bone_Heterogeneous.out"

def load_geant4_data(filename):
    """Cargar datos de Geant4 con manejo robusto de headers y formato"""
    print(f"Cargando datos de: {filename}")
    
    # Leer archivo saltando headers
    try:
        data = pd.read_csv(filename, sep='\s+', comment='#', header=None)
        data.columns = ['x', 'y', 'z', 'energy']
        print(f"  ✓ Datos cargados: {len(data)} puntos")
        print(f"  ✓ Rango X: {data['x'].min():.2f} a {data['x'].max():.2f} cm")  
        print(f"  ✓ Rango Y: {data['y'].min():.2f} a {data['y'].max():.2f} cm")
        print(f"  ✓ Energía total: {data['energy'].sum():.2e} MeV")
        return data
    except Exception as e:
        print(f"  ✗ Error cargando {filename}: {e}")
        return None

def create_2d_map(data, title="Mapa 2D"):
    """Crear mapa 2D de deposición de energía con coordenadas reales"""
    print(f"Creando mapa 2D: {title}")
    
    # Crear malla 2D usando coordenadas reales
    x_coords = data['x'].values
    y_coords = data['y'].values
    energy_values = data['energy'].values
    
    # Definir límites de la malla  
    x_min, x_max = -MESH_SIZE_CM/2, MESH_SIZE_CM/2
    y_min, y_max = -MESH_SIZE_CM/2, MESH_SIZE_CM/2
    
    # Crear malla 2D
    energy_map = np.zeros((BINS, BINS))
    
    # Mapear coordenadas reales a índices de bins
    for i, (x, y, energy) in enumerate(zip(x_coords, y_coords, energy_values)):
        # Convertir coordenadas reales a índices de bins
        bin_x = int((x - x_min) / BIN_SIZE_CM)
        bin_y = int((y - y_min) / BIN_SIZE_CM)
        
        # Verificar límites
        if 0 <= bin_x < BINS and 0 <= bin_y < BINS:
            energy_map[bin_y, bin_x] = energy
    
    print(f"  ✓ Mapa creado: {np.count_nonzero(energy_map)} voxels con energía")
    print(f"  ✓ Energía máxima: {np.max(energy_map):.2e} MeV")
    print(f"  ✓ Energía promedio (no-cero): {np.mean(energy_map[energy_map > 0]):.2e} MeV")
    
    return energy_map

def plot_comparison_maps(water_map, bone_map):
    """Crear visualización comparativa con geometría anotada"""
    print("Generando mapas comparativos...")
    
    # Configurar colormap personalizado
    colors = ['#000033', '#0066CC', '#00CCFF', '#FFFF00', '#FF6600', '#FF0000', '#FFFFFF']
    cmap = LinearSegmentedColormap.from_list('energy', colors, N=256)
    
    # Coordenadas para visualización (centradas en origen)
    extent = [-MESH_SIZE_CM/2, MESH_SIZE_CM/2, -MESH_SIZE_CM/2, MESH_SIZE_CM/2]
    
    # Calcular diferencia relativa
    difference_map = np.zeros_like(water_map)
    mask = water_map > 0
    difference_map[mask] = ((bone_map[mask] - water_map[mask]) / water_map[mask]) * 100
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('COMPARACIÓN DE REFERENCIA: Agua Homogénea vs Heterogeneidad de Hueso\n' +
                 'Geometría Optimizada: Phantom 18×18×18 cm + Heterogeneidad 8×8×8 cm', 
                 fontsize=16, fontweight='bold')
    
    # Mapa 1: Agua homogénea
    im1 = axes[0,0].imshow(water_map, extent=extent, origin='lower', cmap=cmap, aspect='equal')
    axes[0,0].set_title('Agua Homogénea (Referencia)\n1M eventos, 14 threads', fontsize=12, fontweight='bold')
    axes[0,0].set_xlabel('X (cm)')
    axes[0,0].set_ylabel('Y (cm)')
    
    # Mapa 2: Heterogeneidad de hueso  
    im2 = axes[0,1].imshow(bone_map, extent=extent, origin='lower', cmap=cmap, aspect='equal')
    axes[0,1].set_title('Heterogeneidad de Hueso\nG4_BONE_CORTICAL_ICRP', fontsize=12, fontweight='bold')
    axes[0,1].set_xlabel('X (cm)')
    axes[0,1].set_ylabel('Y (cm)')
    
    # Mapa 3: Diferencia relativa
    diff_cmap = plt.cm.RdBu_r
    im3 = axes[1,0].imshow(difference_map, extent=extent, origin='lower', cmap=diff_cmap, 
                          vmin=-50, vmax=50, aspect='equal')
    axes[1,0].set_title('Diferencia Relativa: (Hueso - Agua)/Agua × 100%', fontsize=12, fontweight='bold')
    axes[1,0].set_xlabel('X (cm)')
    axes[1,0].set_ylabel('Y (cm)')
    
    # Mapa 4: Perfil comparativo en Y=5cm (centro de heterogeneidad)
    y_center_idx = int((HETEROGENEITY_POSITION_Y_CM + MESH_SIZE_CM/2) / BIN_SIZE_CM)
    x_profile = np.linspace(-MESH_SIZE_CM/2, MESH_SIZE_CM/2, BINS)
    
    water_profile = water_map[y_center_idx, :]
    bone_profile = bone_map[y_center_idx, :]
    
    axes[1,1].plot(x_profile, water_profile, 'b-', linewidth=2, label='Agua Homogénea')
    axes[1,1].plot(x_profile, bone_profile, 'r-', linewidth=2, label='Heterogeneidad Hueso')
    axes[1,1].set_title(f'Perfil en Y = {HETEROGENEITY_POSITION_Y_CM} cm\n(Centro de Heterogeneidad)', 
                       fontsize=12, fontweight='bold')
    axes[1,1].set_xlabel('X (cm)')
    axes[1,1].set_ylabel('Energía Depositada (MeV)')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    # Agregar anotaciones de geometría en todos los mapas
    for ax in axes[:2].flatten():
        # Contorno del phantom (18x18 cm)
        phantom_rect = patches.Rectangle((-PHANTOM_SIZE_CM/2, -PHANTOM_SIZE_CM/2), 
                                       PHANTOM_SIZE_CM, PHANTOM_SIZE_CM,
                                       linewidth=2, edgecolor='white', facecolor='none', 
                                       linestyle='--', alpha=0.8)
        ax.add_patch(phantom_rect)
        
        # Región de heterogeneidad (8x8 cm centrada en Y=+5cm)
        het_x = -HETEROGENEITY_SIZE_CM/2
        het_y = HETEROGENEITY_POSITION_Y_CM - HETEROGENEITY_SIZE_CM/2
        het_rect = patches.Rectangle((het_x, het_y), 
                                   HETEROGENEITY_SIZE_CM, HETEROGENEITY_SIZE_CM,
                                   linewidth=2, edgecolor='yellow', facecolor='none', 
                                   alpha=0.9)
        ax.add_patch(het_rect)
        
        # Posición de la fuente (centro: 0,0)
        ax.plot(0, 0, 'wo', markersize=8, markeredgecolor='red', markeredgewidth=2, 
               label='Fuente Ir-192')
        
        # Configurar límites y grilla
        ax.set_xlim(-MESH_SIZE_CM/2, MESH_SIZE_CM/2)
        ax.set_ylim(-MESH_SIZE_CM/2, MESH_SIZE_CM/2)
        ax.grid(True, alpha=0.3)
    
    # Colorbar para mapas de energía
    plt.colorbar(im1, ax=axes[0,0], label='Energía (MeV)', shrink=0.8)
    plt.colorbar(im2, ax=axes[0,1], label='Energía (MeV)', shrink=0.8)
    plt.colorbar(im3, ax=axes[1,0], label='Diferencia (%)', shrink=0.8)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura  
    output_file = "comparacion_referencia_agua_vs_hueso.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Comparación guardada: {output_file}")
    
    return fig

def calculate_statistics(water_map, bone_map):
    """Calcular estadísticas comparativas"""
    print("\n" + "="*60)
    print("ESTADÍSTICAS COMPARATIVAS")
    print("="*60)
    
    # Estadísticas básicas
    water_total = np.sum(water_map)
    bone_total = np.sum(bone_map)
    water_max = np.max(water_map)
    bone_max = np.max(bone_map)
    
    print(f"Energía Total:")
    print(f"  Agua homogénea:      {water_total:.2e} MeV")
    print(f"  Heterogeneidad hueso: {bone_total:.2e} MeV")
    print(f"  Diferencia relativa:  {((bone_total - water_total)/water_total)*100:.2f}%")
    
    print(f"\nEnergía Máxima:")
    print(f"  Agua homogénea:      {water_max:.2e} MeV")
    print(f"  Heterogeneidad hueso: {bone_max:.2e} MeV")
    print(f"  Diferencia relativa:  {((bone_max - water_max)/water_max)*100:.2f}%")
    
    # Análisis en región de heterogeneidad
    het_x_start = int((BINS/2) - (HETEROGENEITY_SIZE_CM/2) / BIN_SIZE_CM)
    het_x_end = int((BINS/2) + (HETEROGENEITY_SIZE_CM/2) / BIN_SIZE_CM)
    het_y_start = int((BINS/2) + (HETEROGENEITY_POSITION_Y_CM - HETEROGENEITY_SIZE_CM/2) / BIN_SIZE_CM)
    het_y_end = int((BINS/2) + (HETEROGENEITY_POSITION_Y_CM + HETEROGENEITY_SIZE_CM/2) / BIN_SIZE_CM)
    
    water_het_region = water_map[het_y_start:het_y_end, het_x_start:het_x_end]
    bone_het_region = bone_map[het_y_start:het_y_end, het_x_start:het_x_end]
    
    water_het_mean = np.mean(water_het_region[water_het_region > 0])
    bone_het_mean = np.mean(bone_het_region[bone_het_region > 0])
    
    print(f"\nAnálisis en Región de Heterogeneidad (8×8 cm):")
    print(f"  Energía promedio (agua):  {water_het_mean:.2e} MeV")
    print(f"  Energía promedio (hueso): {bone_het_mean:.2e} MeV")
    print(f"  Diferencia relativa:      {((bone_het_mean - water_het_mean)/water_het_mean)*100:.2f}%")
    
    print(f"\nConfiguración de Simulación:")
    print(f"  Phantom:               {PHANTOM_SIZE_CM}×{PHANTOM_SIZE_CM}×{PHANTOM_SIZE_CM} cm")
    print(f"  Heterogeneidad:        {HETEROGENEITY_SIZE_CM}×{HETEROGENEITY_SIZE_CM}×{HETEROGENEITY_SIZE_CM} cm")
    print(f"  Posición heterogeneidad: (0, {HETEROGENEITY_POSITION_Y_CM}, 0) cm")
    print(f"  Resolución malla:      {BIN_SIZE_CM*10:.1f} mm/voxel")
    print(f"  Eventos simulados:     1,000,000")
    print(f"  Threads utilizados:    14")

def main():
    """Función principal de análisis"""
    print("COMPARACIÓN DE REFERENCIA: AGUA vs HUESO")
    print("Geometría Optimizada - Análisis Cuantitativo")
    print("="*60)
    
    # Cargar datos
    water_data = load_geant4_data(FILE_WATER)
    bone_data = load_geant4_data(FILE_BONE)
    
    if water_data is None or bone_data is None:
        print("❌ Error: No se pudieron cargar los archivos de datos")
        return
    
    # Crear mapas 2D
    water_map = create_2d_map(water_data, "Agua Homogénea")
    bone_map = create_2d_map(bone_data, "Heterogeneidad Hueso")
    
    # Generar visualizaciones comparativas
    plot_comparison_maps(water_map, bone_map)
    
    # Calcular estadísticas
    calculate_statistics(water_map, bone_map)
    
    print("\n✅ Análisis completado exitosamente")
    print("📊 Visualización guardada: comparacion_referencia_agua_vs_hueso.png")

if __name__ == "__main__":
    main()

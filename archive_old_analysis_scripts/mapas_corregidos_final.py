#!/usr/bin/env python3
"""
MAPAS CORREGIDOS DE DEPOSICIÓN DE ENERGÍA 2D
============================================
Script para crear mapas 2D con coordenadas corregidas y análisis de diferencias.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec

# Configuración de alta calidad
plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

def cargar_datos_corregidos(filename):
    """Cargar datos con coordenadas corregidas"""
    print(f"📂 Cargando: {filename}")
    
    # Leer datos corregidos
    data = pd.read_csv(filename, sep=r'\s+', comment='#', header=None)
    data.columns = ['x', 'y', 'z', 'edep']
    
    print(f"  ✓ {len(data)} puntos cargados")
    print(f"  ✓ Energía total: {data['edep'].sum():.2e} MeV")
    print(f"  ✓ Rango X: {data['x'].min():.2f} a {data['x'].max():.2f} cm")
    print(f"  ✓ Rango Y: {data['y'].min():.2f} a {data['y'].max():.2f} cm")
    
    return data

def crear_mapa_2d_corregido(data, titulo, limite_cm=9.0, bins=180):
    """Crear mapa 2D con resolución apropiada para los datos corregidos"""
    print(f"🗺️  Creando mapa: {titulo}")
    
    # Crear grid para el mapa (usar 180 bins para 0.1 cm de resolución)
    x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    
    # Crear mapa 2D usando histograma ponderado
    mapa, _, _ = np.histogram2d(data['x'], data['y'], 
                               bins=[x_edges, y_edges], 
                               weights=data['edep'])
    
    # Centros de bins para plotting
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    print(f"  ✓ Mapa creado: {np.sum(mapa > 0)} voxels con energía")
    print(f"  ✓ Energía máxima: {mapa.max():.2e} MeV")
    print(f"  ✓ Energía total en mapa: {mapa.sum():.2e} MeV")
    print(f"  ✓ Resolución: {18.0/bins:.3f} cm/bin")
    
    return mapa, x_centers, y_centers

def crear_comparacion_corregida():
    """Crear comparación con datos corregidos"""
    print("🎨 Creando comparación con resolución 1mm optimizada...")
    
    # Cargar datos con resolución 1mm y coordenadas corregidas
    datos_agua = cargar_datos_corregidos('EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.out')
    datos_hueso = cargar_datos_corregidos('EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.out')
    
    # Crear mapas 2D con resolución apropiada
    mapa_agua, x_centers, y_centers = crear_mapa_2d_corregido(datos_agua, "Agua Homogénea", bins=180)
    mapa_hueso, _, _ = crear_mapa_2d_corregido(datos_hueso, "Heterogeneidad Hueso", bins=180)
    
    # Calcular diferencias
    diferencia_abs = mapa_hueso - mapa_agua
    diferencia_rel = np.zeros_like(mapa_agua)
    mask = mapa_agua > 0
    diferencia_rel[mask] = (diferencia_abs[mask] / mapa_agua[mask]) * 100
    diferencia_rel[~mask] = np.nan
    
    # Crear figura con 6 subplots
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 1])
    
    # === FILA 1: MAPAS ORIGINALES ===
    
    # Mapa de agua
    ax1 = fig.add_subplot(gs[0, 0])
    mapa_agua_log = np.log10(mapa_agua + 1e-10)
    mapa_agua_log[mapa_agua == 0] = np.nan
    
    im1 = ax1.imshow(mapa_agua_log.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='hot', aspect='equal')
    ax1.plot(0, 0, 'w*', markersize=15, markeredgecolor='black', markeredgewidth=1,
            label='Fuente Ir-192')
    ax1.set_title('AGUA HOMOGÉNEA\n(Referencia)', fontweight='bold', fontsize=14)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Estadísticas agua
    stats_agua = f'Total: {mapa_agua.sum():.2e} MeV\nMáx: {mapa_agua.max():.2e} MeV'
    ax1.text(0.02, 0.98, stats_agua, transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=9)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('log₁₀(Energía) [MeV]', rotation=270, labelpad=15)
    
    # Mapa de hueso
    ax2 = fig.add_subplot(gs[0, 1])
    mapa_hueso_log = np.log10(mapa_hueso + 1e-10)
    mapa_hueso_log[mapa_hueso == 0] = np.nan
    
    im2 = ax2.imshow(mapa_hueso_log.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='hot', aspect='equal')
    ax2.plot(0, 0, 'w*', markersize=15, markeredgecolor='black', markeredgewidth=1,
            label='Fuente Ir-192')
    
    # Marcar región de heterogeneidad (8×8 cm centrada en (0, 5))
    rect = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='cyan', 
                    facecolor='none', linestyle='--', label='Región hueso')
    ax2.add_patch(rect)
    
    ax2.set_title('HETEROGENEIDAD HUESO\n(G4_BONE_CORTICAL_ICRP)', fontweight='bold', fontsize=14)
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Estadísticas hueso
    stats_hueso = f'Total: {mapa_hueso.sum():.2e} MeV\nMáx: {mapa_hueso.max():.2e} MeV'
    ax2.text(0.02, 0.98, stats_hueso, transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=9)
    
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('log₁₀(Energía) [MeV]', rotation=270, labelpad=15)
    
    # Diferencia absoluta
    ax3 = fig.add_subplot(gs[0, 2])
    im3 = ax3.imshow(diferencia_abs.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal')
    ax3.plot(0, 0, 'k*', markersize=15, label='Fuente')
    rect3 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--', label='Región hueso')
    ax3.add_patch(rect3)
    ax3.set_title('DIFERENCIA ABSOLUTA\n(Hueso - Agua)', fontweight='bold', fontsize=14)
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
    cbar3.set_label('ΔE [MeV]', rotation=270, labelpad=15)
    
    # === FILA 2: ANÁLISIS DE DIFERENCIAS ===
    
    # Diferencia relativa
    ax4 = fig.add_subplot(gs[1, 0])
    diff_plot = np.copy(diferencia_rel)
    im4 = ax4.imshow(diff_plot.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-5, vmax=5)
    ax4.plot(0, 0, 'k*', markersize=15, label='Fuente')
    rect4 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--', label='Región hueso')
    ax4.add_patch(rect4)
    ax4.set_title('DIFERENCIA RELATIVA\n[(Hueso-Agua)/Agua × 100%]', fontweight='bold', fontsize=14)
    ax4.set_xlabel('X (cm)')
    ax4.set_ylabel('Y (cm)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    cbar4 = plt.colorbar(im4, ax=ax4, shrink=0.8)
    cbar4.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Perfil vertical (atraviesa heterogeneidad)
    ax5 = fig.add_subplot(gs[1, 1])
    
    idx_centro_x = len(x_centers) // 2
    perfil_agua_y = mapa_agua[idx_centro_x, :]
    perfil_hueso_y = mapa_hueso[idx_centro_x, :]
    
    ax5.plot(y_centers, perfil_agua_y, 'b-', linewidth=3, label='Agua homogénea', alpha=0.8)
    ax5.plot(y_centers, perfil_hueso_y, 'r-', linewidth=3, label='Heterogeneidad hueso', alpha=0.8)
    ax5.axvline(0, color='black', linestyle='--', alpha=0.5, label='Fuente')
    ax5.axvspan(1, 9, alpha=0.2, color='orange', label='Región hueso')
    ax5.set_xlabel('Y (cm)')
    ax5.set_ylabel('Energía Depositada (MeV)')
    ax5.set_title('PERFIL VERTICAL (X = 0 cm)\nAtravesando Heterogeneidad', fontweight='bold', fontsize=14)
    ax5.set_yscale('log')  # Escala logarítmica para mejor visualización
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(-9, 9)
    
    # Histograma de diferencias
    ax6 = fig.add_subplot(gs[1, 2])
    
    mask_valido = (mapa_agua > 0) & (mapa_hueso > 0)
    diff_validas = diferencia_rel[mask_valido]
    
    # Filtrar outliers para mejor visualización
    q1, q99 = np.percentile(diff_validas, [5, 95])
    diff_filtradas = diff_validas[(diff_validas >= q1) & (diff_validas <= q99)]
    
    ax6.hist(diff_filtradas, bins=30, alpha=0.7, edgecolor='black', density=True, 
            color='skyblue', label=f'n = {len(diff_filtradas)}')
    ax6.axvline(0, color='red', linestyle='--', linewidth=2, label='Sin diferencia')
    ax6.axvline(np.mean(diff_filtradas), color='blue', linestyle='-', linewidth=2,
                label=f'Media: {np.mean(diff_filtradas):.2f}%')
    ax6.set_xlabel('Diferencia Relativa [%]')
    ax6.set_ylabel('Densidad')
    ax6.set_title('DISTRIBUCIÓN DE DIFERENCIAS\n(5%-95% percentil)', fontweight='bold', fontsize=14)
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # Título general
    fig.suptitle('ANÁLISIS OPTIMIZADO: DEPOSICIÓN DE ENERGÍA EN BRAQUITERAPIA\n' + 
                 'Monte Carlo - Agua Homogénea vs Heterogeneidad Hueso Cortical (Resolución 1mm)',
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig('MAPAS_1mm_Agua_vs_Hueso_OPTIMIZADO.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: MAPAS_1mm_Agua_vs_Hueso_OPTIMIZADO.png")
    plt.close()
    
    # Imprimir estadísticas
    print("\n📊 ESTADÍSTICAS FINALES (RESOLUCIÓN 1MM OPTIMIZADA):")
    print(f"  Energía Total Agua:      {mapa_agua.sum():.2e} MeV")
    print(f"  Energía Total Hueso:     {mapa_hueso.sum():.2e} MeV")
    print(f"  Diferencia Total:        {((mapa_hueso.sum() - mapa_agua.sum()) / mapa_agua.sum()) * 100:+.2f}%")
    print(f"  Diferencia Promedio:     {np.mean(diff_filtradas):.2f}%")
    print(f"  Desviación Estándar:     {np.std(diff_filtradas):.2f}%")
    print(f"  Rango de diferencias:    {np.min(diff_filtradas):.2f}% a {np.max(diff_filtradas):.2f}%")

def main():
    """Función principal"""
    print("=" * 70)
    print("MAPAS OPTIMIZADOS DE DEPOSICIÓN DE ENERGÍA")
    print("Análisis con resolución 1mm mejorada (1M eventos)")
    print("=" * 70)
    
    crear_comparacion_corregida()
    
    print("\n✅ ANÁLISIS COMPLETADO CON RESOLUCIÓN 1MM OPTIMIZADA")
    print("📁 Archivo generado: MAPAS_1mm_Agua_vs_Hueso_OPTIMIZADO.png")
    print("=" * 70)

if __name__ == "__main__":
    main()

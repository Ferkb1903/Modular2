#!/usr/bin/env python3
"""
RESUMEN VISUAL FINAL - COMPARACIÓN AGUA vs HUESO
================================================
Script para crear un resumen visual completo con los mapas principales
y análisis de diferencias en una sola imagen.
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
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['legend.fontsize'] = 8

def cargar_y_procesar_datos():
    """Cargar y procesar ambos conjuntos de datos"""
    print("📂 Cargando datos para resumen final...")
    
    # Cargar datos de agua
    data_agua = pd.read_csv('EnergyDeposition_REF_Water_Homogeneous.out', 
                           sep=r'\s+', comment='#', header=None)
    data_agua.columns = ['i', 'j', 'k', 'edep']
    
    # Cargar datos de hueso
    data_hueso = pd.read_csv('EnergyDeposition_REF_Bone_Heterogeneous.out', 
                            sep=r'\s+', comment='#', header=None)
    data_hueso.columns = ['i', 'j', 'k', 'edep']
    
    # Convertir a coordenadas físicas
    bin_size = 18.0 / 360  # 0.05 cm por bin
    
    for data in [data_agua, data_hueso]:
        data['x'] = (data['i'] - 180) * bin_size
        data['y'] = (data['j'] - 180) * bin_size
    
    # Crear mapas 2D
    limite_cm = 9.0
    bins = 360
    x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    
    mapa_agua, _, _ = np.histogram2d(data_agua['x'], data_agua['y'], 
                                    bins=[x_edges, y_edges], 
                                    weights=data_agua['edep'])
    
    mapa_hueso, _, _ = np.histogram2d(data_hueso['x'], data_hueso['y'], 
                                     bins=[x_edges, y_edges], 
                                     weights=data_hueso['edep'])
    
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    print(f"  ✓ Agua: {np.sum(mapa_agua > 0)} voxels, energía total: {mapa_agua.sum():.2e} MeV")
    print(f"  ✓ Hueso: {np.sum(mapa_hueso > 0)} voxels, energía total: {mapa_hueso.sum():.2e} MeV")
    
    return mapa_agua, mapa_hueso, x_centers, y_centers

def crear_resumen_final():
    """Crear figura de resumen final"""
    print("🎨 Creando resumen visual final...")
    
    # Cargar datos
    mapa_agua, mapa_hueso, x_centers, y_centers = cargar_y_procesar_datos()
    
    # Calcular diferencias
    diferencia_abs = mapa_hueso - mapa_agua
    diferencia_rel = np.zeros_like(mapa_agua)
    mask = mapa_agua > 0
    diferencia_rel[mask] = (diferencia_abs[mask] / mapa_agua[mask]) * 100
    diferencia_rel[~mask] = np.nan
    
    # Crear figura con grid complejo
    fig = plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1, 1, 0.8], width_ratios=[1, 1, 1, 0.3])
    
    # === FILA 1: MAPAS ORIGINALES ===
    
    # Mapa de agua
    ax1 = fig.add_subplot(gs[0, 0])
    mapa_agua_log = np.log10(mapa_agua + 1e-10)
    mapa_agua_log[mapa_agua == 0] = np.nan
    
    im1 = ax1.imshow(mapa_agua_log.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='hot', aspect='equal')
    ax1.plot(0, 0, 'w*', markersize=12, markeredgecolor='black', markeredgewidth=1)
    ax1.set_title('AGUA HOMOGÉNEA\n(Referencia)', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.grid(True, alpha=0.3)
    
    # Estadísticas agua
    stats_agua = f'Total: {mapa_agua.sum():.2e} MeV\nMáx: {mapa_agua.max():.2e} MeV\nVoxels: {np.sum(mapa_agua > 0)}'
    ax1.text(0.02, 0.98, stats_agua, transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=8)
    
    # Mapa de hueso
    ax2 = fig.add_subplot(gs[0, 1])
    mapa_hueso_log = np.log10(mapa_hueso + 1e-10)
    mapa_hueso_log[mapa_hueso == 0] = np.nan
    
    im2 = ax2.imshow(mapa_hueso_log.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='hot', aspect='equal')
    ax2.plot(0, 0, 'w*', markersize=12, markeredgecolor='black', markeredgewidth=1)
    
    # Marcar región de heterogeneidad
    rect = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='cyan', 
                    facecolor='none', linestyle='--')
    ax2.add_patch(rect)
    
    ax2.set_title('HETEROGENEIDAD HUESO\n(G4_BONE_CORTICAL_ICRP)', fontweight='bold')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.grid(True, alpha=0.3)
    
    # Estadísticas hueso
    stats_hueso = f'Total: {mapa_hueso.sum():.2e} MeV\nMáx: {mapa_hueso.max():.2e} MeV\nVoxels: {np.sum(mapa_hueso > 0)}'
    ax2.text(0.02, 0.98, stats_hueso, transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=8)
    
    # Diferencia absoluta
    ax3 = fig.add_subplot(gs[0, 2])
    im3 = ax3.imshow(diferencia_abs.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal')
    ax3.plot(0, 0, 'k*', markersize=12)
    rect3 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--')
    ax3.add_patch(rect3)
    ax3.set_title('DIFERENCIA ABSOLUTA\n(Hueso - Agua)', fontweight='bold')
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    ax3.grid(True, alpha=0.3)
    
    # === FILA 2: ANÁLISIS DE DIFERENCIAS ===
    
    # Diferencia relativa
    ax4 = fig.add_subplot(gs[1, 0])
    diff_plot = np.copy(diferencia_rel)
    im4 = ax4.imshow(diff_plot.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-10, vmax=10)
    ax4.plot(0, 0, 'k*', markersize=12)
    rect4 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--')
    ax4.add_patch(rect4)
    ax4.set_title('DIFERENCIA RELATIVA\n[(Hueso-Agua)/Agua × 100%]', fontweight='bold')
    ax4.set_xlabel('X (cm)')
    ax4.set_ylabel('Y (cm)')
    ax4.grid(True, alpha=0.3)
    
    # Histograma de diferencias
    ax5 = fig.add_subplot(gs[1, 1])
    mask_valido = (mapa_agua > 0) & (mapa_hueso > 0)
    diff_validas = diferencia_rel[mask_valido]
    
    # Filtrar outliers para mejor visualización
    q1, q99 = np.percentile(diff_validas, [1, 99])
    diff_filtradas = diff_validas[(diff_validas >= q1) & (diff_validas <= q99)]
    
    ax5.hist(diff_filtradas, bins=50, alpha=0.7, edgecolor='black', density=True, color='skyblue')
    ax5.axvline(0, color='red', linestyle='--', linewidth=2, label='Sin diferencia')
    ax5.axvline(np.mean(diff_filtradas), color='blue', linestyle='-', linewidth=2,
                label=f'Media: {np.mean(diff_filtradas):.2f}%')
    ax5.set_xlabel('Diferencia Relativa [%]')
    ax5.set_ylabel('Densidad')
    ax5.set_title('DISTRIBUCIÓN DE DIFERENCIAS\n(Filtrada 1%-99%)', fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Perfiles lineales
    ax6 = fig.add_subplot(gs[1, 2])
    
    # Perfil vertical (X=0, atraviesa la heterogeneidad)
    idx_centro_x = len(x_centers) // 2
    perfil_agua_y = mapa_agua[idx_centro_x, :]
    perfil_hueso_y = mapa_hueso[idx_centro_x, :]
    
    ax6.plot(y_centers, perfil_agua_y, 'b-', linewidth=2, label='Agua', alpha=0.8)
    ax6.plot(y_centers, perfil_hueso_y, 'r-', linewidth=2, label='Hueso', alpha=0.8)
    ax6.axvline(0, color='black', linestyle='--', alpha=0.5)
    ax6.axvspan(1, 9, alpha=0.2, color='orange', label='Región hueso')
    ax6.set_xlabel('Y (cm)')
    ax6.set_ylabel('Energía (MeV)')
    ax6.set_title('PERFIL VERTICAL\n(X = 0 cm)', fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim(-9, 9)
    
    # === FILA 3: ESTADÍSTICAS Y RESUMEN ===
    
    # Tabla de estadísticas
    ax7 = fig.add_subplot(gs[2, :3])
    ax7.axis('off')
    
    # Calcular estadísticas detalladas
    energia_total_agua = mapa_agua.sum()
    energia_total_hueso = mapa_hueso.sum()
    diff_total = ((energia_total_hueso - energia_total_agua) / energia_total_agua) * 100
    
    energia_max_agua = mapa_agua.max()
    energia_max_hueso = mapa_hueso.max()
    diff_max = ((energia_max_hueso - energia_max_agua) / energia_max_agua) * 100
    
    # Análisis en región de heterogeneidad
    mask_hetero = ((x_centers[:, None] >= -4) & (x_centers[:, None] <= 4) & 
                   (y_centers[None, :] >= 1) & (y_centers[None, :] <= 9))
    energia_hetero_agua = mapa_agua[mask_hetero].sum()
    energia_hetero_hueso = mapa_hueso[mask_hetero].sum()
    diff_hetero = ((energia_hetero_hueso - energia_hetero_agua) / energia_hetero_agua) * 100
    
    # Crear tabla
    estadisticas = f"""
    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                           RESUMEN ESTADÍSTICO FINAL                                             ║
    ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
    ║                                                                                                                  ║
    ║   CONFIGURACIÓN DE SIMULACIÓN:                          RESULTADOS PRINCIPALES:                                ║
    ║   • Phantom: 18×18×18 cm (optimizado)                   • Energía Total Agua:    {energia_total_agua:.2e} MeV      ║
    ║   • Heterogeneidad: 8×8×8 cm hueso cortical             • Energía Total Hueso:   {energia_total_hueso:.2e} MeV      ║
    ║   • Posición: (0, 5, 0) cm                              • Diferencia Total:      {diff_total:+.2f}%                 ║
    ║   • Resolución: 0.5 mm/voxel                            • Energía Máx Agua:      {energia_max_agua:.2e} MeV        ║
    ║   • Eventos: 1,000,000                                  • Energía Máx Hueso:     {energia_max_hueso:.2e} MeV        ║
    ║   • Threads: 14                                         • Diferencia Máxima:     {diff_max:+.2f}%                  ║
    ║                                                         • Región Heterogeneidad: {diff_hetero:+.2f}%               ║
    ║                                                                                                                  ║
    ║   INTERPRETACIÓN FÍSICA:                                                                                         ║
    ║   • El hueso cortical (ρ≈1.92 g/cm³) absorbe más energía que el agua (ρ=1.00 g/cm³)                          ║
    ║   • Las diferencias son pequeñas debido a la geometría optimizada                                               ║
    ║   • Los resultados son consistentes con la física de interacción de fotones                                     ║
    ║                                                                                                                  ║
    ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    """
    
    ax7.text(0.5, 0.5, estadisticas, transform=ax7.transAxes, fontsize=9,
             verticalalignment='center', horizontalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.8))
    
    # === COLORBARS ===
    
    # Colorbar para mapas de energía
    cax1 = fig.add_subplot(gs[0, 3])
    cbar1 = plt.colorbar(im1, cax=cax1)
    cbar1.set_label('log₁₀(Energía) [MeV]', rotation=270, labelpad=15)
    
    # Colorbar para diferencias
    cax2 = fig.add_subplot(gs[1, 3])
    cbar2 = plt.colorbar(im4, cax=cax2)
    cbar2.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Título general
    fig.suptitle('ANÁLISIS COMPLETO: DEPOSICIÓN DE ENERGÍA EN BRAQUITERAPIA\n' + 
                 'Comparación Monte Carlo Agua Homogénea vs Heterogeneidad Hueso Cortical',
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig('RESUMEN_FINAL_Agua_vs_Hueso_Completo.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: RESUMEN_FINAL_Agua_vs_Hueso_Completo.png")
    plt.close()

def main():
    """Función principal"""
    print("🎨 CREANDO RESUMEN VISUAL FINAL")
    print("=" * 60)
    
    crear_resumen_final()
    
    print("\n✅ RESUMEN FINAL COMPLETADO")
    print("📁 Archivo generado: RESUMEN_FINAL_Agua_vs_Hueso_Completo.png")
    print("=" * 60)

if __name__ == "__main__":
    main()

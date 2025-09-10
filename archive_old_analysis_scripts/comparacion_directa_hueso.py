#!/usr/bin/env python3
"""
COMPARACIÓN DIRECTA: REGIÓN DE HUESO vs AGUA
===========================================
Análisis específico de la diferencia dosimétrica en la misma región anatómica
entre la simulación con hueso cortical y la simulación de agua homogénea.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle, Circle
import matplotlib.gridspec as gridspec
from scipy import stats as scipy_stats

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
    
    data = pd.read_csv(filename, sep=r'\s+', comment='#', header=None)
    data.columns = ['x', 'y', 'z', 'edep']
    
    print(f"  ✓ {len(data)} puntos cargados")
    print(f"  ✓ Energía total: {data['edep'].sum():.2e} MeV")
    
    return data

def crear_mapas_2d(data, limite_cm=9.0, bins=180):
    """Crear mapa 2D de una simulación"""
    x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    
    mapa, _, _ = np.histogram2d(data['x'], data['y'], 
                              bins=[x_edges, y_edges], 
                              weights=data['edep'])
    
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    return mapa, x_centers, y_centers

def definir_region_hueso(x_centers, y_centers):
    """Definir exactamente la región donde está ubicado el hueso"""
    X, Y = np.meshgrid(x_centers, y_centers, indexing='ij')
    
    # Región de hueso: rectángulo 8×8 cm centrado en (0, 5)
    # Límites: X ∈ [-4, +4] cm, Y ∈ [+1, +9] cm
    mask_hueso = ((X >= -4.0) & (X <= 4.0) & (Y >= 1.0) & (Y <= 9.0))
    
    return mask_hueso, X, Y

def analizar_region_hueso():
    """Análisis específico de la región del hueso"""
    print("=" * 80)
    print("COMPARACIÓN DIRECTA: REGIÓN DE HUESO vs AGUA HOMOGÉNEA")
    print("Análisis de la misma ubicación anatómica en ambas simulaciones")
    print("=" * 80)
    
    # Cargar datos
    datos_agua = cargar_datos_corregidos('EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.out')
    datos_hueso = cargar_datos_corregidos('EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.out')
    
    # Crear mapas
    print("\n🗺️  Creando mapas 2D...")
    mapa_agua, x_centers, y_centers = crear_mapas_2d(datos_agua, bins=180)
    mapa_hueso, _, _ = crear_mapas_2d(datos_hueso, bins=180)
    
    # Definir región del hueso
    mask_hueso, X, Y = definir_region_hueso(x_centers, y_centers)
    
    print(f"  ✓ Mapas creados con resolución {18.0/180:.3f} cm/bin")
    print(f"  ✓ Región de hueso definida: {np.sum(mask_hueso)} voxels")
    
    # Extraer valores en la región del hueso
    dosis_agua_en_region_hueso = mapa_agua[mask_hueso]
    dosis_hueso_en_region_hueso = mapa_hueso[mask_hueso]
    
    # Filtrar voxels con dosis válida (>0 en ambas simulaciones)
    mask_valido = (dosis_agua_en_region_hueso > 0) & (dosis_hueso_en_region_hueso > 0)
    
    dosis_agua_valida = dosis_agua_en_region_hueso[mask_valido]
    dosis_hueso_valida = dosis_hueso_en_region_hueso[mask_valido]
    
    print(f"  ✓ Voxels válidos para comparación: {len(dosis_agua_valida)}")
    
    # Calcular diferencias
    diferencia_absoluta = dosis_hueso_valida - dosis_agua_valida
    diferencia_relativa = (diferencia_absoluta / dosis_agua_valida) * 100
    
    # Estadísticas detalladas
    estadisticas = {
        'n_voxels': len(dosis_agua_valida),
        'dosis_agua_media': np.mean(dosis_agua_valida),
        'dosis_agua_std': np.std(dosis_agua_valida),
        'dosis_hueso_media': np.mean(dosis_hueso_valida),
        'dosis_hueso_std': np.std(dosis_hueso_valida),
        'diferencia_abs_media': np.mean(diferencia_absoluta),
        'diferencia_abs_std': np.std(diferencia_absoluta),
        'diferencia_rel_media': np.mean(diferencia_relativa),
        'diferencia_rel_std': np.std(diferencia_relativa),
        'diferencia_rel_mediana': np.median(diferencia_relativa),
        'diferencia_rel_p25': np.percentile(diferencia_relativa, 25),
        'diferencia_rel_p75': np.percentile(diferencia_relativa, 75),
        'diferencia_rel_min': np.min(diferencia_relativa),
        'diferencia_rel_max': np.max(diferencia_relativa)
    }
    
    # Test estadístico
    t_stat, p_value = scipy_stats.ttest_rel(dosis_hueso_valida, dosis_agua_valida)
    estadisticas['t_statistic'] = t_stat
    estadisticas['p_value'] = p_value
    
    # Crear visualización
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 1])
    
    # === FILA 1: MAPAS COMPARATIVOS ===
    
    # Mapa de agua en región de hueso
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Crear mapa destacando la región de hueso
    mapa_agua_display = np.copy(mapa_agua)
    mapa_agua_display[~mask_hueso] = np.nan  # Solo mostrar región de hueso
    
    im1 = ax1.imshow(mapa_agua_display.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='Blues', aspect='equal', vmin=0)
    
    ax1.plot(0, 0, 'r*', markersize=15, label='Fuente Ir-192')
    rect1 = Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='red', 
                     facecolor='none', linestyle='-', label='Región analizada')
    ax1.add_patch(rect1)
    
    ax1.set_title('SIMULACIÓN AGUA HOMOGÉNEA\nRegión donde está el hueso', 
                  fontweight='bold', fontsize=14)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Dosis [MeV]', rotation=270, labelpad=15)
    
    # Mapa de hueso en región de hueso
    ax2 = fig.add_subplot(gs[0, 1])
    
    mapa_hueso_display = np.copy(mapa_hueso)
    mapa_hueso_display[~mask_hueso] = np.nan  # Solo mostrar región de hueso
    
    im2 = ax2.imshow(mapa_hueso_display.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='Reds', aspect='equal', vmin=0)
    
    ax2.plot(0, 0, 'k*', markersize=15, label='Fuente Ir-192')
    rect2 = Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='blue', 
                     facecolor='none', linestyle='-', label='Región con hueso')
    ax2.add_patch(rect2)
    
    ax2.set_title('SIMULACIÓN HUESO CORTICAL\nMisma región con heterogeneidad', 
                  fontweight='bold', fontsize=14)
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Dosis [MeV]', rotation=270, labelpad=15)
    
    # Mapa de diferencias relativas en la región
    ax3 = fig.add_subplot(gs[0, 2])
    
    diferencia_mapa = np.full_like(mapa_agua, np.nan)
    mask_valido_mapa = (mapa_agua > 0) & (mapa_hueso > 0) & mask_hueso
    diferencia_mapa[mask_valido_mapa] = ((mapa_hueso[mask_valido_mapa] - mapa_agua[mask_valido_mapa]) / 
                                        mapa_agua[mask_valido_mapa]) * 100
    
    im3 = ax3.imshow(diferencia_mapa.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-50, vmax=100)
    
    ax3.plot(0, 0, 'k*', markersize=15, label='Fuente Ir-192')
    rect3 = Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='white', 
                     facecolor='none', linestyle='-', label='Región comparada')
    ax3.add_patch(rect3)
    
    ax3.set_title('DIFERENCIA RELATIVA\n[(Hueso-Agua)/Agua × 100%]', 
                  fontweight='bold', fontsize=14)
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
    cbar3.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # === FILA 2: ANÁLISIS ESTADÍSTICO ===
    
    # Histograma comparativo
    ax4 = fig.add_subplot(gs[1, 0])
    
    bins_hist = np.linspace(0, max(np.max(dosis_agua_valida), np.max(dosis_hueso_valida)), 50)
    
    ax4.hist(dosis_agua_valida, bins=bins_hist, alpha=0.6, color='blue', 
            label=f'Agua (μ={np.mean(dosis_agua_valida):.0f})', density=True)
    ax4.hist(dosis_hueso_valida, bins=bins_hist, alpha=0.6, color='red', 
            label=f'Hueso (μ={np.mean(dosis_hueso_valida):.0f})', density=True)
    
    ax4.axvline(np.mean(dosis_agua_valida), color='blue', linestyle='--', linewidth=2)
    ax4.axvline(np.mean(dosis_hueso_valida), color='red', linestyle='--', linewidth=2)
    
    ax4.set_xlabel('Dosis [MeV]')
    ax4.set_ylabel('Densidad de probabilidad')
    ax4.set_title('DISTRIBUCIÓN DE DOSIS\nComparación en región de hueso', 
                  fontweight='bold', fontsize=14)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Análisis de diferencias relativas
    ax5 = fig.add_subplot(gs[1, 1])
    
    ax5.hist(diferencia_relativa, bins=50, alpha=0.7, color='orange', edgecolor='black')
    ax5.axvline(estadisticas['diferencia_rel_media'], color='red', linestyle='-', linewidth=3,
                label=f"Media: {estadisticas['diferencia_rel_media']:.1f}%")
    ax5.axvline(estadisticas['diferencia_rel_mediana'], color='blue', linestyle='--', linewidth=2,
                label=f"Mediana: {estadisticas['diferencia_rel_mediana']:.1f}%")
    ax5.axvline(0, color='black', linestyle=':', linewidth=2, label='Sin diferencia')
    
    ax5.set_xlabel('Diferencia relativa [%]')
    ax5.set_ylabel('Frecuencia')
    ax5.set_title('DISTRIBUCIÓN DE DIFERENCIAS\nImpacto del hueso vs agua', 
                  fontweight='bold', fontsize=14)
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Tabla de resultados
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    # Crear tabla de resultados
    tabla_datos = [
        ['Métrica', 'Valor'],
        ['─────────────────────', '──────────────'],
        ['Voxels analizados', f"{estadisticas['n_voxels']:,}"],
        ['', ''],
        ['DOSIS PROMEDIO:', ''],
        ['  • Agua homogénea', f"{estadisticas['dosis_agua_media']:.0f} ± {estadisticas['dosis_agua_std']:.0f} MeV"],
        ['  • Con hueso cortical', f"{estadisticas['dosis_hueso_media']:.0f} ± {estadisticas['dosis_hueso_std']:.0f} MeV"],
        ['', ''],
        ['DIFERENCIA ABSOLUTA:', ''],
        ['  • Media', f"{estadisticas['diferencia_abs_media']:+.0f} ± {estadisticas['diferencia_abs_std']:.0f} MeV"],
        ['', ''],
        ['DIFERENCIA RELATIVA:', ''],
        ['  • Media', f"{estadisticas['diferencia_rel_media']:+.1f} ± {estadisticas['diferencia_rel_std']:.1f}%"],
        ['  • Mediana', f"{estadisticas['diferencia_rel_mediana']:+.1f}%"],
        ['  • Rango', f"{estadisticas['diferencia_rel_min']:.1f}% a {estadisticas['diferencia_rel_max']:.1f}%"],
        ['  • Q1 - Q3', f"{estadisticas['diferencia_rel_p25']:.1f}% - {estadisticas['diferencia_rel_p75']:.1f}%"],
        ['', ''],
        ['TEST ESTADÍSTICO:', ''],
        ['  • t-estadístico', f"{estadisticas['t_statistic']:.2f}"],
        ['  • p-valor', f"{estadisticas['p_value']:.2e}"],
        ['  • Significativo', 'SÍ' if estadisticas['p_value'] < 0.05 else 'NO']
    ]
    
    # Mostrar tabla
    y_pos = 0.95
    for fila in tabla_datos:
        if len(fila) == 2:
            text = f"{fila[0]:<25} {fila[1]}"
            weight = 'bold' if fila[0].isupper() or '─' in fila[0] else 'normal'
            ax6.text(0.05, y_pos, text, transform=ax6.transAxes, fontsize=10,
                    verticalalignment='top', fontweight=weight, fontfamily='monospace')
        y_pos -= 0.045
    
    ax6.set_title('RESULTADOS CUANTITATIVOS\nAnálisis estadístico completo', 
                  fontweight='bold', fontsize=14, pad=20)
    
    # Título general
    fig.suptitle('COMPARACIÓN DIRECTA: REGIÓN DE HUESO vs AGUA HOMOGÉNEA\n' + 
                 f'Análisis de {estadisticas["n_voxels"]:,} voxels en la misma ubicación anatómica (5M eventos)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.06)
    plt.savefig('COMPARACION_DIRECTA_REGION_HUESO.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: COMPARACION_DIRECTA_REGION_HUESO.png")
    plt.close()
    
    return estadisticas

def main():
    """Función principal"""
    estadisticas = analizar_region_hueso()
    
    print("\n" + "="*80)
    print("🎯 RESPUESTA DIRECTA A TU PREGUNTA:")
    print("="*80)
    print(f"🔍 DIFERENCIA MEDIA EN LA REGIÓN DEL HUESO:")
    print(f"   • Diferencia relativa: {estadisticas['diferencia_rel_media']:+.1f}% ± {estadisticas['diferencia_rel_std']:.1f}%")
    print(f"   • Diferencia absoluta: {estadisticas['diferencia_abs_media']:+.0f} ± {estadisticas['diferencia_abs_std']:.0f} MeV")
    print(f"   • Mediana: {estadisticas['diferencia_rel_mediana']:+.1f}%")
    print(f"   • Basado en: {estadisticas['n_voxels']:,} voxels analizados")
    
    print(f"\n📊 INTERPRETACIÓN:")
    if estadisticas['diferencia_rel_media'] > 0:
        print(f"   • El hueso AUMENTA la dosis en {estadisticas['diferencia_rel_media']:.1f}% promedio")
        print(f"   • Esto significa {estadisticas['diferencia_rel_media']/100:.2f} veces más dosis que agua")
    else:
        print(f"   • El hueso REDUCE la dosis en {abs(estadisticas['diferencia_rel_media']):.1f}% promedio")
    
    print(f"\n🧪 VALIDACIÓN ESTADÍSTICA:")
    print(f"   • p-valor: {estadisticas['p_value']:.2e}")
    if estadisticas['p_value'] < 0.001:
        print(f"   • Diferencia ALTAMENTE SIGNIFICATIVA (p < 0.001)")
    elif estadisticas['p_value'] < 0.05:
        print(f"   • Diferencia SIGNIFICATIVA (p < 0.05)")
    else:
        print(f"   • Diferencia NO significativa (p ≥ 0.05)")
    
    print(f"\n✅ ANÁLISIS COMPLETO GUARDADO EN: COMPARACION_DIRECTA_REGION_HUESO.png")
    print("="*80)

if __name__ == "__main__":
    main()

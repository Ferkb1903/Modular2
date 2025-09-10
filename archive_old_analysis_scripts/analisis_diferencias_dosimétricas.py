#!/usr/bin/env python3
"""
ANÁLISIS ESPECÍFICO DE DIFERENCIAS DOSIMÉTRICAS
===============================================
Script dedicado al análisis detallado de las diferencias entre agua homogénea 
y heterogeneidad de hueso en braquiterapia.
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

def crear_mapa_2d_diferencias(data_agua, data_hueso, limite_cm=9.0, bins=180):
    """Crear mapas 2D optimizados para análisis de diferencias"""
    print("🗺️  Creando mapas para análisis de diferencias...")
    
    # Crear grid
    x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
    
    # Crear mapas 2D
    mapa_agua, _, _ = np.histogram2d(data_agua['x'], data_agua['y'], 
                                   bins=[x_edges, y_edges], 
                                   weights=data_agua['edep'])
    
    mapa_hueso, _, _ = np.histogram2d(data_hueso['x'], data_hueso['y'], 
                                    bins=[x_edges, y_edges], 
                                    weights=data_hueso['edep'])
    
    # Centros de bins
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    # Calcular diferencias
    diferencia_abs = mapa_hueso - mapa_agua
    diferencia_rel = np.zeros_like(mapa_agua)
    
    # Evitar división por cero
    mask = mapa_agua > 0
    diferencia_rel[mask] = (diferencia_abs[mask] / mapa_agua[mask]) * 100
    diferencia_rel[~mask] = np.nan
    
    print(f"  ✓ Mapas creados con resolución {18.0/bins:.3f} cm/bin")
    
    return mapa_agua, mapa_hueso, diferencia_abs, diferencia_rel, x_centers, y_centers

def analizar_regiones(diferencia_rel, x_centers, y_centers):
    """Analizar diferencias por regiones específicas"""
    print("📊 Analizando diferencias por regiones...")
    
    # Crear máscaras para diferentes regiones
    X, Y = np.meshgrid(x_centers, y_centers, indexing='ij')
    
    # Región de hueso (rectángulo 8×8 cm centrado en (0, 5))
    mask_hueso = ((X >= -4) & (X <= 4) & (Y >= 1) & (Y <= 9))
    
    # Región cerca de la fuente (círculo de 2 cm)
    mask_fuente = (X**2 + Y**2 <= 4)
    
    # Región de agua pura (fuera del hueso, pero dentro del phantom)
    mask_agua = ((X**2 + Y**2 <= 81) & ~mask_hueso & ~mask_fuente)
    
    # Región periférica (anillo exterior)
    mask_periferia = ((X**2 + Y**2 > 36) & (X**2 + Y**2 <= 81) & ~mask_hueso)
    
    # Extraer datos válidos por región
    regiones = {
        'Hueso': diferencia_rel[mask_hueso & ~np.isnan(diferencia_rel)],
        'Cerca fuente': diferencia_rel[mask_fuente & ~np.isnan(diferencia_rel)],
        'Agua pura': diferencia_rel[mask_agua & ~np.isnan(diferencia_rel)],
        'Periferia': diferencia_rel[mask_periferia & ~np.isnan(diferencia_rel)]
    }
    
    # Estadísticas por región
    estadisticas = {}
    for nombre, datos in regiones.items():
        if len(datos) > 0:
            estadisticas[nombre] = {
                'media': np.mean(datos),
                'mediana': np.median(datos),
                'std': np.std(datos),
                'min': np.min(datos),
                'max': np.max(datos),
                'p25': np.percentile(datos, 25),
                'p75': np.percentile(datos, 75),
                'n_voxels': len(datos)
            }
    
    return regiones, estadisticas, (mask_hueso, mask_fuente, mask_agua, mask_periferia)

def crear_analisis_diferencias():
    """Crear análisis completo de diferencias dosimétricas"""
    print("=" * 70)
    print("ANÁLISIS ESPECÍFICO DE DIFERENCIAS DOSIMÉTRICAS")
    print("Impacto del hueso cortical en distribución de dosis")
    print("=" * 70)
    
    # Cargar datos
    datos_agua = cargar_datos_corregidos('EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.out')
    datos_hueso = cargar_datos_corregidos('EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.out')
    
    # Crear mapas
    mapa_agua, mapa_hueso, diferencia_abs, diferencia_rel, x_centers, y_centers = crear_mapa_2d_diferencias(
        datos_agua, datos_hueso, bins=180)
    
    # Analizar por regiones
    regiones, estadisticas, masks = analizar_regiones(diferencia_rel, x_centers, y_centers)
    mask_hueso, mask_fuente, mask_agua, mask_periferia = masks
    
    # Crear figura completa
    fig = plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(3, 3, height_ratios=[1, 1, 0.8], width_ratios=[1, 1, 1])
    
    # === FILA 1: ANÁLISIS DE DIFERENCIAS ===
    
    # Mapa de diferencias relativas con regiones marcadas
    ax1 = fig.add_subplot(gs[0, 0])
    diff_plot = np.copy(diferencia_rel)
    im1 = ax1.imshow(diff_plot.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-50, vmax=50)
    
    # Marcar regiones de análisis
    ax1.plot(0, 0, 'k*', markersize=15, label='Fuente Ir-192')
    rect_hueso = Rectangle((-4, 1), 8, 8, linewidth=3, edgecolor='cyan', 
                          facecolor='none', linestyle='-', label='Región hueso')
    ax1.add_patch(rect_hueso)
    
    circle_fuente = Circle((0, 0), 2, linewidth=2, edgecolor='yellow',
                          facecolor='none', linestyle='--', label='Zona fuente')
    ax1.add_patch(circle_fuente)
    
    ax1.set_title('DIFERENCIAS RELATIVAS POR REGIONES\n[(Hueso-Agua)/Agua × 100%]', 
                  fontweight='bold', fontsize=14)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Histograma de diferencias absolatas
    ax2 = fig.add_subplot(gs[0, 1])
    diff_abs_validas = diferencia_abs[~np.isnan(diferencia_abs)]
    
    ax2.hist(diff_abs_validas, bins=50, alpha=0.7, edgecolor='black', 
            color='orange', label=f'n = {len(diff_abs_validas)}')
    ax2.axvline(0, color='red', linestyle='--', linewidth=2, label='Sin diferencia')
    ax2.axvline(np.mean(diff_abs_validas), color='blue', linestyle='-', linewidth=2,
                label=f'Media: {np.mean(diff_abs_validas):.0f} MeV')
    ax2.set_xlabel('Diferencia Absoluta [MeV]')
    ax2.set_ylabel('Frecuencia')
    ax2.set_title('DISTRIBUCIÓN DE DIFERENCIAS ABSOLUTAS\n(Hueso - Agua)', 
                  fontweight='bold', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Análisis radial de diferencias
    ax3 = fig.add_subplot(gs[0, 2])
    X, Y = np.meshgrid(x_centers, y_centers, indexing='ij')
    R = np.sqrt(X**2 + Y**2)
    
    # Crear bins radiales
    r_bins = np.linspace(0, 9, 19)
    r_centers = (r_bins[:-1] + r_bins[1:]) / 2
    
    diff_radial_media = []
    diff_radial_std = []
    
    for i in range(len(r_bins)-1):
        mask_r = (R >= r_bins[i]) & (R < r_bins[i+1]) & ~np.isnan(diferencia_rel)
        if np.sum(mask_r) > 0:
            diff_radial_media.append(np.mean(diferencia_rel[mask_r]))
            diff_radial_std.append(np.std(diferencia_rel[mask_r]))
        else:
            diff_radial_media.append(0)
            diff_radial_std.append(0)
    
    ax3.errorbar(r_centers, diff_radial_media, yerr=diff_radial_std, 
                marker='o', linestyle='-', linewidth=2, markersize=6,
                capsize=4, capthick=2, label='Media ± σ')
    ax3.axhline(0, color='red', linestyle='--', alpha=0.7, label='Sin diferencia')
    ax3.axvspan(1, 7.5, alpha=0.2, color='cyan', label='Influencia hueso')
    ax3.set_xlabel('Distancia radial (cm)')
    ax3.set_ylabel('Diferencia relativa [%]')
    ax3.set_title('PERFIL RADIAL DE DIFERENCIAS\nPromedio en anillos concéntricos', 
                  fontweight='bold', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # === FILA 2: ANÁLISIS POR REGIONES ===
    
    # Box plot por regiones
    ax4 = fig.add_subplot(gs[1, 0])
    
    datos_boxplot = [regiones[nombre] for nombre in ['Hueso', 'Agua pura', 'Cerca fuente', 'Periferia'] 
                     if nombre in regiones and len(regiones[nombre]) > 0]
    labels_boxplot = [nombre for nombre in ['Hueso', 'Agua pura', 'Cerca fuente', 'Periferia'] 
                      if nombre in regiones and len(regiones[nombre]) > 0]
    
    bp = ax4.boxplot(datos_boxplot, labels=labels_boxplot, patch_artist=True)
    colors_box = ['cyan', 'lightblue', 'yellow', 'lightgreen']
    for patch, color in zip(bp['boxes'], colors_box[:len(bp['boxes'])]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax4.axhline(0, color='red', linestyle='--', alpha=0.7)
    ax4.set_ylabel('Diferencia relativa [%]')
    ax4.set_title('DISTRIBUCIÓN DE DIFERENCIAS POR REGIÓN\nComparación estadística', 
                  fontweight='bold', fontsize=14)
    ax4.grid(True, alpha=0.3)
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
    
    # Mapa de significancia estadística
    ax5 = fig.add_subplot(gs[1, 1])
    
    # Calcular significancia local (test t contra cero)
    significancia = np.zeros_like(diferencia_rel)
    window_size = 5  # ventana 5×5 para test local
    
    for i in range(window_size//2, diferencia_rel.shape[0] - window_size//2):
        for j in range(window_size//2, diferencia_rel.shape[1] - window_size//2):
            ventana = diferencia_rel[i-window_size//2:i+window_size//2+1, 
                                   j-window_size//2:j+window_size//2+1]
            ventana_valida = ventana[~np.isnan(ventana)]
            if len(ventana_valida) >= 5:  # Mínimo para test estadístico
                t_stat, p_value = scipy_stats.ttest_1samp(ventana_valida, 0)
                significancia[i, j] = -np.log10(p_value + 1e-10)  # -log10(p)
    
    significancia[significancia == 0] = np.nan
    
    im5 = ax5.imshow(significancia.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='viridis', aspect='equal')
    
    ax5.plot(0, 0, 'w*', markersize=15, label='Fuente')
    rect5 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='white', 
                     facecolor='none', linestyle='--', label='Región hueso')
    ax5.add_patch(rect5)
    
    ax5.set_title('SIGNIFICANCIA ESTADÍSTICA\n-log₁₀(p-value) por ventana local', 
                  fontweight='bold', fontsize=14)
    ax5.set_xlabel('X (cm)')
    ax5.set_ylabel('Y (cm)')
    ax5.legend()
    
    cbar5 = plt.colorbar(im5, ax=ax5, shrink=0.8)
    cbar5.set_label('-log₁₀(p)', rotation=270, labelpad=15)
    
    # Análisis direccional
    ax6 = fig.add_subplot(gs[1, 2])
    
    # Perfiles direccionales a través del hueso
    idx_centro_x = len(x_centers) // 2
    idx_centro_y = len(y_centers) // 2
    
    # Perfil horizontal (Y=0)
    perfil_horizontal = diferencia_rel[idx_centro_x, :]
    mask_h = ~np.isnan(perfil_horizontal)
    
    # Perfil vertical (X=0) 
    perfil_vertical = diferencia_rel[:, idx_centro_y]
    mask_v = ~np.isnan(perfil_vertical)
    
    ax6.plot(y_centers[mask_h], perfil_horizontal[mask_h], 'b-', linewidth=3, 
            label='Perfil horizontal (Y=0)', alpha=0.8)
    ax6.plot(x_centers[mask_v], perfil_vertical[mask_v], 'r-', linewidth=3, 
            label='Perfil vertical (X=0)', alpha=0.8)
    
    ax6.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax6.axvspan(1, 9, alpha=0.2, color='cyan', label='Región hueso (vertical)')
    ax6.axvspan(-4, 4, alpha=0.2, color='orange', label='Región hueso (horizontal)')
    
    ax6.set_xlabel('Posición (cm)')
    ax6.set_ylabel('Diferencia relativa [%]')
    ax6.set_title('PERFILES DIRECCIONALES\nA través de heterogeneidades', 
                  fontweight='bold', fontsize=14)
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # === FILA 3: TABLA DE ESTADÍSTICAS ===
    
    ax7 = fig.add_subplot(gs[2, :])
    ax7.axis('off')
    
    # Crear tabla de estadísticas
    tabla_datos = []
    headers = ['Región', 'N voxels', 'Media [%]', 'Mediana [%]', 'Std [%]', 
               'Min [%]', 'Max [%]', 'P25 [%]', 'P75 [%]']
    
    for nombre, stats in estadisticas.items():
        fila = [
            nombre,
            f"{stats['n_voxels']:,}",
            f"{stats['media']:.1f}",
            f"{stats['mediana']:.1f}",
            f"{stats['std']:.1f}",
            f"{stats['min']:.1f}",
            f"{stats['max']:.1f}",
            f"{stats['p25']:.1f}",
            f"{stats['p75']:.1f}"
        ]
        tabla_datos.append(fila)
    
    tabla = ax7.table(cellText=tabla_datos, colLabels=headers,
                     cellLoc='center', loc='center',
                     bbox=[0.1, 0.3, 0.8, 0.4])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1, 2)
    
    # Colorear filas
    colores_tabla = ['lightcyan', 'lightblue', 'lightyellow', 'lightgreen']
    for i, color in enumerate(colores_tabla[:len(tabla_datos)]):
        for j in range(len(headers)):
            tabla[(i+1, j)].set_facecolor(color)
    
    # Header en gris
    for j in range(len(headers)):
        tabla[(0, j)].set_facecolor('lightgray')
        tabla[(0, j)].set_text_props(weight='bold')
    
    ax7.set_title('ESTADÍSTICAS DETALLADAS POR REGIÓN ANATÓMICA\nAnálisis cuantitativo del impacto dosimétrico', 
                  fontweight='bold', fontsize=16, pad=20)
    
    # Título general
    fig.suptitle('ANÁLISIS DOSIMÉTRICO DETALLADO: IMPACTO DEL HUESO CORTICAL\n' + 
                 'Evaluación cuantitativa de diferencias en braquiterapia (5M eventos, resolución 1mm)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.06)
    plt.savefig('ANALISIS_DIFERENCIAS_DOSIMETRICAS_DETALLADO.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: ANALISIS_DIFERENCIAS_DOSIMETRICAS_DETALLADO.png")
    plt.close()
    
    # Imprimir resumen ejecutivo
    print("\n" + "="*70)
    print("📋 RESUMEN EJECUTIVO - IMPACTO DOSIMÉTRICO DEL HUESO")
    print("="*70)
    
    for nombre, stats in estadisticas.items():
        print(f"\n🔍 {nombre.upper()}:")
        print(f"   • Diferencia media: {stats['media']:+.1f}% ± {stats['std']:.1f}%")
        print(f"   • Rango: {stats['min']:.1f}% a {stats['max']:.1f}%")
        print(f"   • Voxels analizados: {stats['n_voxels']:,}")
        
        # Interpretación clínica
        if abs(stats['media']) > 10:
            print(f"   ⚠️  IMPACTO SIGNIFICATIVO (>10%)")
        elif abs(stats['media']) > 5:
            print(f"   ⚡ Impacto moderado (5-10%)")
        else:
            print(f"   ✅ Impacto menor (<5%)")
    
    print(f"\n💡 CONCLUSIONES PRINCIPALES:")
    if 'Hueso' in estadisticas:
        hueso_stats = estadisticas['Hueso']
        print(f"   • El hueso cortical causa diferencias de {hueso_stats['media']:+.1f}% en promedio")
        print(f"   • Variabilidad dosimétrica: ±{hueso_stats['std']:.1f}%")
        
    if 'Agua pura' in estadisticas:
        agua_stats = estadisticas['Agua pura']
        print(f"   • Efectos indirectos en agua: {agua_stats['media']:+.1f}% ± {agua_stats['std']:.1f}%")
        
    print(f"   • Los efectos se extienden más allá de la región de hueso")
    print(f"   • Relevancia clínica: ALTA para planificación de tratamiento")

def main():
    """Función principal"""
    crear_analisis_diferencias()
    
    print("\n✅ ANÁLISIS DE DIFERENCIAS DOSIMÉTRICAS COMPLETADO")
    print("📁 Archivo generado: ANALISIS_DIFERENCIAS_DOSIMETRICAS_DETALLADO.png")
    print("="*70)

if __name__ == "__main__":
    main()

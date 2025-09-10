#!/usr/bin/env python3
"""
COMPARACIÓN CON ESCALAS CONSISTENTES
===================================
Análisis con escalas de color apropiadas para mostrar la verdadera magnitud 
de las diferencias dosimétricas.
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

def analizar_escalas_consistentes():
    """Crear análisis con escalas de color consistentes y apropiadas"""
    print("=" * 80)
    print("ANÁLISIS CON ESCALAS CONSISTENTES")
    print("Evaluación de la verdadera magnitud de las diferencias")
    print("=" * 80)
    
    # Cargar datos
    datos_agua = cargar_datos_corregidos('EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.out')
    datos_hueso = cargar_datos_corregidos('EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.out')
    
    # Crear mapas
    print("\n🗺️  Creando mapas con análisis de rangos...")
    mapa_agua, x_centers, y_centers = crear_mapas_2d(datos_agua, bins=180)
    mapa_hueso, _, _ = crear_mapas_2d(datos_hueso, bins=180)
    
    # Calcular diferencias
    diferencia_abs = mapa_hueso - mapa_agua
    diferencia_rel = np.zeros_like(mapa_agua)
    
    mask_valido = mapa_agua > 0
    diferencia_rel[mask_valido] = (diferencia_abs[mask_valido] / mapa_agua[mask_valido]) * 100
    diferencia_rel[~mask_valido] = np.nan
    
    # Analizar estadísticas de diferencias para escalas apropiadas
    diff_validas = diferencia_rel[~np.isnan(diferencia_rel)]
    
    print(f"📊 ESTADÍSTICAS DE DIFERENCIAS REALES:")
    print(f"  • Media: {np.mean(diff_validas):.1f}%")
    print(f"  • Mediana: {np.median(diff_validas):.1f}%")
    print(f"  • Std: {np.std(diff_validas):.1f}%")
    print(f"  • Mín: {np.min(diff_validas):.1f}%")
    print(f"  • Máx: {np.max(diff_validas):.1f}%")
    print(f"  • P95: {np.percentile(diff_validas, 95):.1f}%")
    print(f"  • P99: {np.percentile(diff_validas, 99):.1f}%")
    
    # Definir escalas apropiadas
    # Escala 1: Conservadora (captura el 95% de los datos)
    p95 = np.percentile(diff_validas, 95)
    escala_conservadora = max(100, p95)
    
    # Escala 2: Completa (captura el 99% de los datos) 
    p99 = np.percentile(diff_validas, 99)
    escala_completa = max(200, p99)
    
    # Escala 3: Logarítmica para valores extremos
    diff_log = np.copy(diferencia_rel)
    mask_pos = (diferencia_rel > 0) & ~np.isnan(diferencia_rel)
    mask_neg = (diferencia_rel < 0) & ~np.isnan(diferencia_rel)
    diff_log[mask_pos] = np.log10(diferencia_rel[mask_pos] + 1)
    diff_log[mask_neg] = -np.log10(abs(diferencia_rel[mask_neg]) + 1)
    diff_log[diferencia_rel == 0] = 0
    
    print(f"\n🎨 ESCALAS DEFINIDAS:")
    print(f"  • Conservadora: ±{escala_conservadora:.0f}% (captura 95% datos)")
    print(f"  • Completa: ±{escala_completa:.0f}% (captura 99% datos)")
    print(f"  • Logarítmica: para valores extremos")
    
    # Crear figura comparativa
    fig = plt.figure(figsize=(24, 16))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1, 1, 0.6], width_ratios=[1, 1, 1, 1])
    
    # === FILA 1: ESCALAS DIFERENTES DE LA MISMA DATA ===
    
    # Escala muy conservadora (±50%)
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(diferencia_rel.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-50, vmax=50)
    
    ax1.plot(0, 0, 'k*', markersize=12)
    rect1 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='white', 
                     facecolor='none', linestyle='-')
    ax1.add_patch(rect1)
    
    ax1.set_title('ESCALA ±50%\n(Subestima diferencias)', fontweight='bold', fontsize=12)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Escala conservadora (P95)
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(diferencia_rel.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', 
                     vmin=-escala_conservadora, vmax=escala_conservadora)
    
    ax2.plot(0, 0, 'k*', markersize=12)
    rect2 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='white', 
                     facecolor='none', linestyle='-')
    ax2.add_patch(rect2)
    
    ax2.set_title(f'ESCALA ±{escala_conservadora:.0f}%\n(Captura 95% datos)', 
                  fontweight='bold', fontsize=12)
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Escala completa (P99)
    ax3 = fig.add_subplot(gs[0, 2])
    im3 = ax3.imshow(diferencia_rel.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', 
                     vmin=-escala_completa, vmax=escala_completa)
    
    ax3.plot(0, 0, 'k*', markersize=12)
    rect3 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='white', 
                     facecolor='none', linestyle='-')
    ax3.add_patch(rect3)
    
    ax3.set_title(f'ESCALA ±{escala_completa:.0f}%\n(Captura 99% datos)', 
                  fontweight='bold', fontsize=12)
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    
    cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
    cbar3.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Escala logarítmica
    ax4 = fig.add_subplot(gs[0, 3])
    im4 = ax4.imshow(diff_log.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-3, vmax=3)
    
    ax4.plot(0, 0, 'k*', markersize=12)
    rect4 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='white', 
                     facecolor='none', linestyle='-')
    ax4.add_patch(rect4)
    
    ax4.set_title('ESCALA LOGARÍTMICA\nlog₁₀(|diff|+1)', fontweight='bold', fontsize=12)
    ax4.set_xlabel('X (cm)')
    ax4.set_ylabel('Y (cm)')
    
    cbar4 = plt.colorbar(im4, ax=ax4, shrink=0.8)
    cbar4.set_label('log₁₀(|diff|+1)', rotation=270, labelpad=15)
    
    # === FILA 2: ANÁLISIS DE SATURACIÓN ===
    
    # Histograma mostrando saturación
    ax5 = fig.add_subplot(gs[1, 0])
    
    bins_hist = np.logspace(-1, 4, 100)  # Escala logarítmica
    ax5.hist(diff_validas[diff_validas > 0], bins=bins_hist, alpha=0.7, 
            color='red', label=f'Diferencias positivas (n={np.sum(diff_validas > 0):,})')
    ax5.hist(abs(diff_validas[diff_validas < 0]), bins=bins_hist, alpha=0.7, 
            color='blue', label=f'Diferencias negativas (n={np.sum(diff_validas < 0):,})')
    
    ax5.axvline(50, color='green', linestyle='--', linewidth=2, label='Límite ±50%')
    ax5.axvline(escala_conservadora, color='orange', linestyle='--', linewidth=2, 
               label=f'Límite ±{escala_conservadora:.0f}% (P95)')
    ax5.axvline(escala_completa, color='purple', linestyle='--', linewidth=2, 
               label=f'Límite ±{escala_completa:.0f}% (P99)')
    
    ax5.set_xscale('log')
    ax5.set_xlabel('|Diferencia| [%] (escala log)')
    ax5.set_ylabel('Frecuencia')
    ax5.set_title('DISTRIBUCIÓN DE DIFERENCIAS\nSaturación en diferentes escalas', 
                  fontweight='bold', fontsize=12)
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # Porcentaje de datos saturados
    ax6 = fig.add_subplot(gs[1, 1])
    
    escalas = [50, 100, escala_conservadora, escala_completa, 500, 1000]
    porcentajes_saturados = []
    
    for escala in escalas:
        saturados = np.sum(abs(diff_validas) > escala)
        porcentaje = (saturados / len(diff_validas)) * 100
        porcentajes_saturados.append(porcentaje)
    
    bars = ax6.bar(range(len(escalas)), porcentajes_saturados, 
                   color=['red', 'orange', 'yellow', 'lightgreen', 'green', 'blue'],
                   alpha=0.7, edgecolor='black')
    
    ax6.set_xticks(range(len(escalas)))
    ax6.set_xticklabels([f'±{int(e)}%' for e in escalas], rotation=45)
    ax6.set_ylabel('% Datos saturados')
    ax6.set_title('PÉRDIDA DE INFORMACIÓN\nPor saturación de escala', 
                  fontweight='bold', fontsize=12)
    ax6.grid(True, alpha=0.3)
    
    # Añadir valores en las barras
    for bar, porcentaje in zip(bars, porcentajes_saturados):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{porcentaje:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # Mapas lado a lado - comparación directa
    ax7 = fig.add_subplot(gs[1, 2])
    
    # Solo región del hueso con escala apropiada
    X, Y = np.meshgrid(x_centers, y_centers, indexing='ij')
    mask_hueso = ((X >= -4) & (X <= 4) & (Y >= 1) & (Y <= 9))
    
    diff_hueso = np.copy(diferencia_rel)
    diff_hueso[~mask_hueso] = np.nan
    
    im7 = ax7.imshow(diff_hueso.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='Reds', aspect='equal', vmin=0, vmax=escala_completa)
    
    ax7.plot(0, 0, 'k*', markersize=12)
    rect7 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='blue', 
                     facecolor='none', linestyle='-')
    ax7.add_patch(rect7)
    
    ax7.set_title('SOLO REGIÓN DEL HUESO\nEscala apropiada', fontweight='bold', fontsize=12)
    ax7.set_xlabel('X (cm)')
    ax7.set_ylabel('Y (cm)')
    
    cbar7 = plt.colorbar(im7, ax=ax7, shrink=0.8)
    cbar7.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # Valores extremos identificados
    ax8 = fig.add_subplot(gs[1, 3])
    
    # Encontrar voxels con diferencias extremas
    mask_extremos = abs(diferencia_rel) > 1000
    diff_extremos = np.copy(diferencia_rel)
    diff_extremos[~mask_extremos] = np.nan
    
    im8 = ax8.imshow(diff_extremos.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='plasma', aspect='equal')
    
    ax8.plot(0, 0, 'w*', markersize=12)
    
    ax8.set_title('VALORES EXTREMOS\n(>1000% diferencia)', fontweight='bold', fontsize=12)
    ax8.set_xlabel('X (cm)')
    ax8.set_ylabel('Y (cm)')
    
    cbar8 = plt.colorbar(im8, ax=ax8, shrink=0.8)
    cbar8.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # === FILA 3: TABLA COMPARATIVA ===
    
    ax9 = fig.add_subplot(gs[2, :])
    ax9.axis('off')
    
    # Crear tabla comparativa
    tabla_datos = [
        ['Escala', 'Rango [%]', 'Datos visibles', 'Datos saturados', 'Información perdida', 'Uso recomendado'],
        ['─'*15, '─'*15, '─'*15, '─'*15, '─'*20, '─'*25],
        ['±50%', '±50', f'{100-porcentajes_saturados[0]:.1f}%', f'{porcentajes_saturados[0]:.1f}%', 
         'ALTA - Subestima severamente', 'Vista general rápida'],
        ['±100%', '±100', f'{100-porcentajes_saturados[1]:.1f}%', f'{porcentajes_saturados[1]:.1f}%', 
         'MODERADA - Pierde detalles', 'Comparaciones básicas'],
        [f'±{escala_conservadora:.0f}% (P95)', f'±{escala_conservadora:.0f}', 
         f'{100-porcentajes_saturados[2]:.1f}%', f'{porcentajes_saturados[2]:.1f}%', 
         'BAJA - Captura mayoría', '✅ ANÁLISIS ESTÁNDAR'],
        [f'±{escala_completa:.0f}% (P99)', f'±{escala_completa:.0f}', 
         f'{100-porcentajes_saturados[3]:.1f}%', f'{porcentajes_saturados[3]:.1f}%', 
         'MUY BAJA - Casi completo', '✅ ANÁLISIS DETALLADO'],
        ['Logarítmica', 'log₁₀(|diff|+1)', '100%', '0%', 
         'NINGUNA - Escala no lineal', '✅ VALORES EXTREMOS']
    ]
    
    # Mostrar tabla
    y_pos = 0.9
    for i, fila in enumerate(tabla_datos):
        if i < 2:  # Headers
            weight = 'bold'
            color = 'black'
        elif '✅' in fila[-1]:  # Recomendados
            weight = 'bold'
            color = 'darkgreen'
        else:
            weight = 'normal'
            color = 'darkred'
            
        text = f"{fila[0]:<15} {fila[1]:<15} {fila[2]:<15} {fila[3]:<15} {fila[4]:<20} {fila[5]:<25}"
        ax9.text(0.02, y_pos, text, transform=ax9.transAxes, fontsize=9,
                verticalalignment='top', fontweight=weight, fontfamily='monospace',
                color=color)
        y_pos -= 0.12
    
    ax9.set_title('COMPARACIÓN DE ESCALAS DE COLOR - MISMOS DATOS, DIFERENTES VISUALIZACIONES\n' +
                  'Impacto de la elección de escala en la interpretación de resultados', 
                  fontweight='bold', fontsize=14, pad=20)
    
    # Título general
    fig.suptitle('ANÁLISIS DE CONSISTENCIA EN ESCALAS DE COLOR\n' + 
                 f'Evaluación de {len(diff_validas):,} voxels con diferencias reales de -100% a +{np.max(diff_validas):.0f}%',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.07)
    plt.savefig('ANALISIS_ESCALAS_CONSISTENTES.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: ANALISIS_ESCALAS_CONSISTENTES.png")
    plt.close()
    
    return {
        'diferencia_media': np.mean(diff_validas),
        'diferencia_mediana': np.median(diff_validas),
        'diferencia_std': np.std(diff_validas),
        'diferencia_max': np.max(diff_validas),
        'diferencia_min': np.min(diff_validas),
        'escala_conservadora': escala_conservadora,
        'escala_completa': escala_completa,
        'porcentajes_saturados': porcentajes_saturados
    }

def main():
    """Función principal"""
    resultados = analizar_escalas_consistentes()
    
    print("\n" + "="*80)
    print("🎯 RESPUESTA A TU OBSERVACIÓN:")
    print("="*80)
    print("SÍ, estoy usando los MISMOS DATOS pero con ESCALAS DIFERENTES.")
    print("\n🔍 PROBLEMA IDENTIFICADO:")
    print("  • Las escalas de ±50% y ±100% son INADECUADAS para estos datos")
    print("  • Los datos reales van de -100% a +{:.0f}%".format(resultados['diferencia_max']))
    print("  • La mayoría de información se pierde por 'saturación' de color")
    
    print(f"\n📊 ESCALAS RECOMENDADAS:")
    print(f"  ✅ Estándar: ±{resultados['escala_conservadora']:.0f}% (captura 95% de datos)")
    print(f"  ✅ Detallada: ±{resultados['escala_completa']:.0f}% (captura 99% de datos)")
    print(f"  ✅ Logarítmica: para valores extremos hasta +{resultados['diferencia_max']:.0f}%")
    
    print(f"\n⚠️  DATOS PERDIDOS CON ESCALAS PEQUEÑAS:")
    print(f"  • Escala ±50%: {resultados['porcentajes_saturados'][0]:.1f}% datos saturados")
    print(f"  • Escala ±100%: {resultados['porcentajes_saturados'][1]:.1f}% datos saturados")
    
    print(f"\n✅ ANÁLISIS COMPLETO GUARDADO EN: ANALISIS_ESCALAS_CONSISTENTES.png")
    print("="*80)

if __name__ == "__main__":
    main()

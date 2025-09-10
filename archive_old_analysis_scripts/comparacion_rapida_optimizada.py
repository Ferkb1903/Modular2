#!/usr/bin/env python3
"""
COMPARACIÓN RÁPIDA: GEOMETRÍA OPTIMIZADA vs ORIGINAL
Análisis de heterogeneidad en braquiterapia

Geometría Optimizada (Hueso): 18x18x18 cm phantom + 8x8x8 cm heterogeneidad  
Geometría Original (Agua): 30x30x30 cm phantom homogéneo
"""

import numpy as np
import matplotlib.pyplot as plt

def load_and_analyze(filename, title, color):
    """Cargar datos y calcular estadísticas básicas"""
    try:
        data = np.loadtxt(filename, skiprows=2)
        print(f"\n📊 {title}:")
        print(f"   📁 Archivo: {filename}")
        print(f"   📏 Puntos de datos: {len(data):,}")
        print(f"   ⚡ Energía total: {np.sum(data[:, 3]):.2e} MeV")
        print(f"   📈 Energía promedio: {np.mean(data[:, 3]):.2e} MeV")
        print(f"   📊 Energía máxima: {np.max(data[:, 3]):.2e} MeV")
        print(f"   📉 Energía mínima: {np.min(data[:, 3]):.2e} MeV")
        return data
    except Exception as e:
        print(f"❌ Error cargando {filename}: {e}")
        return None

def quick_comparison():
    """Comparación rápida de geometrías"""
    print("🎯 COMPARACIÓN RÁPIDA: GEOMETRÍA OPTIMIZADA vs ORIGINAL")
    print("=" * 65)
    
    # Cargar datos
    bone_data = load_and_analyze("EnergyDeposition_MEGA_Bone_Optimized.out", 
                                "GEOMETRÍA OPTIMIZADA (Hueso)", "red")
    
    water_data = load_and_analyze("../output/EnergyDeposition_MEGA_Water.out", 
                                 "GEOMETRÍA ORIGINAL (Agua)", "blue")
    
    if bone_data is None or water_data is None:
        print("❌ No se pudieron cargar ambos archivos")
        return
    
    print(f"\n🎯 ANÁLISIS COMPARATIVO:")
    print(f"   🔄 Ratio de energía total: {np.sum(bone_data[:, 3]) / np.sum(water_data[:, 3]):.2f}")
    print(f"   📊 Ratio de datos: {len(bone_data) / len(water_data):.2f}")
    
    # Crear gráfica rápida
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histograma de energías
    ax1.hist(bone_data[:, 3], bins=50, alpha=0.7, color='red', 
             label='Optimizada (Hueso)', density=True)
    ax1.hist(water_data[:, 3], bins=50, alpha=0.7, color='blue', 
             label='Original (Agua)', density=True)
    ax1.set_xlabel('Energía Depositada (MeV)')
    ax1.set_ylabel('Densidad de Probabilidad')
    ax1.set_title('Distribución de Energía Depositada')
    ax1.legend()
    ax1.set_yscale('log')
    
    # Comparación de totales
    totals = [np.sum(bone_data[:, 3]), np.sum(water_data[:, 3])]
    labels = ['Optimizada\n(Hueso)', 'Original\n(Agua)']
    colors = ['red', 'blue']
    
    bars = ax2.bar(labels, totals, color=colors, alpha=0.7)
    ax2.set_ylabel('Energía Total (MeV)')
    ax2.set_title('Energía Total Depositada')
    
    # Añadir valores en las barras
    for bar, total in zip(bars, totals):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{total:.2e}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('comparacion_geometrias_optimizada_vs_original.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: comparacion_geometrias_optimizada_vs_original.png")
    plt.show()

if __name__ == "__main__":
    quick_comparison()

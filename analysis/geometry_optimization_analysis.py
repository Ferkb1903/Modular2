#!/usr/bin/env python3
"""
🔍 ANÁLISIS DE OPTIMIZACIÓN GEOMÉTRICA PARA BRAQUITERAPIA
========================================================

Analiza la eficiencia de la geometría actual y propone optimizaciones
para reducir el tiempo de simulación manteniendo la precisión.

Autor: Equipo de Física Médica
Fecha: Septiembre 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import LogNorm
import warnings
warnings.filterwarnings('ignore')

def load_data_for_analysis(filename):
    """Cargar datos específicamente para análisis geométrico"""
    print(f"📂 Cargando: {filename}")
    data = []
    total_events = 0
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 4:
                # Datos en mm, convertir a cm para consistencia
                x = float(parts[0]) / 10.0  # mm -> cm
                y = float(parts[1]) / 10.0  # mm -> cm
                z = float(parts[2]) / 10.0  # mm -> cm
                energy = float(parts[3])    # MeV
                
                if energy > 0:  # Solo datos con energía
                    data.append([x, y, z, energy])
                    total_events += 1
    
    data = np.array(data)
    print(f"   ✅ Eventos válidos: {total_events:,}")
    print(f"   ✅ Rango X: [{np.min(data[:, 0]):.1f}, {np.max(data[:, 0]):.1f}] cm")
    print(f"   ✅ Rango Y: [{np.min(data[:, 1]):.1f}, {np.max(data[:, 1]):.1f}] cm")
    
    return data

def analyze_spatial_efficiency():
    """Analizar eficiencia espacial de la geometría actual"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS DE EFICIENCIA ESPACIAL")
    print("="*70)
    
    try:
        # Cargar datos de referencia (agua homogénea)
        data = load_data_for_analysis('../output/EnergyDeposition_MEGA_Water.out')
        
        if len(data) == 0:
            print("❌ No hay datos válidos para analizar")
            return None
            
        # Configuración actual
        current_size_cm = 32.0  # ±16 cm = 32 cm total
        current_bins = 320
        current_resolution = current_size_cm / current_bins  # cm/bin
        total_voxels = current_bins * current_bins
        used_voxels = len(data)
        
        print(f"\n🔹 CONFIGURACIÓN ACTUAL:")
        print(f"   • Tamaño del mesh: {current_size_cm}×{current_size_cm} cm")
        print(f"   • Número de bins: {current_bins}×{current_bins}")
        print(f"   • Resolución: {current_resolution:.3f} cm/voxel = {current_resolution*10:.1f} mm/voxel")
        print(f"   • Voxeles totales: {total_voxels:,}")
        print(f"   • Voxeles con datos: {used_voxels:,}")
        print(f"   • Eficiencia espacial: {used_voxels/total_voxels*100:.2f}%")
        
        # Análisis de distribución radial
        x, y = data[:, 0], data[:, 1]
        distances = np.sqrt(x**2 + y**2)
        energies = data[:, 3]
        
        print(f"\n🔹 DISTRIBUCIÓN RADIAL:")
        print(f"   • Distancia máxima con datos: {np.max(distances):.2f} cm")
        print(f"   • Distancia promedio: {np.mean(distances):.2f} cm")
        print(f"   • 90% de datos dentro de: {np.percentile(distances, 90):.2f} cm")
        print(f"   • 95% de datos dentro de: {np.percentile(distances, 95):.2f} cm")
        print(f"   • 99% de datos dentro de: {np.percentile(distances, 99):.2f} cm")
        
        return {
            'data': data,
            'distances': distances,
            'energies': energies,
            'current_size': current_size_cm,
            'current_bins': current_bins,
            'used_voxels': used_voxels,
            'total_voxels': total_voxels
        }
        
    except FileNotFoundError:
        print("❌ Archivo de datos no encontrado")
        return None

def analyze_energy_distribution(analysis_data):
    """Analizar distribución acumulativa de energía"""
    if analysis_data is None:
        return None
        
    print("\n" + "="*70)
    print("⚡ ANÁLISIS DE DISTRIBUCIÓN DE ENERGÍA")
    print("="*70)
    
    distances = analysis_data['distances']
    energies = analysis_data['energies']
    
    # Ordenar por distancia para análisis acumulativo
    sorted_indices = np.argsort(distances)
    sorted_distances = distances[sorted_indices]
    sorted_energies = energies[sorted_indices]
    
    # Energía acumulativa
    cumulative_energy = np.cumsum(sorted_energies)
    total_energy = cumulative_energy[-1]
    
    print(f"\n🔹 ENERGÍA TOTAL: {total_energy:.2f} MeV")
    
    # Encontrar distancias críticas
    percentiles = [50, 80, 90, 95, 99, 99.9]
    critical_distances = {}
    
    print(f"\n🔹 DISTANCIAS CRÍTICAS:")
    for p in percentiles:
        target_energy = (p/100) * total_energy
        idx = np.where(cumulative_energy >= target_energy)[0]
        if len(idx) > 0:
            distance = sorted_distances[idx[0]]
            critical_distances[p] = distance
            print(f"   • {p:4.1f}% energía: r ≤ {distance:5.2f} cm")
    
    return critical_distances

def recommend_optimization(analysis_data, critical_distances):
    """Generar recomendaciones de optimización"""
    if analysis_data is None or critical_distances is None:
        return
        
    print("\n" + "="*70)
    print("🎯 RECOMENDACIONES DE OPTIMIZACIÓN")
    print("="*70)
    
    current_size = analysis_data['current_size']
    current_bins = analysis_data['current_bins']
    
    # Escenarios de optimización
    scenarios = [
        ('Conservador (99% energía)', critical_distances.get(99, current_size/2)),
        ('Equilibrado (95% energía)', critical_distances.get(95, current_size/2)),
        ('Agresivo (90% energía)', critical_distances.get(90, current_size/2))
    ]
    
    print(f"\n🔹 ESCENARIOS DE OPTIMIZACIÓN:")
    
    for i, (name, radius) in enumerate(scenarios, 1):
        # Añadir 10% de margen de seguridad
        safe_radius = radius * 1.1
        new_size = safe_radius * 2
        
        # Mantener resolución similar
        new_bins = int(np.ceil(new_size / (current_size / current_bins)))
        # Redondear a múltiplos de 10 para simplicidad
        new_bins = ((new_bins + 9) // 10) * 10
        
        # Recalcular tamaño exacto
        final_size = new_bins * (current_size / current_bins)
        final_radius = final_size / 2
        
        # Cálculos de eficiencia
        volume_reduction = (current_size / final_size) ** 2
        voxel_reduction = (current_bins / new_bins) ** 2
        speedup_factor = voxel_reduction
        
        print(f"\n   {i}. {name}")
        print(f"      • Radio efectivo: {radius:.2f} cm → {final_radius:.2f} cm (con margen)")
        print(f"      • Nuevo mesh: {final_size:.1f}×{final_size:.1f} cm")
        print(f"      • Nuevos bins: {new_bins}×{new_bins}")
        print(f"      • Reducción de volumen: {volume_reduction:.1f}x")
        print(f"      • Reducción de voxeles: {voxel_reduction:.1f}x")
        print(f"      • Speedup esperado: ~{speedup_factor:.1f}x")
        print(f"      • Comando Geant4:")
        print(f"        /score/mesh/boxSize {final_radius:.1f} {final_radius:.1f} 0.0125 cm")
        print(f"        /score/mesh/nBin {new_bins} {new_bins} 1")

def create_optimization_visualization(analysis_data, critical_distances):
    """Crear visualización del análisis de optimización"""
    if analysis_data is None:
        return
        
    print("\n🎨 Generando visualización...")
    
    data = analysis_data['data']
    x, y = data[:, 0], data[:, 1]
    energies = data[:, 3]
    
    # Crear figura con múltiples subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Mapa de energía actual
    H, xedges, yedges = np.histogram2d(x, y, bins=100, weights=energies)
    extent = [-16, 16, -16, 16]
    
    im1 = ax1.imshow(H.T, extent=extent, origin='lower', cmap='hot', 
                     norm=LogNorm(vmin=np.percentile(H[H>0], 1), 
                                 vmax=np.percentile(H, 99)))
    ax1.set_title('Configuración Actual\n(±16 cm)', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    # Marcar límites actuales y heterogeneidad
    current_rect = Rectangle((-16, -16), 32, 32, linewidth=2, 
                           edgecolor='cyan', facecolor='none', linestyle='--')
    ax1.add_patch(current_rect)
    hetero_rect = Rectangle((-3, 3), 6, 6, linewidth=2, 
                          edgecolor='lime', facecolor='none')
    ax1.add_patch(hetero_rect)
    ax1.plot(0, 0, 'w*', markersize=10)
    
    # 2. Optimización conservadora (99%)
    if 99 in critical_distances:
        radius_99 = critical_distances[99] * 1.1
        xlim_99 = [-radius_99, radius_99]
        ylim_99 = [-radius_99, radius_99]
        
        im2 = ax2.imshow(H.T, extent=extent, origin='lower', cmap='hot',
                        norm=LogNorm(vmin=np.percentile(H[H>0], 1), 
                                    vmax=np.percentile(H, 99)))
        ax2.set_xlim(xlim_99)
        ax2.set_ylim(ylim_99)
        ax2.set_title(f'Optimización Conservadora\n(±{radius_99:.1f} cm, 99% energía)', 
                     fontweight='bold')
        ax2.set_xlabel('X (cm)')
        ax2.set_ylabel('Y (cm)')
        
        # Marcar nuevo límite
        new_rect = Rectangle((-radius_99, -radius_99), 2*radius_99, 2*radius_99, 
                           linewidth=3, edgecolor='red', facecolor='none')
        ax2.add_patch(new_rect)
        hetero_rect2 = Rectangle((-3, 3), 6, 6, linewidth=2, 
                               edgecolor='lime', facecolor='none')
        ax2.add_patch(hetero_rect2)
        ax2.plot(0, 0, 'w*', markersize=10)
    
    # 3. Distribución radial de energía
    distances = analysis_data['distances']
    energies = analysis_data['energies']
    
    # Binning radial
    r_bins = np.linspace(0, 16, 50)
    r_centers = (r_bins[1:] + r_bins[:-1]) / 2
    r_energy = []
    
    for i in range(len(r_bins)-1):
        mask = (distances >= r_bins[i]) & (distances < r_bins[i+1])
        r_energy.append(np.sum(energies[mask]))
    
    ax3.plot(r_centers, r_energy, 'b-', linewidth=2, label='Energía por anillo')
    ax3.set_xlabel('Distancia radial (cm)')
    ax3.set_ylabel('Energía depositada (MeV)')
    ax3.set_title('Distribución Radial de Energía', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Marcar distancias críticas
    colors = ['orange', 'red', 'darkred']
    percentiles_plot = [90, 95, 99]
    for i, p in enumerate(percentiles_plot):
        if p in critical_distances:
            ax3.axvline(critical_distances[p], color=colors[i], linestyle='--', 
                       label=f'{p}% energía')
    
    ax3.legend()
    
    # 4. Energía acumulativa
    sorted_indices = np.argsort(distances)
    sorted_distances = distances[sorted_indices]
    cumulative_energy = np.cumsum(energies[sorted_indices])
    cumulative_percent = cumulative_energy / cumulative_energy[-1] * 100
    
    ax4.plot(sorted_distances, cumulative_percent, 'g-', linewidth=2)
    ax4.set_xlabel('Distancia radial (cm)')
    ax4.set_ylabel('Energía acumulativa (%)')
    ax4.set_title('Energía Acumulativa vs Distancia', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Marcar percentiles importantes
    for i, p in enumerate(percentiles_plot):
        if p in critical_distances:
            ax4.axhline(p, color=colors[i], linestyle='--', alpha=0.7)
            ax4.axvline(critical_distances[p], color=colors[i], linestyle='--', 
                       label=f'{p}%: r={critical_distances[p]:.1f} cm')
    
    ax4.legend()
    ax4.set_ylim([80, 100])
    
    plt.tight_layout()
    
    # Guardar figura
    output_file = '../results/geometry_optimization_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Visualización guardada: {output_file}")
    
    return fig

def main():
    print("🔍 ANÁLISIS DE OPTIMIZACIÓN GEOMÉTRICA PARA BRAQUITERAPIA")
    print("=" * 65)
    
    try:
        # Paso 1: Análisis de eficiencia espacial
        analysis_data = analyze_spatial_efficiency()
        
        if analysis_data is None:
            print("❌ No se puede continuar sin datos válidos")
            return
        
        # Paso 2: Análisis de distribución de energía
        critical_distances = analyze_energy_distribution(analysis_data)
        
        # Paso 3: Recomendaciones
        recommend_optimization(analysis_data, critical_distances)
        
        # Paso 4: Visualización
        fig = create_optimization_visualization(analysis_data, critical_distances)
        
        print(f"\n✨ ANÁLISIS DE OPTIMIZACIÓN COMPLETADO ✨")
        print(f"📈 Visualización generada para guiar la optimización")
        
        plt.show()
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

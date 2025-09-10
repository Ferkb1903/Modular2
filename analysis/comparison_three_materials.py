#!/usr/bin/env python3
"""
ANÁLISIS COMPARATIVO DE HETEROGENEIDADES EN BRAQUITERAPIA
=========================================================

Compara los efectos de diferentes heterogeneidades:
1. Hueso (ρ ≈ 1.85 g/cm³) - Mayor densidad
2. Tejido Adiposo (ρ ≈ 0.95 g/cm³) - Menor densidad 
3. Agua pura (ρ = 1.00 g/cm³) - Referencia homogénea

Autor: Equipo de Física Médica
Fecha: Septiembre 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
import warnings
warnings.filterwarnings('ignore')

def load_data(filename):
    """Cargar datos del archivo de deposición de energía"""
    print(f"📂 Cargando: {filename}")
    data = []
    total_events = 0
    total_energy = 0.0
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 4:
                # Convertir de mm a cm (datos en mm, configuración en cm)
                x = float(parts[0]) / 10.0  # mm -> cm
                y = float(parts[1]) / 10.0  # mm -> cm
                z = float(parts[2]) / 10.0  # mm -> cm
                energy = float(parts[3])
                
                data.append([x, y, z, energy])
                total_events += 1
                total_energy += energy
    
    print(f"   ✅ Eventos: {total_events:,}")
    print(f"   ✅ Energía total: {total_energy:.6f} MeV")
    print(f"   ✅ Rango X: [{min(d[0] for d in data):.1f}, {max(d[0] for d in data):.1f}] cm")
    print(f"   ✅ Rango Y: [{min(d[1] for d in data):.1f}, {max(d[1] for d in data):.1f}] cm")
    
    return np.array(data), total_energy

def create_2d_map(data, title, energy_total, vmin=None, vmax=None):
    """Crear mapa 2D de deposición de energía"""
    
    # Crear bins para el mapa 2D
    x_bins = np.linspace(-16, 16, 321)  # 320 bins
    y_bins = np.linspace(-16, 16, 321)  # 320 bins
    
    # Crear histograma 2D
    H, xedges, yedges = np.histogram2d(data[:, 0], data[:, 1], 
                                      bins=[x_bins, y_bins], 
                                      weights=data[:, 3])
    
    # Configurar figura
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    
    # Crear mapa con escala logarítmica
    H_plot = H.T  # Transponer para orientación correcta
    H_plot[H_plot <= 0] = 1e-10  # Evitar log(0)
    
    im = ax.imshow(H_plot, extent=[-16, 16, -16, 16], 
                   origin='lower', cmap='hot', 
                   norm=LogNorm(vmin=vmin, vmax=vmax))
    
    # Marcadores geométricos
    # Límites del phantom (32x32 cm, mostrar hasta ±16 cm)
    phantom_rect = Rectangle((-16, -16), 32, 32, linewidth=2, 
                           edgecolor='cyan', facecolor='none', 
                           linestyle='--', alpha=0.8)
    ax.add_patch(phantom_rect)
    
    # Cubo de heterogeneidad (6x6 cm en x=0, y=6 cm)
    hetero_rect = Rectangle((-3, 3), 6, 6, linewidth=2, 
                          edgecolor='lime', facecolor='none', 
                          linestyle='-', alpha=0.9)
    ax.add_patch(hetero_rect)
    
    # Posición de la fuente (origen)
    ax.plot(0, 0, 'w*', markersize=15, markeredgecolor='black', 
            markeredgewidth=1, label='Fuente Ir-192')
    
    # Configuración
    ax.set_xlabel('X (cm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y (cm)', fontsize=12, fontweight='bold')
    ax.set_title(f'{title}\n(Energía total: {energy_total:.6f} MeV)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Energía Depositada (MeV)', fontsize=11, fontweight='bold')
    
    # Leyenda
    ax.legend(loc='upper right', fontsize=10, fancybox=True, 
              framealpha=0.9, edgecolor='black')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.set_xlim(-16, 16)
    ax.set_ylim(-16, 16)
    
    plt.tight_layout()
    return fig, H

def analyze_heterogeneity_effects(data_bone, data_fat, data_water, 
                                energy_bone, energy_fat, energy_water):
    """Analizar efectos de heterogeneidades"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS COMPARATIVO DE HETEROGENEIDADES")
    print("="*70)
    
    # Energías totales
    print(f"\n🔹 ENERGÍAS TOTALES:")
    print(f"   • Hueso:         {energy_bone:.6f} MeV")
    print(f"   • Tejido Adiposo: {energy_fat:.6f} MeV") 
    print(f"   • Agua (ref):    {energy_water:.6f} MeV")
    
    # Diferencias respecto al agua
    diff_bone = ((energy_bone - energy_water) / energy_water) * 100
    diff_fat = ((energy_fat - energy_water) / energy_water) * 100
    
    print(f"\n🔸 DIFERENCIAS RESPECTO AL AGUA:")
    print(f"   • Hueso:         {diff_bone:+.3f}%")
    print(f"   • Tejido Adiposo: {diff_fat:+.3f}%")
    
    # Diferencia entre materiales heterogéneos
    diff_bone_fat = ((energy_bone - energy_fat) / energy_fat) * 100
    print(f"\n🔸 DIFERENCIA HUESO vs TEJIDO ADIPOSO:")
    print(f"   • Hueso vs Adiposo: {diff_bone_fat:+.3f}%")
    
    # Análisis por regiones
    print(f"\n🔸 ANÁLISIS POR REGIONES:")
    
    # Región del cubo heterogéneo (x: -3 a 3, y: 3 a 9)
    mask_hetero = ((data_water[:, 0] >= -3) & (data_water[:, 0] <= 3) & 
                   (data_water[:, 1] >= 3) & (data_water[:, 1] <= 9))
    
    mask_hetero_bone = ((data_bone[:, 0] >= -3) & (data_bone[:, 0] <= 3) & 
                        (data_bone[:, 1] >= 3) & (data_bone[:, 1] <= 9))
    
    mask_hetero_fat = ((data_fat[:, 0] >= -3) & (data_fat[:, 0] <= 3) & 
                       (data_fat[:, 1] >= 3) & (data_fat[:, 1] <= 9))
    
    energy_hetero_water = data_water[mask_hetero, 3].sum()
    energy_hetero_bone = data_bone[mask_hetero_bone, 3].sum()
    energy_hetero_fat = data_fat[mask_hetero_fat, 3].sum()
    
    print(f"   🎯 Región heterogénea (-3≤x≤3, 3≤y≤9):")
    print(f"     • Agua:          {energy_hetero_water:.6f} MeV")
    print(f"     • Hueso:         {energy_hetero_bone:.6f} MeV")
    print(f"     • Tejido Adiposo: {energy_hetero_fat:.6f} MeV")
    
    diff_hetero_bone = ((energy_hetero_bone - energy_hetero_water) / energy_hetero_water) * 100
    diff_hetero_fat = ((energy_hetero_fat - energy_hetero_water) / energy_hetero_water) * 100
    
    print(f"     • Dif. Hueso:    {diff_hetero_bone:+.3f}%")
    print(f"     • Dif. Adiposo:  {diff_hetero_fat:+.3f}%")
    
    # Interpretación física
    print(f"\n🔬 INTERPRETACIÓN FÍSICA:")
    print(f"   • HUESO (ρ≈1.85): Mayor densidad → Mayor atenuación")
    print(f"     ∘ Absorbe más radiación en la región heterogénea")
    print(f"     ∘ Efecto: {diff_bone:+.3f}% en energía total")
    print(f"   • TEJIDO ADIPOSO (ρ≈0.95): Menor densidad → Menor atenuación") 
    print(f"     ∘ Permite mayor penetración de radiación")
    print(f"     ∘ Efecto: {diff_fat:+.3f}% en energía total")
    print(f"   • AGUA (ρ=1.00): Referencia homogénea")

def main():
    print("🧬 ANÁLISIS COMPARATIVO DE HETEROGENEIDADES EN BRAQUITERAPIA")
    print("=" * 65)
    
    try:
        # Cargar datos
        data_bone, energy_bone = load_data('EnergyDeposition_MEGA.out')
        data_fat, energy_fat = load_data('EnergyDeposition_MEGA_Fat.out') 
        data_water, energy_water = load_data('EnergyDeposition_MEGA_Water.out')
        
        # Determinar escala común para comparación
        all_energies = np.concatenate([data_bone[:, 3], data_fat[:, 3], data_water[:, 3]])
        vmin = np.percentile(all_energies[all_energies > 0], 1)
        vmax = np.percentile(all_energies, 99)
        
        print(f"\n🎨 Escala de colores: [{vmin:.2e}, {vmax:.2e}] MeV")
        
        # Crear mapas comparativos
        print(f"\n📊 Generando visualizaciones comparativas...")
        
        fig_bone, H_bone = create_2d_map(data_bone, 
                                        'PHANTOM HETEROGÉNEO - HUESO\n(ρ ≈ 1.85 g/cm³)', 
                                        energy_bone, vmin, vmax)
        
        fig_fat, H_fat = create_2d_map(data_fat, 
                                      'PHANTOM HETEROGÉNEO - TEJIDO ADIPOSO\n(ρ ≈ 0.95 g/cm³)', 
                                      energy_fat, vmin, vmax)
        
        fig_water, H_water = create_2d_map(data_water, 
                                          'PHANTOM HOMOGÉNEO - AGUA\n(ρ = 1.00 g/cm³)', 
                                          energy_water, vmin, vmax)
        
        # Guardar figuras
        print(f"\n💾 Guardando figuras...")
        fig_bone.savefig('mapa_energia_hueso.png', dpi=300, bbox_inches='tight')
        fig_fat.savefig('mapa_energia_tejido_adiposo.png', dpi=300, bbox_inches='tight')
        fig_water.savefig('mapa_energia_agua.png', dpi=300, bbox_inches='tight')
        
        print(f"   ✅ mapa_energia_hueso.png")
        print(f"   ✅ mapa_energia_tejido_adiposo.png") 
        print(f"   ✅ mapa_energia_agua.png")
        
        # Análisis comparativo
        analyze_heterogeneity_effects(data_bone, data_fat, data_water, 
                                    energy_bone, energy_fat, energy_water)
        
        print(f"\n✨ ANÁLISIS COMPLETADO ✨")
        print(f"📈 Se generaron 3 mapas de energía para comparación")
        
        plt.show()
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontró el archivo {e.filename}")
        print(f"   Asegúrate de que las simulaciones se hayan ejecutado correctamente")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print(f"   Verifica que los archivos de datos tengan el formato correcto")

if __name__ == "__main__":
    main()

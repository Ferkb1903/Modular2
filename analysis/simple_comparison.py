#!/usr/bin/env python3
"""
🔬 ANÁLISIS SIMPLE: PHANTOM HETEROGÉNEO vs HOMOGÉNEO
===================================================

Comparación directa y clara entre:
- Phantom con heterogeneidades (agua + hueso)
- Phantom homogéneo (solo agua)

Autor: Equipo de Física Médica
Fecha: Septiembre 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm

def load_data(filename):
    """Carga datos de deposición de energía."""
    print(f"📊 Cargando: {filename}")
    data = np.loadtxt(filename, comments='#')
    x = data[:, 0] / 10.0  # Convertir de mm a cm
    y = data[:, 1] / 10.0  # Convertir de mm a cm
    dose = data[:, 3]      # MeV (sin conversión)
    print(f"   ✅ {len(dose)} voxeles cargados")
    print(f"   📏 Rango X: {np.min(x):.1f} a {np.max(x):.1f} cm")
    print(f"   📏 Rango Y: {np.min(y):.1f} a {np.max(y):.1f} cm")
    return x, y, dose

def create_2d_map(x, y, dose):
    """Crea mapa 2D de dosis."""
    # Grid regular
    x_unique = np.unique(x)
    y_unique = np.unique(y)
    X, Y = np.meshgrid(x_unique, y_unique)
    Z = np.zeros_like(X)
    
    # Llenar datos
    for xi, yi, di in zip(x, y, dose):
        x_idx = np.where(x_unique == xi)[0][0]
        y_idx = np.where(y_unique == yi)[0][0]
        Z[y_idx, x_idx] = di
    
    return X, Y, Z

def main():
    print("🚀 ANÁLISIS SIMPLE DE HETEROGENEIDADES")
    print("=" * 50)
    
    try:
        # Cargar datos (ajustar rutas para nueva estructura)
        x_hetero, y_hetero, dose_hetero = load_data('../output/EnergyDeposition_MEGA.out')
        x_homo, y_homo, dose_homo = load_data('../output/EnergyDeposition_MEGA_Water.out')
        
        # Estadísticas básicas
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   💎 Heterogéneo: {np.sum(dose_hetero):.0f} MeV total")
        print(f"   💧 Homogéneo:   {np.sum(dose_homo):.0f} MeV total")
        print(f"   🔄 Diferencia:  {((np.sum(dose_hetero)-np.sum(dose_homo))/np.sum(dose_homo)*100):+.2f}%")
        
        # Crear mapas 2D
        print(f"\n🗺️ Creando mapas 2D...")
        X_het, Y_het, Z_het = create_2d_map(x_hetero, y_hetero, dose_hetero)
        X_hom, Y_hom, Z_hom = create_2d_map(x_homo, y_homo, dose_homo)
    
    print(f"   📏 Mapa heterogéneo: {Z_het.shape}")
    print(f"   📏 Mapa homogéneo:   {Z_hom.shape}")
    
    # Ajustar tamaños si son diferentes
    if Z_het.shape != Z_hom.shape:
        min_rows = min(Z_het.shape[0], Z_hom.shape[0])
        min_cols = min(Z_het.shape[1], Z_hom.shape[1])
        Z_het = Z_het[:min_rows, :min_cols]
        Z_hom = Z_hom[:min_rows, :min_cols]
        X_het = X_het[:min_rows, :min_cols]
        Y_het = Y_het[:min_rows, :min_cols]
        print(f"   ✂️ Ajustado a: {Z_het.shape}")
    
    # Calcular diferencia
    diff = Z_het - Z_hom
    diff_percent = np.zeros_like(diff)
    mask = Z_hom > 0
    diff_percent[mask] = 100 * (Z_het[mask] - Z_hom[mask]) / Z_hom[mask]
    
    # Crear figura
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🔬 COMPARACIÓN SIMPLE: HETEROGÉNEO vs HOMOGÉNEO\n' +
                 '💎 Agua+Hueso vs 💧 Solo Agua | 🎯 10M Eventos c/u',
                 fontsize=16, fontweight='bold')
    
    # Usar escala logarítmica para mejor visualización
    z_min = min(np.min(Z_het[Z_het > 0]), np.min(Z_hom[Z_hom > 0])) * 0.1
    z_max = max(np.max(Z_het), np.max(Z_hom))
    levels_log = np.logspace(np.log10(z_min), np.log10(z_max), 30)
    
    # 1. Phantom Heterogéneo
    ax1 = axes[0, 0]
    im1 = ax1.contourf(X_het, Y_het, np.maximum(Z_het, z_min), 
                       levels=levels_log, cmap='hot', norm=LogNorm())
    
    # Marcadores visuales
    # Phantom boundary (32x32 cm total según mesh)
    phantom_boundary = Rectangle((-16, -16), 32, 32, linewidth=3, edgecolor='cyan', 
                                facecolor='none', linestyle='-', alpha=0.8)
    ax1.add_patch(phantom_boundary)
    
    # Bone cube (6x6 cm en posición (0, 6, 0) cm según código fuente)
    # Centro en Y=6, entonces va de Y=3 a Y=9, X=-3 a X=3
    bone_cube = Rectangle((-3, 3), 6, 6, linewidth=3, edgecolor='yellow', 
                         facecolor='none', linestyle='-', alpha=0.9)
    ax1.add_patch(bone_cube)
    
    # Source en el centro
    ax1.plot(0, 0, '+', color='white', markersize=15, markeredgewidth=3)
    
    ax1.set_title('💎 PHANTOM HETEROGÉNEO\n(Agua + Hueso 6×6×6 cm³)', fontweight='bold')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.grid(True, alpha=0.3)
    ax1.text(0, 6, 'HUESO\n6×6×6 cm³', ha='center', va='center', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8),
             fontweight='bold', fontsize=10)
    cbar1 = plt.colorbar(im1, ax=ax1, label='Energy Deposition (MeV)')
    cbar1.ax.set_ylabel('Energy Deposition (MeV) - Log Scale', rotation=270, labelpad=20)
    
    # Leyenda
    ax1.legend([phantom_boundary, bone_cube], 
              ['Phantom Boundary', 'Bone Cube'], 
              loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # 2. Phantom Homogéneo  
    ax2 = axes[0, 1]
    im2 = ax2.contourf(X_het, Y_het, np.maximum(Z_hom, z_min), 
                       levels=levels_log, cmap='hot', norm=LogNorm())
    
    # Marcadores visuales
    # Phantom boundary (32x32 cm total según mesh)
    phantom_boundary2 = Rectangle((-16, -16), 32, 32, linewidth=3, edgecolor='cyan', 
                                 facecolor='none', linestyle='-', alpha=0.8)
    ax2.add_patch(phantom_boundary2)    # Source en el centro
    ax2.plot(0, 0, '+', color='white', markersize=15, markeredgewidth=3)
    
    ax2.set_title('💧 PHANTOM HOMOGÉNEO\n(Solo Agua)', fontweight='bold')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(im2, ax=ax2, label='Energy Deposition (MeV)')
    cbar2.ax.set_ylabel('Energy Deposition (MeV) - Log Scale', rotation=270, labelpad=20)
    
    # Leyenda
    ax2.legend([phantom_boundary2], 
              ['Phantom Boundary'], 
              loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # 3. Diferencia Absoluta
    ax3 = axes[1, 0]
    im3 = ax3.contourf(X_het, Y_het, diff, levels=50, cmap='RdBu_r', extend='both')
    
    # Marcadores visuales
    phantom_boundary3 = Rectangle((-16, -16), 32, 32, linewidth=2, edgecolor='cyan', 
                                 facecolor='none', linestyle='-', alpha=0.7)
    ax3.add_patch(phantom_boundary3)
    
    bone_cube3 = Rectangle((-3, 3), 6, 6, linewidth=2, edgecolor='yellow', 
                          facecolor='none', linestyle='--', alpha=0.8)
    ax3.add_patch(bone_cube3)
    
    ax3.plot(0, 0, '+', color='black', markersize=12, markeredgewidth=2)
    
    ax3.set_title('🔄 DIFERENCIA ABSOLUTA\n(Heterogéneo - Homogéneo)', fontweight='bold')
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Y (cm)')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(im3, ax=ax3, label='Δ Energy Deposition (MeV)')
    
    # 4. Diferencia Relativa
    ax4 = axes[1, 1]
    levels_rel = np.linspace(-15, 15, 31)
    im4 = ax4.contourf(X_het, Y_het, diff_percent, levels=levels_rel, cmap='RdBu_r', extend='both')
    
    # Marcadores visuales
    phantom_boundary4 = Rectangle((-16, -16), 32, 32, linewidth=2, edgecolor='cyan', 
                                 facecolor='none', linestyle='-', alpha=0.7)
    ax4.add_patch(phantom_boundary4)
    
    bone_cube4 = Rectangle((-3, 3), 6, 6, linewidth=2, edgecolor='yellow', 
                          facecolor='none', linestyle='--', alpha=0.8)
    ax4.add_patch(bone_cube4)
    
    ax4.plot(0, 0, '+', color='black', markersize=12, markeredgewidth=2)
    
    ax4.set_title('📊 DIFERENCIA RELATIVA\n[(Het-Hom)/Hom × 100%]', fontweight='bold')
    ax4.set_xlabel('X (cm)')
    ax4.set_ylabel('Y (cm)')
    ax4.grid(True, alpha=0.3)
    plt.colorbar(im4, ax=ax4, label='Difference (%)')
    
    plt.tight_layout()
    
    # Guardar figura (ajustar ruta para nueva estructura)
    output_file = '../results/simple_heterogeneity_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figura guardada: {output_file}")
    
    # Estadísticas de diferencias
    print(f"\n📊 ESTADÍSTICAS DE DIFERENCIAS:")
    print(f"   🔄 Diferencia absoluta promedio: {np.mean(diff):.2f} MeV")
    print(f"   📈 Diferencia relativa promedio: {np.mean(diff_percent[mask]):.2f}%")
    print(f"   📊 Rango diferencia relativa: {np.min(diff_percent[mask]):.1f}% a {np.max(diff_percent[mask]):.1f}%")
    
    # Mostrar
    plt.show()
    
    print(f"\n🎉 ANÁLISIS COMPLETADO")
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontró el archivo")
        print(f"   Verifica que los archivos estén en ../output/")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()

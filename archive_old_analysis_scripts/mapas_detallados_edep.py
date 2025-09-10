#!/usr/bin/env python3
"""
ANÁLISIS DETALLADO DE MAPAS DE DEPOSICIÓN DE ENERGÍA 2D
=======================================================
Script para crear mapas 2D detallados y análisis de diferencias
entre agua homogénea y heterogeneidad de hueso.

Autor: GitHub Copilot
Fecha: Septiembre 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
import seaborn as sns

# Configuración de matplotlib para alta calidad
plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

def cargar_datos(filename):
    """Cargar datos de deposición de energía de Geant4"""
    print(f"📂 Cargando: {filename}")
    
    # Leer datos con pandas (formato: i j k value)
    data = pd.read_csv(filename, sep=r'\s+', comment='#', header=None)
    data.columns = ['i', 'j', 'k', 'edep']
    
    # Convertir índices a coordenadas físicas
    # Malla: 360×360 bins, rango ±9 cm
    bin_size = 18.0 / 360  # 0.05 cm por bin
    data['x'] = (data['i'] - 180) * bin_size  # Centrar en 0
    data['y'] = (data['j'] - 180) * bin_size
    data['z'] = (data['k'] - 0.5) * 0.0125    # Espesor de 0.0125 cm
    
    print(f"  ✓ {len(data)} puntos cargados")
    print(f"  ✓ Energía total: {data['edep'].sum():.2e} MeV")
    print(f"  ✓ Rango X: {data['x'].min():.2f} a {data['x'].max():.2f} cm")
    print(f"  ✓ Rango Y: {data['y'].min():.2f} a {data['y'].max():.2f} cm")
    
    return data

def crear_mapa_2d(data, titulo, limite_cm=9.0, bins=360):
    """Crear mapa 2D de deposición de energía"""
    print(f"🗺️  Creando mapa: {titulo}")
    
    # Crear grid para el mapa
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
    
    return mapa, x_centers, y_centers

def plot_mapa_individual(mapa, x_centers, y_centers, titulo, filename, 
                        mostrar_heterogeneidad=False):
    """Crear plot individual de un mapa"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Usar logaritmo para mejor visualización
    mapa_log = np.log10(mapa + 1e-10)  # Evitar log(0)
    mapa_log[mapa == 0] = np.nan  # Puntos sin energía en blanco
    
    # Crear colormap
    im = ax.imshow(mapa_log.T, origin='lower', 
                   extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                   cmap='hot', aspect='equal')
    
    # Marcar posición de la fuente
    ax.plot(0, 0, 'w*', markersize=15, markeredgecolor='black', markeredgewidth=1,
            label='Fuente Ir-192')
    
    # Marcar región de heterogeneidad si es necesario
    if mostrar_heterogeneidad:
        # Heterogeneidad: 8×8 cm centrada en (0, 5) cm
        rect = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='cyan', 
                        facecolor='none', linestyle='--', 
                        label='Región de hueso')
        ax.add_patch(rect)
    
    # Configurar axes
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_title(f'{titulo}\nDeposición de Energía (log₁₀ MeV)', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('log₁₀(Energía Depositada) [MeV]', rotation=270, labelpad=20)
    
    # Agregar estadísticas como texto
    energia_total = np.sum(mapa)
    energia_max = np.max(mapa)
    n_voxels = np.sum(mapa > 0)
    
    stats_text = f'Total: {energia_total:.2e} MeV\nMáx: {energia_max:.2e} MeV\nVoxels: {n_voxels}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  ✓ Guardado: {filename}")
    plt.close()

def plot_diferencia(mapa_agua, mapa_hueso, x_centers, y_centers):
    """Crear plot de la diferencia entre mapas"""
    print("🔍 Calculando diferencias...")
    
    # Calcular diferencia relativa (hueso - agua) / agua
    diferencia_abs = mapa_hueso - mapa_agua
    
    # Para diferencia relativa, evitar división por cero
    diferencia_rel = np.zeros_like(mapa_agua)
    mask = mapa_agua > 0
    diferencia_rel[mask] = (diferencia_abs[mask] / mapa_agua[mask]) * 100
    
    # Crear figura con 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Diferencia absoluta
    ax1 = axes[0]
    im1 = ax1.imshow(diferencia_abs.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal')
    ax1.set_title('Diferencia Absoluta\n(Hueso - Agua)')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.plot(0, 0, 'k*', markersize=10, label='Fuente')
    
    # Marcar región de heterogeneidad
    rect1 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--', label='Región hueso')
    ax1.add_patch(rect1)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('ΔE [MeV]', rotation=270, labelpad=15)
    
    # 2. Diferencia relativa
    ax2 = axes[1]
    # Aplicar límites para mejor visualización
    diff_plot = np.copy(diferencia_rel)
    diff_plot[~mask] = np.nan  # Ocultar regiones sin datos
    
    im2 = ax2.imshow(diff_plot.T, origin='lower',
                     extent=[x_centers[0], x_centers[-1], y_centers[0], y_centers[-1]],
                     cmap='RdBu_r', aspect='equal', vmin=-10, vmax=10)
    ax2.set_title('Diferencia Relativa\n[(Hueso-Agua)/Agua × 100%]')
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.plot(0, 0, 'k*', markersize=10, label='Fuente')
    
    rect2 = Rectangle((-4, 1), 8, 8, linewidth=2, edgecolor='black', 
                     facecolor='none', linestyle='--', label='Región hueso')
    ax2.add_patch(rect2)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Diferencia [%]', rotation=270, labelpad=15)
    
    # 3. Histograma de diferencias
    ax3 = axes[2]
    
    # Solo datos válidos (donde hay energía en ambos casos)
    mask_valido = (mapa_agua > 0) & (mapa_hueso > 0)
    diff_validas = diferencia_rel[mask_valido]
    
    ax3.hist(diff_validas, bins=50, alpha=0.7, edgecolor='black', density=True)
    ax3.axvline(0, color='red', linestyle='--', label='Sin diferencia')
    ax3.axvline(np.mean(diff_validas), color='blue', linestyle='-', 
                label=f'Media: {np.mean(diff_validas):.2f}%')
    ax3.set_xlabel('Diferencia Relativa [%]')
    ax3.set_ylabel('Densidad de Probabilidad')
    ax3.set_title('Distribución de Diferencias')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('diferencias_detalladas_agua_vs_hueso.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: diferencias_detalladas_agua_vs_hueso.png")
    plt.close()
    
    # Estadísticas de diferencias
    print("\n📊 ESTADÍSTICAS DE DIFERENCIAS:")
    print(f"  Diferencia absoluta promedio: {np.mean(diferencia_abs[mask]):.2e} MeV")
    print(f"  Diferencia relativa promedio: {np.mean(diff_validas):.2f}%")
    print(f"  Desviación estándar relativa: {np.std(diff_validas):.2f}%")
    print(f"  Rango de diferencias: {np.min(diff_validas):.2f}% a {np.max(diff_validas):.2f}%")
    
    return diferencia_abs, diferencia_rel

def analisis_perfiles(mapa_agua, mapa_hueso, x_centers, y_centers):
    """Crear perfiles lineales para análisis detallado"""
    print("📈 Creando perfiles lineales...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Encontrar índices centrales
    idx_centro_x = len(x_centers) // 2
    idx_centro_y = len(y_centers) // 2
    
    # 1. Perfil horizontal (Y=0)
    ax1 = axes[0, 0]
    perfil_agua_x = mapa_agua[:, idx_centro_y]
    perfil_hueso_x = mapa_hueso[:, idx_centro_y]
    
    ax1.plot(x_centers, perfil_agua_x, 'b-', linewidth=2, label='Agua homogénea')
    ax1.plot(x_centers, perfil_hueso_x, 'r-', linewidth=2, label='Heterogeneidad hueso')
    ax1.axvline(0, color='black', linestyle='--', alpha=0.5, label='Fuente')
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Energía Depositada (MeV)')
    ax1.set_title('Perfil Horizontal (Y = 0 cm)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-9, 9)
    
    # 2. Perfil vertical (X=0)
    ax2 = axes[0, 1]
    perfil_agua_y = mapa_agua[idx_centro_x, :]
    perfil_hueso_y = mapa_hueso[idx_centro_x, :]
    
    ax2.plot(y_centers, perfil_agua_y, 'b-', linewidth=2, label='Agua homogénea')
    ax2.plot(y_centers, perfil_hueso_y, 'r-', linewidth=2, label='Heterogeneidad hueso')
    ax2.axvline(0, color='black', linestyle='--', alpha=0.5, label='Fuente')
    ax2.axvspan(1, 9, alpha=0.2, color='orange', label='Región hueso')
    ax2.set_xlabel('Y (cm)')
    ax2.set_ylabel('Energía Depositada (MeV)')
    ax2.set_title('Perfil Vertical (X = 0 cm)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-9, 9)
    
    # 3. Diferencia en perfil horizontal
    ax3 = axes[1, 0]
    diff_x = ((perfil_hueso_x - perfil_agua_x) / np.maximum(perfil_agua_x, 1e-10)) * 100
    ax3.plot(x_centers, diff_x, 'g-', linewidth=2)
    ax3.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax3.axvline(0, color='black', linestyle='--', alpha=0.5, label='Fuente')
    ax3.set_xlabel('X (cm)')
    ax3.set_ylabel('Diferencia Relativa (%)')
    ax3.set_title('Diferencia Horizontal: (Hueso-Agua)/Agua × 100%')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(-9, 9)
    
    # 4. Diferencia en perfil vertical
    ax4 = axes[1, 1]
    diff_y = ((perfil_hueso_y - perfil_agua_y) / np.maximum(perfil_agua_y, 1e-10)) * 100
    ax4.plot(y_centers, diff_y, 'g-', linewidth=2)
    ax4.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax4.axvline(0, color='black', linestyle='--', alpha=0.5, label='Fuente')
    ax4.axvspan(1, 9, alpha=0.2, color='orange', label='Región hueso')
    ax4.set_xlabel('Y (cm)')
    ax4.set_ylabel('Diferencia Relativa (%)')
    ax4.set_title('Diferencia Vertical: (Hueso-Agua)/Agua × 100%')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(-9, 9)
    
    plt.tight_layout()
    plt.savefig('perfiles_detallados_agua_vs_hueso.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: perfiles_detallados_agua_vs_hueso.png")
    plt.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("ANÁLISIS DETALLADO DE MAPAS DE DEPOSICIÓN DE ENERGÍA")
    print("Comparación: Agua Homogénea vs Heterogeneidad Hueso")
    print("=" * 60)
    
    # Cargar datos
    datos_agua = cargar_datos('EnergyDeposition_REF_Water_Homogeneous.out')
    datos_hueso = cargar_datos('EnergyDeposition_REF_Bone_Heterogeneous.out')
    
    print("\n" + "=" * 60)
    print("CREANDO MAPAS 2D")
    print("=" * 60)
    
    # Crear mapas 2D
    mapa_agua, x_centers, y_centers = crear_mapa_2d(datos_agua, "Agua Homogénea")
    mapa_hueso, _, _ = crear_mapa_2d(datos_hueso, "Heterogeneidad Hueso")
    
    print("\n" + "=" * 60)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 60)
    
    # Crear plots individuales
    plot_mapa_individual(mapa_agua, x_centers, y_centers, 
                        "Agua Homogénea - Referencia", 
                        "mapa_agua_homogenea_detallado.png")
    
    plot_mapa_individual(mapa_hueso, x_centers, y_centers, 
                        "Heterogeneidad de Hueso Cortical", 
                        "mapa_hueso_heterogeneo_detallado.png", 
                        mostrar_heterogeneidad=True)
    
    # Crear análisis de diferencias
    plot_diferencia(mapa_agua, mapa_hueso, x_centers, y_centers)
    
    # Crear perfiles lineales
    analisis_perfiles(mapa_agua, mapa_hueso, x_centers, y_centers)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("📁 Archivos generados:")
    print("  • mapa_agua_homogenea_detallado.png")
    print("  • mapa_hueso_heterogeneo_detallado.png") 
    print("  • diferencias_detalladas_agua_vs_hueso.png")
    print("  • perfiles_detallados_agua_vs_hueso.png")
    print("=" * 60)

if __name__ == "__main__":
    main()

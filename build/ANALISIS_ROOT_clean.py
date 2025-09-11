#!/usr/bin/env python3
"""
ANÁLISIS DE DATOS ROOT PARA BRAQUITERAPIA
========================================
Script optimizado para leer y analizar histogramas ROOT de Geant4
con escala logarítmica
"""

import uproot
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Circle
import numpy as np

# Configuración de alta calidad
plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 12

def load_histogram_data(filepath):
    """
    Carga un histograma 2D desde un archivo ROOT de Geant4
    """
    print(f"📂 Cargando: {filepath}")
    
    with uproot.open(filepath) as file:
        # Obtener el primer histograma disponible
        hist_name = list(file.keys())[0]
        print(f"  ✓ Histograma: {hist_name}")
        
        hist = file[hist_name]
        values = hist.values()
        x_edges = hist.axes[0].edges()
        y_edges = hist.axes[1].edges()
        
        print(f"  ✓ Dimensiones: {values.shape}")
        print(f"  ✓ Energía total: {np.sum(values):.2e}")
        
        return values, x_edges, y_edges

def create_comparative_map(archivo_agua, archivo_hueso):
    """
    Crea mapas comparativos entre agua y hueso con escala logarítmica
    """
    print("🔬 ANÁLISIS COMPARATIVO DE BRAQUITERAPIA")
    print("="*50)
    
    # Cargar datos
    values_agua, x_edges, y_edges = load_histogram_data(archivo_agua)
    values_hueso, _, _ = load_histogram_data(archivo_hueso)
    
    # Configurar límites espaciales
    x_min, x_max = x_edges[0], x_edges[-1]
    y_min, y_max = y_edges[0], y_edges[-1]
    
    # Crear figura con 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # Configurar normalización logarítmica
    vmax = max(np.max(values_agua), np.max(values_hueso))
    vmin = max(1e-6, vmax * 1e-6)  # Evitar valores cero
    norm_log = colors.LogNorm(vmin=vmin, vmax=vmax)
    
    # 1. Mapa de Agua (Homogéneo)
    im1 = axes[0].imshow(values_agua.T, origin='lower', cmap='viridis', 
                        norm=norm_log, extent=[x_min, x_max, y_min, y_max],
                        aspect='equal')
    axes[0].set_title('Phantom Homogéneo\n(Solo Agua)', fontweight='bold')
    axes[0].set_xlabel('X (mm)')
    axes[0].set_ylabel('Y (mm)')
    axes[0].grid(True, alpha=0.3)
    
    # Añadir círculo del phantom
    circle1 = Circle((0, 0), 90, fill=False, color='white', linewidth=2, linestyle='--')
    axes[0].add_patch(circle1)
    
    cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8)
    cbar1.set_label('Deposición de Energía\n(escala log)', fontsize=10)
    
    # 2. Mapa de Hueso (Heterogéneo)
    im2 = axes[1].imshow(values_hueso.T, origin='lower', cmap='viridis',
                        norm=norm_log, extent=[x_min, x_max, y_min, y_max],
                        aspect='equal')
    axes[1].set_title('Phantom Heterogéneo\n(Agua + Hueso)', fontweight='bold')
    axes[1].set_xlabel('X (mm)')
    axes[1].set_ylabel('Y (mm)')
    axes[1].grid(True, alpha=0.3)
    
    circle2 = Circle((0, 0), 90, fill=False, color='white', linewidth=2, linestyle='--')
    axes[1].add_patch(circle2)
    
    cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8)
    cbar2.set_label('Deposición de Energía\n(escala log)', fontsize=10)
    
    # 3. Mapa de Diferencia (Agua - Hueso)
    diferencia = values_agua - values_hueso
    
    # Normalización simétrica para diferencias
    vmax_diff = np.max(np.abs(diferencia))
    norm_diff = colors.Normalize(vmin=-vmax_diff, vmax=vmax_diff)
    
    im3 = axes[2].imshow(diferencia.T, origin='lower', cmap='RdBu_r',
                        norm=norm_diff, extent=[x_min, x_max, y_min, y_max],
                        aspect='equal')
    axes[2].set_title('Diferencia\n(Agua - Hueso)', fontweight='bold')
    axes[2].set_xlabel('X (mm)')
    axes[2].set_ylabel('Y (mm)')
    axes[2].grid(True, alpha=0.3)
    
    circle3 = Circle((0, 0), 90, fill=False, color='black', linewidth=2, linestyle='--')
    axes[2].add_patch(circle3)
    
    cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8)
    cbar3.set_label('Diferencia de Energía', fontsize=10)
    
    plt.tight_layout()
    
    # Guardar figura
    filename = 'MAPAS_ROOT_LOGARITMICOS_AGUA_vs_HUESO.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"💾 Mapas guardados como: {filename}")
    
    plt.show()
    
    return values_agua, values_hueso, diferencia

def print_quantitative_analysis(values_agua, values_hueso, diferencia):
    """
    Análisis cuantitativo de las diferencias
    """
    print("\n📊 ANÁLISIS CUANTITATIVO:")
    print("="*40)
    
    energia_agua = np.sum(values_agua)
    energia_hueso = np.sum(values_hueso)
    diferencia_total = energia_agua - energia_hueso
    
    print(f"💧 Energía total (Agua):     {energia_agua:.2e}")
    print(f"🦴 Energía total (Hueso):    {energia_hueso:.2e}")
    print(f"📈 Diferencia absoluta:      {diferencia_total:.2e}")
    print(f"📊 Diferencia relativa:      {(diferencia_total/energia_agua)*100:.2f}%")
    
    print(f"\n🔍 ESTADÍSTICAS DE DIFERENCIA:")
    print(f"   • Máxima:     {np.max(diferencia):.2e}")
    print(f"   • Mínima:     {np.min(diferencia):.2e}")
    print(f"   • Promedio:   {np.mean(diferencia):.2e}")
    print(f"   • Desv. std:  {np.std(diferencia):.2e}")

def analyze_single_file(filepath):
    """
    Analiza un solo archivo ROOT con escala logarítmica
    """
    print("🔬 ANÁLISIS DE ARCHIVO ROOT INDIVIDUAL")
    print("="*40)
    
    # Cargar datos
    values, x_edges, y_edges = load_histogram_data(filepath)
    
    # Configurar límites espaciales
    x_min, x_max = x_edges[0], x_edges[-1]
    y_min, y_max = y_edges[0], y_edges[-1]
    
    # Crear figura
    plt.figure(figsize=(10, 8))
    
    # Configurar normalización logarítmica
    vmax = np.max(values)
    vmin = max(1e-6, vmax * 1e-6)
    norm_log = colors.LogNorm(vmin=vmin, vmax=vmax)
    
    # Crear mapa
    im = plt.imshow(values.T, origin='lower', cmap='viridis',
                   norm=norm_log, extent=[x_min, x_max, y_min, y_max],
                   aspect='equal')
    
    plt.title('Mapa de Deposición de Energía\n(Escala Logarítmica)', fontweight='bold')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    plt.grid(True, alpha=0.3)
    
    # Añadir círculo del phantom
    circle = Circle((0, 0), 90, fill=False, color='white', linewidth=2, linestyle='--')
    plt.gca().add_patch(circle)
    
    cbar = plt.colorbar(im, shrink=0.8)
    cbar.set_label('Deposición de Energía (escala log)', fontsize=12)
    
    # Guardar figura
    filename = f'MAPA_ROOT_LOGARITMICO_{filepath.replace(".root", "")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"💾 Mapa guardado como: {filename}")
    
    plt.show()
    
    # Estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Energía total:  {np.sum(values):.2e}")
    print(f"   • Valor máximo:   {np.max(values):.2e}")
    print(f"   • Valor mínimo:   {np.min(values):.2e}")
    print(f"   • Promedio:       {np.mean(values):.2e}")

# Script principal
def main():
    # Para análisis de un solo archivo
    archivo_unico = "brachytherapy.root"
    
    try:
        # Analizar archivo único
        analyze_single_file(archivo_unico)
        
        print("\n✅ ¡Análisis completado exitosamente!")
        print("💡 Para comparar dos archivos, modifica las rutas en main()")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Verificar que el archivo ROOT existe y es válido")

if __name__ == "__main__":
    main()

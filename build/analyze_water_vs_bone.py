#!/usr/bin/env python3
"""
Análisis comparativo de mapas de dosis 2D: Agua vs Hueso
=========================================================

Visualiza y compara la deposición de energía entre:
- Phantom homogéneo (agua)
- Phantom heterogéneo (hueso)

Autor: Análisis Braquiterapia ROOT
Fecha: 2025-09-10
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import sys
import os

def load_dose_map(filename):
    """Carga un mapa de dosis desde archivo ROOT"""
    try:
        print(f"Cargando archivo: {filename}")
        file = uproot.open(filename)
        
        # Listar contenido del archivo para debug
        print(f"Contenido del archivo: {list(file.keys())}")
        
        # Buscar el histograma 2D (típicamente h20)
        hist_key = None
        for key in file.keys():
            if 'h2' in key.lower() or '2d' in key.lower():
                hist_key = key
                break
        
        if not hist_key:
            # Probar con el nombre estándar
            hist_key = 'h20'
        
        print(f"Usando histograma: {hist_key}")
        hist = file[hist_key]
        
        # Extraer datos y ejes
        data = hist.values()
        x_edges = hist.axis(0).edges()
        y_edges = hist.axis(1).edges()
        
        # Convertir a centímetros si es necesario
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2
        
        print(f"Dimensiones del mapa: {data.shape}")
        print(f"Rango X: {x_edges[0]:.2f} a {x_edges[-1]:.2f}")
        print(f"Rango Y: {y_edges[0]:.2f} a {y_edges[-1]:.2f}")
        print(f"Deposición total: {np.sum(data):.2e} keV")
        print(f"Deposición máxima: {np.max(data):.2e} keV")
        
        return data, x_edges, y_edges, x_centers, y_centers
        
    except Exception as e:
        print(f"Error cargando {filename}: {e}")
        return None, None, None, None, None

def plot_comparison(water_data, bone_data, x_edges, y_edges, water_file, bone_file):
    """Crea visualización comparativa de ambos mapas"""
    
    # Configurar figura con 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Comparación de Mapas de Dosis: Agua vs Hueso', fontsize=16, fontweight='bold')
    
    # Encontrar escala común para comparación
    vmin = min(np.min(water_data[water_data > 0]), np.min(bone_data[bone_data > 0]))
    vmax = max(np.max(water_data), np.max(bone_data))
    
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    
    # Subplot 1: Agua homogénea
    im1 = axes[0].imshow(water_data.T, origin='lower', extent=extent, 
                        norm=LogNorm(vmin=vmin, vmax=vmax), cmap='hot')
    axes[0].set_title('Phantom Homogéneo\n(Agua)', fontweight='bold')
    axes[0].set_xlabel('X (cm)')
    axes[0].set_ylabel('Y (cm)')
    axes[0].grid(True, alpha=0.3)
    
    # Subplot 2: Hueso heterogéneo
    im2 = axes[1].imshow(bone_data.T, origin='lower', extent=extent,
                        norm=LogNorm(vmin=vmin, vmax=vmax), cmap='hot')
    axes[1].set_title('Phantom Heterogéneo\n(Hueso)', fontweight='bold')
    axes[1].set_xlabel('X (cm)')
    axes[1].set_ylabel('Y (cm)')
    axes[1].grid(True, alpha=0.3)
    
    # Subplot 3: Diferencia (Agua - Hueso)
    diff_data = water_data - bone_data
    
    # Usar escala simétrica para diferencias
    diff_max = np.max(np.abs(diff_data))
    im3 = axes[2].imshow(diff_data.T, origin='lower', extent=extent,
                        vmin=-diff_max, vmax=diff_max, cmap='RdBu_r')
    axes[2].set_title('Diferencia\n(Agua - Hueso)', fontweight='bold')
    axes[2].set_xlabel('X (cm)')
    axes[2].set_ylabel('Y (cm)')
    axes[2].grid(True, alpha=0.3)
    
    # Añadir colorbars
    plt.colorbar(im1, ax=axes[0], label='Deposición (keV)')
    plt.colorbar(im2, ax=axes[1], label='Deposición (keV)')
    plt.colorbar(im3, ax=axes[2], label='Diferencia (keV)')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    output_file = 'comparison_water_vs_bone_ROOT.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nFigura guardada como: {output_file}")
    
    return fig

def calculate_statistics(water_data, bone_data):
    """Calcula estadísticas comparativas"""
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS COMPARATIVAS")
    print("="*60)
    
    # Deposición total
    water_total = np.sum(water_data)
    bone_total = np.sum(bone_data)
    diff_total = water_total - bone_total
    diff_percent = (diff_total / water_total) * 100
    
    print(f"Deposición total:")
    print(f"  Agua:       {water_total:.2e} keV")
    print(f"  Hueso:      {bone_total:.2e} keV")
    print(f"  Diferencia: {diff_total:.2e} keV ({diff_percent:+.2f}%)")
    
    # Deposición máxima
    water_max = np.max(water_data)
    bone_max = np.max(bone_data)
    diff_max = water_max - bone_max
    diff_max_percent = (diff_max / water_max) * 100
    
    print(f"\nDeposición máxima:")
    print(f"  Agua:       {water_max:.2e} keV")
    print(f"  Hueso:      {bone_max:.2e} keV")
    print(f"  Diferencia: {diff_max:.2e} keV ({diff_max_percent:+.2f}%)")
    
    # Estadísticas de diferencias
    diff_data = water_data - bone_data
    diff_mean = np.mean(diff_data)
    diff_std = np.std(diff_data)
    diff_rms = np.sqrt(np.mean(diff_data**2))
    
    print(f"\nEstadísticas de diferencias:")
    print(f"  Media:      {diff_mean:.2e} keV")
    print(f"  Desv. Est.: {diff_std:.2e} keV")
    print(f"  RMS:        {diff_rms:.2e} keV")
    
    return {
        'water_total': water_total,
        'bone_total': bone_total,
        'diff_percent': diff_percent,
        'water_max': water_max,
        'bone_max': bone_max,
        'diff_max_percent': diff_max_percent
    }

def main():
    """Función principal"""
    
    print("="*60)
    print("ANÁLISIS COMPARATIVO: AGUA vs HUESO")
    print("="*60)
    
    # Definir archivos (los más recientes)
    water_file = "20250910_074137_585_eDep.root"
    bone_file = "20250910_074851_813_eDep.root"
    
    # Verificar que existan los archivos
    if not os.path.exists(water_file):
        print(f"Error: No se encuentra {water_file}")
        return
    
    if not os.path.exists(bone_file):
        print(f"Error: No se encuentra {bone_file}")
        return
    
    # Cargar datos
    print("\n1. Cargando datos...")
    water_data, x_edges_w, y_edges_w, x_centers_w, y_centers_w = load_dose_map(water_file)
    bone_data, x_edges_b, y_edges_b, x_centers_b, y_centers_b = load_dose_map(bone_file)
    
    if water_data is None or bone_data is None:
        print("Error: No se pudieron cargar los datos")
        return
    
    # Verificar compatibilidad de dimensiones
    if water_data.shape != bone_data.shape:
        print(f"Error: Dimensiones incompatibles")
        print(f"Agua: {water_data.shape}, Hueso: {bone_data.shape}")
        return
    
    print("\n2. Calculando estadísticas...")
    stats = calculate_statistics(water_data, bone_data)
    
    print("\n3. Generando visualización...")
    fig = plot_comparison(water_data, bone_data, x_edges_w, y_edges_w, water_file, bone_file)
    
    print("\n4. ¡Análisis completado!")
    print(f"Archivos analizados:")
    print(f"  - Agua: {water_file}")
    print(f"  - Hueso: {bone_file}")
    
    # Mostrar gráfico
    plt.show()

if __name__ == "__main__":
    main()

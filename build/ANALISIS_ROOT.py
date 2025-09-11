#!/usr/bin/env python3
"""
ANÁLISIS DE DATOS ROOT PARA BRAQUITERAPIA
========================================
Script optimizado para leer y analizar histogramas ROOT de Geant4
"""

import uproot
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Circle
import numpy as np
import pandas as pd

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
    cbar1.set_label('Deposición de Energía (escala log)', fontsize=10)
    
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
    cbar2.set_label('Deposición de Energía (escala log)', fontsize=10)
    
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

# Script principal
def main():
    # Archivos de datos
    archivo_agua = "brachytherapy.root"  # Cambiar por archivo de agua
    archivo_hueso = "brachytherapy.root" # Cambiar por archivo de hueso
    
    try:
        # Crear mapas comparativos
        values_agua, values_hueso, diferencia = create_comparative_map(archivo_agua, archivo_hueso)
        
        # Análisis cuantitativo
        print_quantitative_analysis(values_agua, values_hueso, diferencia)
        
        print("\n✅ ¡Análisis completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Verificar que los archivos ROOT existen y son válidos")

if __name__ == "__main__":
    main()
                
                # Crear centros de bins
                x_centers = (x_edges[:-1] + x_edges[1:]) / 2
                y_centers = (y_edges[:-1] + y_edges[1:]) / 2
                
                # Crear meshgrid para coordenadas
                X, Y = np.meshgrid(x_centers, y_centers, indexing='ij')
                
                # Convertir a DataFrame para compatibilidad
                data_list = []
                for i in range(len(x_centers)):
                    for j in range(len(y_centers)):
                        if values[i, j] > 0:  # Solo incluir valores positivos
                            data_list.append({
                                'x': X[i, j],
                                'y': Y[i, j], 
                                'z': 0.0,  # Asumiendo plano Z=0
                                'edep': values[i, j]
                            })
                
                data = pd.DataFrame(data_list)
                
                print(f"  ✓ {len(data):,} puntos con energía > 0")
                print(f"  ✓ Energía total: {data['edep'].sum():.2e}")
                print(f"  ✓ Rango X: [{data['x'].min():.1f}, {data['x'].max():.1f}]")
                print(f"  ✓ Rango Y: [{data['y'].min():.1f}, {data['y'].max():.1f}]")
                
                return data, values, x_centers, y_centers
                
            else:
                print(f"  ❌ No se encontraron datos válidos en el archivo")
                return None, None, None, None
                
        except Exception as e:
            print(f"  ❌ Error leyendo archivo ROOT: {e}")
            print(f"  💡 Intentando método alternativo...")
            return self.load_ascii_fallback(filepath)
    
    def load_ascii_fallback(self, filepath):
        """
        Método de respaldo para cargar archivos ASCII si ROOT falla
        """
        ascii_file = filepath.replace('.root', '.out')
        print(f"  🔄 Intentando cargar archivo ASCII: {ascii_file}")
        
        try:
            data = pd.read_csv(ascii_file, sep=r'\s+', comment='#', header=None)
            data.columns = ['x', 'y', 'z', 'edep']
            data = data[data['edep'] > 0].copy()
            
            print(f"  ✓ Archivo ASCII cargado exitosamente")
            print(f"  ✓ {len(data):,} eventos con energía > 0")
            
            return data, None, None, None
            
        except Exception as e:
            print(f"  ❌ Error con método de respaldo: {e}")
            return None, None, None, None
    
    def load_both_datasets(self):
        """
        Carga ambos conjuntos de datos ROOT
        """
        print("="*70)
        print("🔬 ANÁLISIS COMPARATIVO DE BRAQUITERAPIA - DATOS ROOT")
        print("   Phantom Homogéneo (Agua) vs Heterogéneo (Hueso)")
        print("="*70)
        
        # Cargar datos de agua
        self.data_agua, self.values_agua, self.x_agua, self.y_agua = self.load_root_data(self.archivo_agua)
        
        # Cargar datos de hueso
        self.data_hueso, self.values_hueso, self.x_hueso, self.y_hueso = self.load_root_data(self.archivo_hueso)
        
        if self.data_agua is None or self.data_hueso is None:
            print("❌ No se pudieron cargar los datos ROOT necesarios")
            return False
        
        print(f"\n📊 RESUMEN:")
        print(f"   • Agua:  {len(self.data_agua):,} eventos")
        print(f"   • Hueso: {len(self.data_hueso):,} eventos")
        return True
    
    def create_comparative_maps_from_root(self):
        """
        Crear mapas comparativos usando datos ROOT directamente
        """
        print("\n🗺️  Creando mapas 2D desde datos ROOT...")
        
        # Si tenemos valores de histograma directo, usarlos
        if self.values_agua is not None and self.values_hueso is not None:
            mapa_agua = self.values_agua
            mapa_hueso = self.values_hueso
            x_centers = self.x_agua
            y_centers = self.y_agua
            
        else:
            # Crear mapas a partir de datos puntuales
            limite_cm = 9.0
            bins = 180
            
            mapa_agua, x_centers, y_centers = self.crear_mapa_2d(
                self.data_agua, "Phantom Homogéneo (Agua)", limite_cm, bins
            )
            mapa_hueso, _, _ = self.crear_mapa_2d(
                self.data_hueso, "Phantom Heterogéneo (Hueso)", limite_cm, bins
            )
        
        return self.plot_comparative_maps(mapa_agua, mapa_hueso, x_centers, y_centers)
    
    def crear_mapa_2d(self, data, titulo, limite_cm=9.0, bins=180):
        """
        Crea un mapa 2D de deposición de energía desde DataFrame
        """
        # Crear grid para el mapa 2D
        x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
        y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
        
        # Crear histograma 2D ponderado por energía
        mapa, x_edges, y_edges = np.histogram2d(
            data['x'], data['y'], 
            bins=[x_edges, y_edges], 
            weights=data['edep']
        )
        
        # Centros de los bins
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2
        
        return mapa.T, x_centers, y_centers
    
    def plot_comparative_maps(self, mapa_agua, mapa_hueso, x_centers, y_centers):
        """
        Plotear mapas comparativos
        """
        # Determinar límites espaciales
        if len(x_centers) > 1:
            limite_cm = max(abs(x_centers[0]), abs(x_centers[-1]))
        else:
            limite_cm = 9.0
        
        # Crear figura con 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(24, 8))
        
        # Configurar normalización
        vmax = max(np.max(mapa_agua), np.max(mapa_hueso))
        vmin = 1e-3 * vmax
        norm = colors.LogNorm(vmin=vmin, vmax=vmax)
        
        # Mapa 1: Agua (Homogéneo)
        im1 = axes[0].imshow(mapa_agua, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='viridis', norm=norm)
        axes[0].set_title('Phantom Homogéneo\n(Solo Agua)', fontsize=16, fontweight='bold')
        axes[0].set_xlabel('X (cm)')
        axes[0].set_ylabel('Y (cm)')
        axes[0].grid(True, alpha=0.3)
        
        # Círculo del phantom
        circle1 = Circle((0, 0), limite_cm, fill=False, color='white', linewidth=2, linestyle='--')
        axes[0].add_patch(circle1)
        
        cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8)
        cbar1.set_label('Deposición de Energía', fontsize=12)
        
        # Mapa 2: Hueso (Heterogéneo)
        im2 = axes[1].imshow(mapa_hueso, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='viridis', norm=norm)
        axes[1].set_title('Phantom Heterogéneo\n(Agua + Hueso)', fontsize=16, fontweight='bold')
        axes[1].set_xlabel('X (cm)')
        axes[1].set_ylabel('Y (cm)')
        axes[1].grid(True, alpha=0.3)
        
        circle2 = Circle((0, 0), limite_cm, fill=False, color='white', linewidth=2, linestyle='--')
        axes[1].add_patch(circle2)
        
        cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8)
        cbar2.set_label('Deposición de Energía', fontsize=12)
        
        # Mapa 3: Diferencia
        diferencia = mapa_agua - mapa_hueso
        vmax_diff = np.max(np.abs(diferencia))
        norm_diff = colors.Normalize(vmin=-vmax_diff, vmax=vmax_diff)
        
        im3 = axes[2].imshow(diferencia, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='RdBu_r', norm=norm_diff)
        axes[2].set_title('Diferencia\n(Agua - Hueso)', fontsize=16, fontweight='bold')
        axes[2].set_xlabel('X (cm)')
        axes[2].set_ylabel('Y (cm)')
        axes[2].grid(True, alpha=0.3)
        
        circle3 = Circle((0, 0), limite_cm, fill=False, color='black', linewidth=2, linestyle='--')
        axes[2].add_patch(circle3)
        
        cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8)
        cbar3.set_label('Diferencia de Energía', fontsize=12)
        
        plt.tight_layout()
        
        # Guardar figura
        filename = 'MAPAS_2D_ROOT_COMPARACION_AGUA_vs_HUESO.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Mapa ROOT guardado como: {filename}")
        
        plt.show()
        
        return mapa_agua, mapa_hueso, diferencia
    
    def analisis_cuantitativo_root(self, mapa_agua, mapa_hueso, diferencia):
        """
        Análisis cuantitativo específico para datos ROOT
        """
        print("\n📊 ANÁLISIS CUANTITATIVO DE DATOS ROOT:")
        print("="*50)
        
        energia_total_agua = np.sum(mapa_agua)
        energia_total_hueso = np.sum(mapa_hueso)
        diferencia_total = energia_total_agua - energia_total_hueso
        
        print(f"💧 Energía total (Agua):     {energia_total_agua:.2e}")
        print(f"🦴 Energía total (Hueso):    {energia_total_hueso:.2e}")
        print(f"📈 Diferencia absoluta:      {diferencia_total:.2e}")
        print(f"📊 Diferencia relativa:      {(diferencia_total/energia_total_agua)*100:.2f}%")
        
        print(f"\n🔍 ESTADÍSTICAS DE LA DIFERENCIA:")
        print(f"   • Diferencia máxima:     {np.max(diferencia):.2e}")
        print(f"   • Diferencia mínima:     {np.min(diferencia):.2e}")
        print(f"   • Diferencia promedio:   {np.mean(diferencia):.2e}")
        print(f"   • Desviación estándar:   {np.std(diferencia):.2e}")
        
        return {
            'energia_agua': energia_total_agua,
            'energia_hueso': energia_total_hueso,
            'diferencia_total': diferencia_total,
            'diferencia_relativa': (diferencia_total/energia_total_agua)*100
        }
    
    def run_root_analysis(self):
        """
        Ejecuta el análisis completo de archivos ROOT
        """
        if self.data_agua is None or self.data_hueso is None:
            print("❌ No se pueden ejecutar los análisis sin datos ROOT")
            return
        
        # Crear mapas y calcular diferencias
        mapa_agua, mapa_hueso, diferencia = self.create_comparative_maps_from_root()
        
        # Análisis cuantitativo
        resultados = self.analisis_cuantitativo_root(mapa_agua, mapa_hueso, diferencia)
        
        print("\n✅ ¡Análisis de datos ROOT completado exitosamente!")
        return resultados

# Script principal
def main():
    # Archivos ROOT (pueden no existir aún)
    archivo_agua_root = "EnergyDeposition_REF_Water_Homogeneous10M.root"
    archivo_hueso_root = "EnergyDeposition_REF_Bone_Heterogeneous10M.root"
    
    # Archivos alternativos
    archivo_agua_alt = "brachytherapy_water.root"
    archivo_hueso_alt = "brachytherapy_bone.root"
    
    # Verificar qué archivos existen
    import os
    
    if os.path.exists(archivo_agua_root) and os.path.exists(archivo_hueso_root):
        archivos = (archivo_agua_root, archivo_hueso_root)
    elif os.path.exists(archivo_agua_alt) and os.path.exists(archivo_hueso_alt):
        archivos = (archivo_agua_alt, archivo_hueso_alt)
    else:
        print("❌ No se encontraron archivos ROOT. Opciones:")
        print("   1. Ejecutar convert_to_root_output.py primero")
        print("   2. Verificar que las simulaciones generen archivos .root")
        print("   3. Revisar nombres de archivos en el código")
        return
    
    try:
        # Crear instancia del analizador ROOT
        analyzer = BrachytherapyROOTAnalyzer(archivos[0], archivos[1])
        
        # Ejecutar análisis
        resultados = analyzer.run_root_analysis()
        
    except Exception as e:
        print(f"❌ Error en el análisis ROOT: {e}")
        print("Verificar instalación de uproot y archivos ROOT")

if __name__ == "__main__":
    main()

import pandas as pd
import uproot  # Para leer archivos ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle, Circle
import warnings
warnings.filterwarnings('ignore')

# Configuración de alta calidad para las figuras
plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 12

class BrachytherapyAnalyzer:
    def __init__(self, archivo_agua, archivo_hueso):
        """
        Inicializa el analizador para comparar phantom homogéneo vs heterogéneo
        """
        self.archivo_agua = archivo_agua
        self.archivo_hueso = archivo_hueso
        self.data_agua = None
        self.data_hueso = None
        self.load_both_datasets()
    
    def load_data(self, filepath):
        """
        Carga los datos de un archivo de Geant4
        """
        print(f"📂 Cargando: {filepath}")
        
        try:
            # Cargar datos (formato: x y z edep)
            data = pd.read_csv(filepath, sep=r'\s+', comment='#', header=None)
            
            # Asignar nombres de columnas según el número de columnas
            if data.shape[1] == 4:
                data.columns = ['x', 'y', 'z', 'edep']
            elif data.shape[1] == 3:
                data.columns = ['x', 'y', 'edep']
                data['z'] = 0  # Añadir columna z con valor 0
            else:
                print(f"⚠️  Formato inesperado: {data.shape[1]} columnas")
                return None
            
            # Filtrar datos con energía positiva
            data = data[data['edep'] > 0].copy()
            
            print(f"  ✓ {len(data):,} eventos con energía > 0")
            print(f"  ✓ Energía total: {data['edep'].sum():.2e} MeV")
            print(f"  ✓ Rango X: [{data['x'].min():.1f}, {data['x'].max():.1f}] mm")
            print(f"  ✓ Rango Y: [{data['y'].min():.1f}, {data['y'].max():.1f}] mm")
            
            return data
            
        except Exception as e:
            print(f"❌ Error al cargar {filepath}: {e}")
            return None
    
    def load_both_datasets(self):
        """
        Carga ambos conjuntos de datos
        """
        print("="*70)
        print("🔬 ANÁLISIS COMPARATIVO DE BRAQUITERAPIA")
        print("   Phantom Homogéneo (Agua) vs Heterogéneo (Hueso)")
        print("="*70)
        
        self.data_agua = self.load_data(self.archivo_agua)
        self.data_hueso = self.load_data(self.archivo_hueso)
        
        if self.data_agua is None or self.data_hueso is None:
            print("❌ No se pudieron cargar los datos necesarios")
            return False
        
        print(f"\n📊 RESUMEN:")
        print(f"   • Agua:  {len(self.data_agua):,} eventos")
        print(f"   • Hueso: {len(self.data_hueso):,} eventos")
        return True
    
    
    def crear_mapa_2d(self, data, titulo, limite_cm=9.0, bins=180):
        """
        Crea un mapa 2D de deposición de energía
        """
        # Convertir coordenadas de mm a cm si es necesario
        if data['x'].max() > 50:  # Probablemente en mm
            x_data = data['x'] / 10.0  # mm -> cm
            y_data = data['y'] / 10.0  # mm -> cm
            print(f"  🔄 Coordenadas convertidas de mm a cm")
        else:
            x_data = data['x']
            y_data = data['y']
        
        # Crear grid para el mapa 2D
        x_edges = np.linspace(-limite_cm, limite_cm, bins+1)
        y_edges = np.linspace(-limite_cm, limite_cm, bins+1)
        
        # Crear histograma 2D ponderado por energía
        mapa, x_edges, y_edges = np.histogram2d(
            x_data, y_data, 
            bins=[x_edges, y_edges], 
            weights=data['edep']
        )
        
        # Centros de los bins para el plot
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2
        
        return mapa.T, x_centers, y_centers  # Transponer para orientación correcta
    
    def plot_mapas_2d(self):
        """
        Crea mapas 2D comparativos de ambos phantoms
        """
        print("\n🗺️  Creando mapas 2D de deposición de energía...")
        
        # Parámetros del mapa
        limite_cm = 9.0
        bins = 180  # 1mm de resolución
        
        # Crear mapas
        mapa_agua, x_centers, y_centers = self.crear_mapa_2d(
            self.data_agua, "Phantom Homogéneo (Agua)", limite_cm, bins
        )
        
        mapa_hueso, _, _ = self.crear_mapa_2d(
            self.data_hueso, "Phantom Heterogéneo (Hueso)", limite_cm, bins
        )
        
        # Crear figura con 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(24, 8))
        
        # Configurar colormap y normalización
        vmax = max(np.max(mapa_agua), np.max(mapa_hueso))
        vmin = 1e-3 * vmax  # Para escala logarítmica
        norm = colors.LogNorm(vmin=vmin, vmax=vmax)
        
        # Mapa 1: Agua (Homogéneo)
        im1 = axes[0].imshow(mapa_agua, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='viridis', norm=norm)
        axes[0].set_title('Phantom Homogéneo\n(Solo Agua)', fontsize=16, fontweight='bold')
        axes[0].set_xlabel('X (cm)')
        axes[0].set_ylabel('Y (cm)')
        axes[0].grid(True, alpha=0.3)
        
        # Añadir círculo para mostrar límites del phantom
        circle1 = Circle((0, 0), limite_cm, fill=False, color='white', linewidth=2, linestyle='--')
        axes[0].add_patch(circle1)
        
        # Colorbar para agua
        cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8)
        cbar1.set_label('Deposición de Energía (MeV)', fontsize=12)
        
        # Mapa 2: Hueso (Heterogéneo)
        im2 = axes[1].imshow(mapa_hueso, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='viridis', norm=norm)
        axes[1].set_title('Phantom Heterogéneo\n(Agua + Hueso)', fontsize=16, fontweight='bold')
        axes[1].set_xlabel('X (cm)')
        axes[1].set_ylabel('Y (cm)')
        axes[1].grid(True, alpha=0.3)
        
        # Añadir círculo para mostrar límites del phantom
        circle2 = Circle((0, 0), limite_cm, fill=False, color='white', linewidth=2, linestyle='--')
        axes[1].add_patch(circle2)
        
        # Colorbar para hueso
        cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8)
        cbar2.set_label('Deposición de Energía (MeV)', fontsize=12)
        
        # Mapa 3: Diferencia (Agua - Hueso)
        diferencia = mapa_agua - mapa_hueso
        
        # Normalización simétrica para diferencias
        vmax_diff = np.max(np.abs(diferencia))
        norm_diff = colors.Normalize(vmin=-vmax_diff, vmax=vmax_diff)
        
        im3 = axes[2].imshow(diferencia, extent=[-limite_cm, limite_cm, -limite_cm, limite_cm],
                           origin='lower', cmap='RdBu_r', norm=norm_diff)
        axes[2].set_title('Diferencia\n(Agua - Hueso)', fontsize=16, fontweight='bold')
        axes[2].set_xlabel('X (cm)')
        axes[2].set_ylabel('Y (cm)')
        axes[2].grid(True, alpha=0.3)
        
        # Añadir círculo para mostrar límites del phantom
        circle3 = Circle((0, 0), limite_cm, fill=False, color='black', linewidth=2, linestyle='--')
        axes[2].add_patch(circle3)
        
        # Colorbar para diferencia
        cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8)
        cbar3.set_label('Diferencia de Energía (MeV)', fontsize=12)
        
        plt.tight_layout()
        
        # Guardar figura
        filename = 'MAPAS_2D_COMPARACION_AGUA_vs_HUESO.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 Mapa guardado como: {filename}")
        
        plt.show()
        
        return mapa_agua, mapa_hueso, diferencia
    
    def analisis_cuantitativo(self, mapa_agua, mapa_hueso, diferencia):
        """
        Análisis cuantitativo de las diferencias
        """
        print("\n📊 ANÁLISIS CUANTITATIVO DE DIFERENCIAS:")
        print("="*50)
        
        # Energías totales
        energia_total_agua = np.sum(mapa_agua)
        energia_total_hueso = np.sum(mapa_hueso)
        diferencia_total = energia_total_agua - energia_total_hueso
        
        print(f"💧 Energía total (Agua):     {energia_total_agua:.2e} MeV")
        print(f"🦴 Energía total (Hueso):    {energia_total_hueso:.2e} MeV")
        print(f"📈 Diferencia absoluta:      {diferencia_total:.2e} MeV")
        print(f"📊 Diferencia relativa:      {(diferencia_total/energia_total_agua)*100:.2f}%")
        
        # Estadísticas de la diferencia
        print(f"\n🔍 ESTADÍSTICAS DE LA DIFERENCIA:")
        print(f"   • Diferencia máxima:     {np.max(diferencia):.2e} MeV")
        print(f"   • Diferencia mínima:     {np.min(diferencia):.2e} MeV")
        print(f"   • Diferencia promedio:   {np.mean(diferencia):.2e} MeV")
        print(f"   • Desviación estándar:   {np.std(diferencia):.2e} MeV")
        
        # Análisis por zonas radiales
        print(f"\n🎯 ANÁLISIS RADIAL:")
        self.analisis_radial(mapa_agua, mapa_hueso, diferencia)
        
        return {
            'energia_agua': energia_total_agua,
            'energia_hueso': energia_total_hueso,
            'diferencia_total': diferencia_total,
            'diferencia_relativa': (diferencia_total/energia_total_agua)*100
        }
    
    def analisis_radial(self, mapa_agua, mapa_hueso, diferencia, limite_cm=9.0):
        """
        Análisis de diferencias por zonas radiales
        """
        bins = mapa_agua.shape[0]
        center = bins // 2
        
        # Crear grid de coordenadas
        y, x = np.mgrid[0:bins, 0:bins]
        y = (y - center) * (2 * limite_cm / bins)
        x = (x - center) * (2 * limite_cm / bins)
        r = np.sqrt(x**2 + y**2)
        
        # Definir zonas radiales
        zonas = [
            (0, 1, "0-1 cm"),
            (1, 3, "1-3 cm"),
            (3, 6, "3-6 cm"),
            (6, 9, "6-9 cm")
        ]
        
        for r_min, r_max, nombre in zonas:
            mask = (r >= r_min) & (r <= r_max)
            
            if np.any(mask):
                energia_agua_zona = np.sum(mapa_agua[mask])
                energia_hueso_zona = np.sum(mapa_hueso[mask])
                diferencia_zona = energia_agua_zona - energia_hueso_zona
                
                if energia_agua_zona > 0:
                    porcentaje = (diferencia_zona / energia_agua_zona) * 100
                    print(f"   • {nombre}: {porcentaje:+6.2f}% de diferencia")
    
    def run_analysis(self):
        """
        Ejecuta el análisis completo
        """
        if self.data_agua is None or self.data_hueso is None:
            print("❌ No se pueden ejecutar los análisis sin datos")
            return
        
        # Crear mapas 2D y calcular diferencias
        mapa_agua, mapa_hueso, diferencia = self.plot_mapas_2d()
        
        # Análisis cuantitativo
        resultados = self.analisis_cuantitativo(mapa_agua, mapa_hueso, diferencia)
        
        print("\n✅ ¡Análisis completado exitosamente!")
        return resultados

# Script principal
def main():
    # Archivos de datos
    archivo_agua = "EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.root"
    archivo_hueso = "EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.root"
    
    try:
        # Crear instancia del analizador
        analyzer = BrachytherapyAnalyzer(archivo_agua, archivo_hueso)
        
        # Ejecutar análisis
        resultados = analyzer.run_analysis()
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        print("Verificar que los archivos existen y tienen el formato correcto")

if __name__ == "__main__":
    main()
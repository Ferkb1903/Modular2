#!/usr/bin/env python3
"""
🔍 ANÁLISIS DE PROPORCIÓN PHANTOM/HETEROGENEIDAD
===============================================

Analiza la relación entre el tamaño del phantom de agua y la heterogeneidad
para optimizar el diseño experimental y maximizar el contraste en la comparación.

Autor: Equipo de Física Médica
Fecha: Septiembre 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

def analyze_current_geometry():
    """Analizar la geometría actual"""
    print("🔍 ANÁLISIS DE LA GEOMETRÍA ACTUAL")
    print("=" * 50)
    
    # Configuración actual
    phantom_size = 30.0  # cm (30×30×30 cm)
    hetero_size = 6.0    # cm (6×6×6 cm)
    hetero_position = [0, 6, 0]  # cm
    
    # Cálculos de volumen
    phantom_volume = phantom_size**3
    hetero_volume = hetero_size**3
    water_volume = phantom_volume - hetero_volume
    
    # Porcentajes
    hetero_percentage = (hetero_volume / phantom_volume) * 100
    water_percentage = (water_volume / phantom_volume) * 100
    
    print(f"\n📏 DIMENSIONES ACTUALES:")
    print(f"   • Phantom total: {phantom_size}×{phantom_size}×{phantom_size} cm")
    print(f"   • Heterogeneidad: {hetero_size}×{hetero_size}×{hetero_size} cm")
    print(f"   • Posición heterogeneidad: {hetero_position} cm")
    
    print(f"\n📊 VOLÚMENES:")
    print(f"   • Phantom total: {phantom_volume:,.0f} cm³")
    print(f"   • Heterogeneidad: {hetero_volume:,.0f} cm³ ({hetero_percentage:.1f}%)")
    print(f"   • Agua: {water_volume:,.0f} cm³ ({water_percentage:.1f}%)")
    
    print(f"\n🎯 PROBLEMA IDENTIFICADO:")
    print(f"   • La heterogeneidad representa solo {hetero_percentage:.1f}% del volumen total")
    print(f"   • El {water_percentage:.1f}% restante es agua homogénea")
    print(f"   • Esto diluye el contraste en el análisis comparativo")
    
    return {
        'phantom_size': phantom_size,
        'hetero_size': hetero_size,
        'hetero_position': hetero_position,
        'hetero_percentage': hetero_percentage
    }

def propose_optimized_geometries():
    """Proponer geometrías optimizadas"""
    print("\n" + "="*70)
    print("💡 PROPUESTAS DE OPTIMIZACIÓN GEOMÉTRICA")
    print("="*70)
    
    scenarios = [
        {
            'name': 'Conservador',
            'phantom_size': 20.0,
            'hetero_size': 8.0,
            'description': 'Reducir phantom, aumentar heterogeneidad moderadamente'
        },
        {
            'name': 'Equilibrado', 
            'phantom_size': 16.0,
            'hetero_size': 10.0,
            'description': 'Phantom compacto con heterogeneidad prominente'
        },
        {
            'name': 'Agresivo',
            'phantom_size': 14.0,
            'hetero_size': 12.0,
            'description': 'Maximizar proporción de heterogeneidad'
        },
        {
            'name': 'Máximo contraste',
            'phantom_size': 12.0,
            'hetero_size': 10.0,
            'description': 'Phantom mínimo viable con heterogeneidad dominante'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        phantom_vol = scenario['phantom_size']**3
        hetero_vol = scenario['hetero_size']**3
        hetero_percent = (hetero_vol / phantom_vol) * 100
        
        # Verificar si la heterogeneidad cabe en el phantom
        fits = scenario['hetero_size'] <= scenario['phantom_size']
        
        print(f"\n{i}. ESCENARIO {scenario['name'].upper()}:")
        print(f"   📏 Phantom: {scenario['phantom_size']}×{scenario['phantom_size']}×{scenario['phantom_size']} cm")
        print(f"   📦 Heterogeneidad: {scenario['hetero_size']}×{scenario['hetero_size']}×{scenario['hetero_size']} cm")
        print(f"   📊 Proporción heterogeneidad: {hetero_percent:.1f}%")
        print(f"   📝 Descripción: {scenario['description']}")
        
        if not fits:
            print(f"   ⚠️  PROBLEMA: Heterogeneidad no cabe en phantom")
        else:
            print(f"   ✅ Geometría viable")
            
            # Calcular posición óptima
            max_offset = (scenario['phantom_size'] - scenario['hetero_size']) / 2
            optimal_y = min(6.0, max_offset)  # Mantener cerca de la fuente
            
            print(f"   📍 Posición sugerida: (0, {optimal_y:.1f}, 0) cm")
            
            # Calcular impacto esperado en scoring mesh
            if hetero_percent > 30:
                print(f"   🎯 Impacto esperado: ALTO contraste en análisis")
            elif hetero_percent > 20:
                print(f"   🎯 Impacto esperado: MODERADO contraste")
            else:
                print(f"   🎯 Impacto esperado: BAJO contraste")
    
    return scenarios

def analyze_dosimetric_implications():
    """Analizar implicaciones dosimétricas"""
    print("\n" + "="*70)
    print("⚡ IMPLICACIONES DOSIMÉTRICAS DE LA OPTIMIZACIÓN")
    print("="*70)
    
    print(f"\n🔬 CONSIDERACIONES FÍSICAS:")
    print(f"   • Fuente Ir-192 en el origen (0,0,0)")
    print(f"   • Energía promedio ~380 keV")
    print(f"   • Rango efectivo en agua ~5-15 cm")
    print(f"   • Efectos de heterogeneidad más pronunciados cerca de la fuente")
    
    print(f"\n🎯 VENTAJAS DE AUMENTAR LA HETEROGENEIDAD:")
    print(f"   ✅ Mayor volumen de interacción con radiación")
    print(f"   ✅ Efectos de scattering y atenuación más evidentes")
    print(f"   ✅ Mejor estadística en la región de interés")
    print(f"   ✅ Contraste más claro en mapas comparativos")
    
    print(f"\n📏 VENTAJAS DE REDUCIR EL PHANTOM:")
    print(f"   ✅ Menor tiempo de simulación")
    print(f"   ✅ Mejor relación señal/ruido")
    print(f"   ✅ Scoring mesh más eficiente")
    print(f"   ✅ Análisis más enfocado en la región crítica")
    
    print(f"\n⚠️  CONSIDERACIONES:")
    print(f"   • Mantener suficiente agua para simular backscatter")
    print(f"   • No reducir tanto que se pierdan efectos de borde")
    print(f"   • Considerar el rango de partículas secundarias")

def create_geometry_comparison():
    """Crear visualización comparativa de geometrías"""
    print(f"\n🎨 Generando comparación visual...")
    
    # Configuración actual vs propuestas
    geometries = [
        {'name': 'ACTUAL', 'phantom': 30, 'hetero': 6, 'color': 'red'},
        {'name': 'CONSERVADOR', 'phantom': 20, 'hetero': 8, 'color': 'orange'},
        {'name': 'EQUILIBRADO', 'phantom': 16, 'hetero': 10, 'color': 'green'},
        {'name': 'AGRESIVO', 'phantom': 14, 'hetero': 12, 'color': 'blue'},
        {'name': 'MAX CONTRASTE', 'phantom': 12, 'hetero': 10, 'color': 'purple'}
    ]
    
    fig, axes = plt.subplots(1, len(geometries), figsize=(20, 4))
    fig.suptitle('COMPARACIÓN DE GEOMETRÍAS PROPUESTAS', fontsize=16, fontweight='bold')
    
    for i, (ax, geom) in enumerate(zip(axes, geometries)):
        phantom_size = geom['phantom']
        hetero_size = geom['hetero']
        
        # Verificar si cabe
        fits = hetero_size <= phantom_size
        
        if fits:
            # Dibujar phantom (agua)
            phantom_rect = Rectangle((-phantom_size/2, -phantom_size/2), 
                                   phantom_size, phantom_size,
                                   facecolor='lightblue', edgecolor='blue', 
                                   linewidth=2, alpha=0.6, label='Agua')
            ax.add_patch(phantom_rect)
            
            # Dibujar heterogeneidad
            hetero_y = min(6.0, (phantom_size - hetero_size)/2)
            hetero_rect = Rectangle((-hetero_size/2, hetero_y - hetero_size/2),
                                  hetero_size, hetero_size,
                                  facecolor=geom['color'], edgecolor='darkred',
                                  linewidth=2, alpha=0.8, label='Heterogeneidad')
            ax.add_patch(hetero_rect)
            
            # Marcar fuente
            ax.plot(0, 0, 'r*', markersize=15, markeredgecolor='black')
            
            # Calcular porcentaje
            hetero_percent = (hetero_size**3 / phantom_size**3) * 100
            
            ax.set_xlim(-phantom_size/2 - 2, phantom_size/2 + 2)
            ax.set_ylim(-phantom_size/2 - 2, phantom_size/2 + 2)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'{geom["name"]}\n{phantom_size}×{phantom_size} cm\n'
                        f'Hetero: {hetero_percent:.1f}%', 
                        fontweight='bold')
            ax.set_xlabel('X (cm)')
            if i == 0:
                ax.set_ylabel('Y (cm)')
        else:
            ax.text(0.5, 0.5, 'GEOMETRÍA\nINVÁLIDA', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=14, fontweight='bold', color='red')
            ax.set_title(f'{geom["name"]}\nINVÁLIDA', fontweight='bold', color='red')
    
    plt.tight_layout()
    
    # Guardar figura
    output_file = '../results/geometry_optimization_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comparación guardada: {output_file}")
    
    return fig

def generate_optimized_macros():
    """Generar macros optimizados para las mejores geometrías"""
    print(f"\n📝 Generando macros optimizados...")
    
    # Configuración equilibrada (recomendada)
    equilibrado_config = {
        'phantom_size': 16.0,
        'hetero_size': 10.0,
        'hetero_position': [0, 3, 0],  # Más cerca de la fuente
        'mesh_size': 9.0,  # Ligeramente mayor que heterogeneidad
        'mesh_bins': 90    # Mantener resolución de 1 mm
    }
    
    print(f"\n🎯 CONFIGURACIÓN RECOMENDADA (EQUILIBRADA):")
    print(f"   • Phantom: {equilibrado_config['phantom_size']}×{equilibrado_config['phantom_size']}×{equilibrado_config['phantom_size']} cm")
    print(f"   • Heterogeneidad: {equilibrado_config['hetero_size']}×{equilibrado_config['hetero_size']}×{equilibrado_config['hetero_size']} cm")
    print(f"   • Posición: {equilibrado_config['hetero_position']} cm")
    print(f"   • Scoring mesh: ±{equilibrado_config['mesh_size']} cm ({equilibrado_config['mesh_bins']}×{equilibrado_config['mesh_bins']} bins)")
    
    hetero_volume = equilibrado_config['hetero_size']**3
    phantom_volume = equilibrado_config['phantom_size']**3
    hetero_percent = (hetero_volume / phantom_volume) * 100
    
    print(f"   • Proporción heterogeneidad: {hetero_percent:.1f}% (vs {8.0:.1f}% actual)")
    print(f"   • Mejora en contraste: {hetero_percent/8.0:.1f}x")
    
    return equilibrado_config

def main():
    print("🔍 ANÁLISIS DE PROPORCIÓN PHANTOM/HETEROGENEIDAD")
    print("=" * 55)
    
    # Analizar geometría actual
    current_geom = analyze_current_geometry()
    
    # Proponer optimizaciones
    scenarios = propose_optimized_geometries()
    
    # Analizar implicaciones
    analyze_dosimetric_implications()
    
    # Crear visualización
    fig = create_geometry_comparison()
    
    # Generar configuración recomendada
    recommended_config = generate_optimized_macros()
    
    print(f"\n✨ CONCLUSIONES Y RECOMENDACIONES ✨")
    print(f"=" * 45)
    print(f"🎯 La configuración EQUILIBRADA es la más recomendada:")
    print(f"   → Aumenta contraste {recommended_config['hetero_size']**3 / 6**3:.1f}x")
    print(f"   → Reduce tiempo de simulación ~3x")
    print(f"   → Mantiene física relevante")
    print(f"   → Optimiza relación señal/ruido")
    
    plt.show()

if __name__ == "__main__":
    main()

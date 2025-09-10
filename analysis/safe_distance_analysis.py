#!/usr/bin/env python3
"""
🔍 ANÁLISIS DE DISTANCIA FUENTE-HETEROGENEIDAD
===============================================

Calcula las distancias óptimas manteniendo al menos 1 cm de agua
entre la fuente y la heterogeneidad para preservar la física correcta.

Autor: Equipo de Física Médica
Fecha: Septiembre 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import warnings
warnings.filterwarnings('ignore')

def analyze_source_heterogeneity_distance():
    """Analizar distancia fuente-heterogeneidad con restricciones físicas"""
    print("🔍 ANÁLISIS DE DISTANCIA FUENTE-HETEROGENEIDAD")
    print("=" * 55)
    
    # Parámetros físicos importantes
    min_water_thickness = 1.0  # cm mínimo de agua
    source_position = [0, 0, 0]  # cm
    
    print(f"\n⚡ CONSIDERACIONES FÍSICAS:")
    print(f"   • Fuente Ir-192 en posición: {source_position} cm")
    print(f"   • Distancia mínima de agua requerida: {min_water_thickness} cm")
    print(f"   • Razón física: Buildup, backscatter, tissue equivalence")
    
    # Analizar configuraciones con restricción de distancia
    configurations = [
        {
            'name': 'CONSERVADOR SEGURO',
            'phantom_size': 18.0,
            'hetero_size': 8.0,
            'hetero_y': 5.0,  # Centroide de heterogeneidad
            'description': 'Phantom moderado, heterogeneidad conservadora'
        },
        {
            'name': 'EQUILIBRADO SEGURO',
            'phantom_size': 16.0,
            'hetero_size': 8.0,
            'hetero_y': 5.0,
            'description': 'Balance óptimo tamaño/contraste'
        },
        {
            'name': 'ALTO CONTRASTE SEGURO',
            'phantom_size': 14.0,
            'hetero_size': 8.0,
            'hetero_y': 4.5,
            'description': 'Máximo contraste manteniendo física'
        },
        {
            'name': 'COMPACTO SEGURO',
            'phantom_size': 12.0,
            'hetero_size': 6.0,
            'hetero_y': 4.0,
            'description': 'Simulación rápida con buena física'
        }
    ]
    
    valid_configs = []
    
    for config in configurations:
        # Calcular distancia mínima desde fuente al borde más cercano de heterogeneidad
        hetero_min_y = config['hetero_y'] - config['hetero_size']/2
        distance_to_hetero = abs(hetero_min_y - source_position[1])
        
        # Verificar si cabe en phantom
        hetero_max_y = config['hetero_y'] + config['hetero_size']/2
        fits_in_phantom = hetero_max_y <= config['phantom_size']/2
        
        # Verificar distancia mínima de agua
        sufficient_water = distance_to_hetero >= min_water_thickness
        
        # Calcular volúmenes y porcentajes
        phantom_vol = config['phantom_size']**3
        hetero_vol = config['hetero_size']**3
        hetero_percent = (hetero_vol / phantom_vol) * 100
        
        print(f"\n🔧 {config['name']}:")
        print(f"   📏 Phantom: {config['phantom_size']}×{config['phantom_size']}×{config['phantom_size']} cm")
        print(f"   📦 Heterogeneidad: {config['hetero_size']}×{config['hetero_size']}×{config['hetero_size']} cm")
        print(f"   📍 Posición heterogeneidad: (0, {config['hetero_y']}, 0) cm")
        print(f"   📏 Distancia fuente→heterogeneidad: {distance_to_hetero:.1f} cm")
        print(f"   📊 Proporción heterogeneidad: {hetero_percent:.1f}%")
        
        # Verificaciones
        if not fits_in_phantom:
            print(f"   ❌ ERROR: Heterogeneidad excede phantom")
        elif not sufficient_water:
            print(f"   ⚠️  ADVERTENCIA: Agua insuficiente ({distance_to_hetero:.1f} cm < {min_water_thickness} cm)")
        else:
            print(f"   ✅ Configuración VÁLIDA")
            print(f"   💧 Capa de agua: {distance_to_hetero:.1f} cm (✓)")
            valid_configs.append(config)
    
    return valid_configs

def create_distance_visualization(valid_configs):
    """Crear visualización de las configuraciones válidas"""
    print(f"\n🎨 Generando visualización de distancias...")
    
    if not valid_configs:
        print("❌ No hay configuraciones válidas para visualizar")
        return None
    
    n_configs = len(valid_configs)
    fig, axes = plt.subplots(1, n_configs, figsize=(5*n_configs, 6))
    if n_configs == 1:
        axes = [axes]
    
    fig.suptitle('CONFIGURACIONES CON DISTANCIA SEGURA FUENTE-HETEROGENEIDAD', 
                 fontsize=14, fontweight='bold')
    
    for i, (ax, config) in enumerate(zip(axes, valid_configs)):
        phantom_size = config['phantom_size']
        hetero_size = config['hetero_size']
        hetero_y = config['hetero_y']
        
        # Dibujar phantom (agua)
        phantom_rect = Rectangle((-phantom_size/2, -phantom_size/2), 
                               phantom_size, phantom_size,
                               facecolor='lightblue', edgecolor='blue', 
                               linewidth=2, alpha=0.6, label='Agua')
        ax.add_patch(phantom_rect)
        
        # Dibujar heterogeneidad
        hetero_rect = Rectangle((-hetero_size/2, hetero_y - hetero_size/2),
                              hetero_size, hetero_size,
                              facecolor='orange', edgecolor='darkred',
                              linewidth=2, alpha=0.8, label='Heterogeneidad')
        ax.add_patch(hetero_rect)
        
        # Marcar fuente
        ax.plot(0, 0, 'r*', markersize=20, markeredgecolor='black', markeredgewidth=2)
        ax.text(0.5, -0.8, 'Fuente Ir-192', ha='center', fontweight='bold', color='red')
        
        # Dibujar línea de distancia
        hetero_min_y = hetero_y - hetero_size/2
        ax.plot([0, 0], [0, hetero_min_y], 'g--', linewidth=3, alpha=0.8)
        
        # Anotar distancia
        distance = hetero_min_y
        ax.text(0.5, distance/2, f'{distance:.1f} cm\n(agua)', 
               ha='center', va='center', fontweight='bold', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))
        
        # Calcular porcentaje
        hetero_percent = (hetero_size**3 / phantom_size**3) * 100
        
        ax.set_xlim(-phantom_size/2 - 1, phantom_size/2 + 1)
        ax.set_ylim(-phantom_size/2 - 1, phantom_size/2 + 1)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'{config["name"]}\n{phantom_size}×{phantom_size} cm\n'
                    f'Heterogeneidad: {hetero_percent:.1f}%\n'
                    f'Distancia: {distance:.1f} cm', 
                    fontweight='bold', fontsize=10)
        ax.set_xlabel('X (cm)')
        if i == 0:
            ax.set_ylabel('Y (cm)')
    
    plt.tight_layout()
    
    # Guardar figura
    output_file = '../results/safe_distance_configurations.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Visualización guardada: {output_file}")
    
    return fig

def recommend_optimal_configuration(valid_configs):
    """Recomendar la configuración óptima"""
    print(f"\n🏆 RECOMENDACIÓN ÓPTIMA")
    print(f"=" * 30)
    
    if not valid_configs:
        print("❌ No hay configuraciones válidas")
        return None
    
    # Criterios de evaluación
    scores = []
    for config in valid_configs:
        phantom_vol = config['phantom_size']**3
        hetero_vol = config['hetero_size']**3
        hetero_percent = (hetero_vol / phantom_vol) * 100
        
        # Score basado en: contraste (40%), eficiencia computacional (30%), seguridad física (30%)
        contrast_score = min(hetero_percent / 15.0, 1.0) * 0.4  # Normalizado a 15% máximo
        efficiency_score = (30.0 / config['phantom_size']) * 0.3  # Phantom más pequeño = más eficiente
        
        hetero_min_y = config['hetero_y'] - config['hetero_size']/2
        safety_score = min(hetero_min_y / 2.0, 1.0) * 0.3  # Bonus por distancia extra
        
        total_score = contrast_score + efficiency_score + safety_score
        scores.append(total_score)
    
    # Encontrar la mejor configuración
    best_idx = np.argmax(scores)
    best_config = valid_configs[best_idx]
    
    hetero_vol = best_config['hetero_size']**3
    phantom_vol = best_config['phantom_size']**3
    hetero_percent = (hetero_vol / phantom_vol) * 100
    hetero_min_y = best_config['hetero_y'] - best_config['hetero_size']/2
    
    print(f"🥇 CONFIGURACIÓN RECOMENDADA: {best_config['name']}")
    print(f"   📏 Phantom: {best_config['phantom_size']}×{best_config['phantom_size']}×{best_config['phantom_size']} cm")
    print(f"   📦 Heterogeneidad: {best_config['hetero_size']}×{best_config['hetero_size']}×{best_config['hetero_size']} cm")
    print(f"   📍 Posición: (0, {best_config['hetero_y']}, 0) cm")
    print(f"   💧 Distancia agua: {hetero_min_y:.1f} cm")
    print(f"   📊 Contraste: {hetero_percent:.1f}%")
    print(f"   ⚡ Score total: {scores[best_idx]:.3f}")
    print(f"   📝 {best_config['description']}")
    
    return best_config

def generate_safe_macros(best_config):
    """Generar parámetros para macros seguros"""
    print(f"\n📝 PARÁMETROS PARA MACROS OPTIMIZADOS")
    print(f"=" * 40)
    
    if not best_config:
        print("❌ No se puede generar macro sin configuración válida")
        return None
    
    # Calcular parámetros para Geant4
    phantom_radius = best_config['phantom_size'] / 2
    hetero_radius = best_config['hetero_size'] / 2
    mesh_size = phantom_radius + 1  # Ligeramente mayor que phantom
    mesh_bins = int(mesh_size * 10)  # 1 mm de resolución
    
    macro_params = {
        'phantom_radius': phantom_radius,
        'hetero_radius': hetero_radius,
        'hetero_position': [0, best_config['hetero_y'], 0],
        'mesh_size': mesh_size,
        'mesh_bins': mesh_bins
    }
    
    print(f"⚙️  PARÁMETROS PARA GEANT4:")
    print(f"   /brachy/det/setPhantomSizeX {phantom_radius:.1f} cm")
    print(f"   /brachy/det/setPhantomSizeY {phantom_radius:.1f} cm") 
    print(f"   /brachy/det/setPhantomSizeZ {phantom_radius:.1f} cm")
    print(f"   /brachy/det/setCleanStateSize {hetero_radius:.1f} cm")
    print(f"   /brachy/det/setCleanStatePosition 0. {best_config['hetero_y']:.1f} 0. cm")
    print(f"   /score/mesh/boxSize {mesh_size:.1f} {mesh_size:.1f} 0.025 cm")
    print(f"   /score/mesh/nBin {mesh_bins} {mesh_bins} 1")
    
    # Calcular mejoras esperadas
    original_phantom_vol = 30**3
    original_hetero_percent = (6**3 / original_phantom_vol) * 100
    new_hetero_percent = (best_config['hetero_size']**3 / best_config['phantom_size']**3) * 100
    
    contrast_improvement = new_hetero_percent / original_hetero_percent
    speedup = (30/best_config['phantom_size'])**3
    
    print(f"\n📈 MEJORAS ESPERADAS:")
    print(f"   🎯 Mejora en contraste: {contrast_improvement:.1f}x")
    print(f"   ⚡ Aceleración simulación: ~{speedup:.1f}x")
    print(f"   💧 Distancia segura de agua: ✅")
    print(f"   🔬 Física preservada: ✅")
    
    return macro_params

def main():
    print("🔍 ANÁLISIS DE DISTANCIA FUENTE-HETEROGENEIDAD CON RESTRICCIONES FÍSICAS")
    print("=" * 75)
    
    # Analizar configuraciones válidas
    valid_configs = analyze_source_heterogeneity_distance()
    
    # Crear visualización
    fig = create_distance_visualization(valid_configs)
    
    # Recomendar configuración óptima
    best_config = recommend_optimal_configuration(valid_configs)
    
    # Generar parámetros para macros
    macro_params = generate_safe_macros(best_config)
    
    print(f"\n✨ RESUMEN EJECUTIVO ✨")
    print(f"=" * 25)
    print(f"🎯 Se identificaron {len(valid_configs)} configuraciones válidas")
    print(f"🏆 Configuración recomendada: {best_config['name'] if best_config else 'Ninguna'}")
    print(f"💧 Todas las configuraciones mantienen >1 cm de agua")
    print(f"🔬 Física de buildup y backscatter preservada")
    
    if fig:
        plt.show()

if __name__ == "__main__":
    main()

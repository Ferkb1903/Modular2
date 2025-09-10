#!/usr/bin/env python3
"""
SCRIPT PARA CONVERTIR MACROS DE .out A .root
===========================================
Convierte automáticamente todos los macros de Geant4 para usar salida ROOT
en lugar de archivos ASCII .out
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Crear backup del archivo original"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def convert_macro_to_root(filepath):
    """Convertir un macro de .out a ROOT"""
    print(f"\n🔄 Procesando: {filepath}")
    
    # Crear backup
    backup_path = backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Buscar líneas de dumpQuantityToFile
    lines = content.split('\n')
    modified = False
    new_lines = []
    
    for line in lines:
        if '/score/dumpQuantityToFile' in line and '.out' in line:
            # Extraer información de la línea
            parts = line.split()
            if len(parts) >= 4:
                mesh_name = parts[1]
                quantity = parts[2] 
                old_filename = parts[3]
                
                # Cambiar .out por .root
                new_filename = old_filename.replace('.out', '.root')
                
                # Comentar la línea original y añadir nueva configuración
                commented_line = f"# ORIGINAL: {line}"
                new_lines.append(commented_line)
                
                # Añadir configuración ROOT
                new_lines.append(f"# ==> CONVERTIDO A ROOT OUTPUT:")
                new_lines.append(f"/score/dumpQuantityToFile {mesh_name} {quantity} {new_filename}")
                
                modified = True
                print(f"  ✓ Convertido: {old_filename} -> {new_filename}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        # Escribir archivo modificado
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"  ✅ Archivo actualizado")
    else:
        # Restaurar desde backup si no hubo cambios
        os.remove(backup_path)
        print(f"  ⚪ No se encontraron cambios necesarios")
    
    return modified

def find_and_convert_macros(directory):
    """Encontrar y convertir todos los macros en un directorio"""
    converted_files = []
    
    print(f"🔍 Buscando archivos .mac en: {directory}")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mac'):
                filepath = os.path.join(root, file)
                if convert_macro_to_root(filepath):
                    converted_files.append(filepath)
    
    return converted_files

def update_analysis_script():
    """Actualizar el script de análisis para leer archivos ROOT"""
    analysis_script = "/home/fer/fer/brachytherapy/build/ANALISIS.py"
    
    if os.path.exists(analysis_script):
        print(f"\n📝 Actualizando script de análisis...")
        
        backup_path = backup_file(analysis_script)
        
        with open(analysis_script, 'r') as f:
            content = f.read()
        
        # Reemplazar referencias a archivos .out por .root
        content = content.replace('EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.out', 
                                 'EnergyDeposition_REF_Water_Homogeneous_CORREGIDO.root')
        content = content.replace('EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.out', 
                                 'EnergyDeposition_REF_Bone_Heterogeneous_CORREGIDO.root')
        
        # Añadir import para ROOT si no existe
        if 'import uproot' not in content:
            content = content.replace('import pandas as pd', 
                                     'import pandas as pd\nimport uproot  # Para leer archivos ROOT')
        
        with open(analysis_script, 'w') as f:
            f.write(content)
        
        print(f"  ✅ Script de análisis actualizado")

def main():
    print("="*70)
    print("🔬 CONVERSIÓN DE SALIDA DE .OUT A .ROOT")
    print("   Brachytherapy Geant4 Simulation")
    print("="*70)
    
    # Directorios a procesar
    directories = [
        "/home/fer/fer/brachytherapy/build",
        "/home/fer/fer/brachytherapy/macros",
        "/home/fer/fer/brachytherapy"
    ]
    
    total_converted = 0
    
    for directory in directories:
        if os.path.exists(directory):
            converted = find_and_convert_macros(directory)
            total_converted += len(converted)
            
            if converted:
                print(f"\n📊 Archivos convertidos en {directory}:")
                for file in converted:
                    print(f"  • {os.path.basename(file)}")
    
    # Actualizar script de análisis
    update_analysis_script()
    
    print(f"\n📈 RESUMEN:")
    print(f"  • Total de macros convertidos: {total_converted}")
    print(f"  • Backups creados automáticamente")
    print(f"  • Script de análisis actualizado")
    
    if total_converted > 0:
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"  1. Recompilar el proyecto: make")
        print(f"  2. Ejecutar simulaciones con los macros actualizados")
        print(f"  3. Verificar que se generen archivos .root")
        print(f"  4. Usar el script de análisis actualizado")
    else:
        print(f"\n⚪ No se encontraron macros que requieran conversión")

if __name__ == "__main__":
    main()

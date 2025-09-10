#!/usr/bin/env python3
"""
CORRECCIÓN DE COORDENADAS EN DATOS DE GEANT4
============================================
Script para corregir el factor 10 en las coordenadas de los archivos
de deposición de energía de Geant4.

Problema detectado: Geant4 reporta coordenadas en mm pero las marca como cm.
Solución: Dividir coordenadas X,Y,Z por 10 para obtener valores reales en cm.
"""

import pandas as pd
import numpy as np

def corregir_archivo_datos(archivo_entrada, archivo_salida):
    """Corregir las coordenadas en un archivo de datos de Geant4"""
    print(f"📂 Procesando: {archivo_entrada}")
    
    # Leer el archivo línea por línea para preservar comentarios
    with open(archivo_entrada, 'r') as f:
        lineas = f.readlines()
    
    # Procesar líneas
    lineas_corregidas = []
    datos_procesados = 0
    
    for linea in lineas:
        if linea.startswith('#') or linea.strip() == '':
            # Preservar comentarios y líneas vacías
            lineas_corregidas.append(linea)
        else:
            # Procesar línea de datos
            try:
                partes = linea.strip().split()
                if len(partes) == 4:
                    x, y, z, energia = float(partes[0]), float(partes[1]), float(partes[2]), float(partes[3])
                    
                    # CORRECCIÓN: Dividir coordenadas por 10 (mm -> cm)
                    x_corregida = x / 10.0
                    y_corregida = y / 10.0
                    z_corregida = z / 10.0
                    
                    # Crear línea corregida
                    linea_corregida = f"{x_corregida:.2f}  {y_corregida:.2f}  {z_corregida:.2f}  {energia}\n"
                    lineas_corregidas.append(linea_corregida)
                    datos_procesados += 1
                else:
                    # Línea con formato inesperado, preservar como está
                    lineas_corregidas.append(linea)
            except:
                # Error en el parsing, preservar línea original
                lineas_corregidas.append(linea)
    
    # Escribir archivo corregido
    with open(archivo_salida, 'w') as f:
        f.writelines(lineas_corregidas)
    
    print(f"  ✓ {datos_procesados} líneas de datos corregidas")
    print(f"  ✓ Guardado: {archivo_salida}")
    
    return datos_procesados

def verificar_correccion(archivo_corregido):
    """Verificar que la corrección fue exitosa"""
    print(f"🔍 Verificando: {archivo_corregido}")
    
    # Leer datos corregidos
    data = pd.read_csv(archivo_corregido, sep=r'\s+', comment='#', header=None)
    data.columns = ['x', 'y', 'z', 'edep']
    
    # Calcular estadísticas
    x_min, x_max = data['x'].min(), data['x'].max()
    y_min, y_max = data['y'].min(), data['y'].max()
    energia_total = data['edep'].sum()
    
    print(f"  ✓ Rango X: {x_min:.2f} a {x_max:.2f} cm (span: {x_max-x_min:.2f} cm)")
    print(f"  ✓ Rango Y: {y_min:.2f} a {y_max:.2f} cm (span: {y_max-y_min:.2f} cm)")
    print(f"  ✓ Energía total: {energia_total:.2e} MeV")
    print(f"  ✓ Puntos de datos: {len(data)}")
    
    # Verificar que los rangos sean físicamente sensatos (±9 cm aprox)
    if abs(x_max) < 10 and abs(x_min) < 10 and abs(y_max) < 10 and abs(y_min) < 10:
        print("  ✅ Coordenadas corregidas correctamente!")
        return True
    else:
        print("  ❌ Las coordenadas siguen siendo incorrectas")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("CORRECCIÓN DE COORDENADAS EN DATOS DE GEANT4")
    print("Factor de corrección: coordenadas / 10 (mm → cm)")
    print("=" * 60)
    
    # Archivos a corregir
    archivos_originales = [
        'EnergyDeposition_REF_Water_Homogeneous.out',
        'EnergyDeposition_REF_Bone_Heterogeneous.out'
    ]
    
    archivos_corregidos = []
    
    for archivo in archivos_originales:
        # Nombre del archivo corregido
        nombre_base = archivo.replace('.out', '')
        archivo_corregido = f"{nombre_base}_CORREGIDO.out"
        
        # Hacer la corrección
        try:
            datos_procesados = corregir_archivo_datos(archivo, archivo_corregido)
            
            if datos_procesados > 0:
                # Verificar la corrección
                if verificar_correccion(archivo_corregido):
                    archivos_corregidos.append(archivo_corregido)
                    print()
                else:
                    print("  ❌ Error en la corrección\n")
            else:
                print("  ❌ No se encontraron datos para procesar\n")
                
        except Exception as e:
            print(f"  ❌ Error procesando {archivo}: {e}\n")
    
    print("=" * 60)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 60)
    print("📁 Archivos corregidos generados:")
    for archivo in archivos_corregidos:
        print(f"  • {archivo}")
    print("\n💡 Usa estos archivos corregidos para generar los mapas.")
    print("=" * 60)

if __name__ == "__main__":
    main()

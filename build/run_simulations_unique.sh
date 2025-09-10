#!/bin/bash
# =================================================================
# SCRIPT PARA EJECUTAR SIMULACIONES CON ARCHIVOS ROOT ÚNICOS
# =================================================================

# Función para ejecutar simulación con nombre único
run_simulation() {
    local macro_file=$1
    local output_name=$2
    local description=$3
    
    echo "🚀 Ejecutando: $description"
    echo "   Macro: $macro_file"
    echo "   Salida ROOT: $output_name"
    echo "================================"
    
    # Establecer variable de entorno
    export BRACHY_ROOT_FILENAME="$output_name"
    
    # Ejecutar simulación
    ./Brachy "$macro_file"
    
    # Verificar que se creó el archivo
    if [ -f "$output_name" ]; then
        echo "✅ Archivo creado: $output_name"
        echo "📊 Tamaño: $(du -h $output_name | cut -f1)"
    else
        echo "❌ Error: No se creó $output_name"
    fi
    
    echo "================================"
    echo ""
}

# Crear directorio para resultados ROOT
mkdir -p root_results

# Ejecutar simulaciones con nombres únicos
echo "🔬 INICIANDO SIMULACIONES DE BRAQUITERAPIA"
echo "==========================================="

# Simulación 1: Agua homogénea
run_simulation "Macro_REF_Water_Homogeneous_ROOT.mac" \
               "root_results/brachytherapy_water_homogeneous_$(date +%Y%m%d_%H%M%S).root" \
               "Phantom Homogéneo (Solo Agua)"

# Simulación 2: Hueso heterogéneo  
run_simulation "Macro_REF_Bone_Heterogeneous_ROOT.mac" \
               "root_results/brachytherapy_bone_heterogeneous_$(date +%Y%m%d_%H%M%S).root" \
               "Phantom Heterogéneo (Agua + Hueso)"

# Mostrar resultados finales
echo "📁 ARCHIVOS ROOT GENERADOS:"
echo "=========================="
ls -la root_results/*.root

echo ""
echo "✅ ¡Simulaciones completadas!"
echo "Los archivos ROOT están en: ./root_results/"

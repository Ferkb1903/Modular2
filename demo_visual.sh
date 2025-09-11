#!/bin/bash

# Script para demostración visual interactiva HDR
echo "🎬 HDR Brachytherapy - Demostración Visual"
echo "=========================================="

# Verificar compilación
if [ ! -f "./build/hdr_brachy" ]; then
    echo "📦 Compilando proyecto..."
    cd build && make -j$(nproc) && cd ..
fi

echo "🎯 Configurando demostración visual..."
echo ""
echo "Esta demostración mostrará:"
echo "  🔵 Rayos gamma del Ir-192 (azul)"
echo "  🔴 Electrones secundarios (rojo)" 
echo "  🟡 Fuente encapsulada (amarillo)"
echo "  💧 Fantoma de agua (transparente)"
echo ""
echo "La simulación ejecutará eventos paso a paso"
echo "para que puedas observar la física en acción"
echo ""
echo "🚀 Presiona ENTER para iniciar..."
read

cd build

# Ejecutar con el macro de demostración
./hdr_brachy ../macros/demo_visual.mac

echo ""
echo "✅ Demostración completada"
echo "💡 Para modo interactivo completo, ejecuta: ./run_visualization.sh"

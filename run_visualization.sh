#!/bin/bash

# Script para ejecutar la simulación HDR con visualización
echo "🔬 HDR Brachytherapy - Modo Visualización"
echo "========================================"

# Verificar que existe el ejecutable
if [ ! -f "./build/hdr_brachy" ]; then
    echo "❌ Error: Ejecutable no encontrado. Compilando..."
    cd build
    make -j$(nproc)
    cd ..
    
    if [ ! -f "./build/hdr_brachy" ]; then
        echo "❌ Error: Falló la compilación"
        exit 1
    fi
fi

echo "✅ Ejecutable encontrado"
echo "🎯 Iniciando simulación con visualización..."
echo ""
echo "Instrucciones:"
echo "  • La ventana de visualización se abrirá automáticamente"
echo "  • Usa los comandos en la interfaz para controlar la simulación"
echo "  • Comandos útiles:"
echo "    /run/beamOn 10    - Ejecutar 10 eventos"
echo "    /vis/viewer/zoom 2 - Hacer zoom x2"
echo "    /vis/viewer/refresh - Actualizar vista"
echo ""
echo "🚀 Presiona ENTER para continuar..."
read

# Cambiar al directorio de trabajo
cd build

# Ejecutar en modo interactivo (sin argumentos)
./hdr_brachy

echo "✅ Simulación completada"

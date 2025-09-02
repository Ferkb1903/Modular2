#!/bin/bash

# Script principal para HDR Brachytherapy Simulation
# Limpio y optimizado

echo "🎯 HDR Brachytherapy Monte Carlo Simulation"
echo "==========================================="

# Verificar ejecutable
if [ ! -f "build/hdr_brachy" ]; then
    echo "📦 Compilando proyecto..."
    mkdir -p build
    cd build
    cmake ..
    make -j$(nproc)
    cd ..
    
    if [ ! -f "build/hdr_brachy" ]; then
        echo "❌ Error en compilación"
        exit 1
    fi
fi

echo "✅ Ejecutable listo"
echo ""
echo "Opciones disponibles:"
echo "1. Simulación rápida (100 eventos)"
echo "2. Simulación estándar (5000 eventos)"
echo "3. Modo interactivo con visualización"
echo ""

read -p "Selecciona opción (1-3): " choice

case $choice in
    1)
        echo "🚀 Ejecutando simulación rápida..."
        cd build
        ./hdr_brachy ../macros/quick_test.mac
        ;;
    2)
        echo "🚀 Ejecutando simulación estándar..."
        cd build
        ./hdr_brachy ../macros/run_tg43.mac
        ;;
    3)
        echo "🎬 Iniciando modo interactivo..."
        echo "Comandos útiles:"
        echo "  /run/initialize"
        echo "  /vis/open OGLIQt"
        echo "  /vis/drawVolume"
        echo "  /run/beamOn 10"
        cd build
        ./hdr_brachy
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo "✅ Simulación completada"

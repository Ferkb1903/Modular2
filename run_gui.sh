#!/bin/bash

# Script para ejecutar simulación HDR con visualización
echo "🎯 HDR Brachytherapy - Visualización Interactiva"
echo "=============================================="

# Verificar que tenemos entorno gráfico
if [ -z "$DISPLAY" ]; then
    echo "❌ Error: No hay entorno gráfico disponible (DISPLAY no definido)"
    echo "💡 Ejecuta en un terminal con entorno gráfico o usa:"
    echo "   export DISPLAY=:0"
    exit 1
fi

# Comprobar ejecutable
if [ ! -f "./build/hdr_brachy" ]; then
    echo "📦 Compilando proyecto..."
    cd build && make -j$(nproc) && cd ..
    if [ ! -f "./build/hdr_brachy" ]; then
        echo "❌ Error en la compilación"
        exit 1
    fi
fi

echo "✅ Sistema preparado"
echo ""
echo "🎬 MODO VISUALIZACIÓN:"
echo "  1. Se abrirá ventana OpenGL con la geometría"
echo "  2. Usa la interfaz para controlar la simulación"
echo "  3. Comandos básicos en terminal:"
echo "     /run/beamOn 10    - Ejecutar 10 eventos"
echo "     /vis/viewer/zoom 2 - Zoom x2"
echo "     /exit             - Salir"
echo ""

# Crear directorio temporal para la sesión
mkdir -p temp
cd build

# Ejecutar con display forzado
DISPLAY=${DISPLAY:-:0} ./hdr_brachy 2>/dev/null || {
    echo ""
    echo "❌ No se pudo abrir ventana gráfica"
    echo "💡 Prueba ejecutar en modo interactivo:"
    echo "   cd build"
    echo "   ./hdr_brachy"
    echo "   Luego usa los comandos:"
    echo "   /run/initialize"
    echo "   /vis/open OGL"
    echo "   /vis/drawVolume"
    echo "   /run/beamOn 10"
}

echo ""
echo "✅ Sesión completada"

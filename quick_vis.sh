#!/bin/bash

# Script de inicio rápido para visualización HDR
echo "🎯 HDR Brachytherapy - Inicio Rápido"
echo "====================================="

cd build

# Crear macro temporal con comandos básicos
cat > quick_start.mac << 'EOF'
# Inicialización y visualización HDR
/run/initialize
/vis/open OGLIQt
/vis/drawVolume
/vis/viewer/set/viewpointVector -1 -1 1
/vis/viewer/set/upVector 0 0 1
/vis/viewer/zoom 2.5
/vis/viewer/set/style wireframe
/vis/scene/add/trajectories smooth
/vis/modeling/trajectories/create/drawByParticleID
/vis/modeling/trajectories/drawByParticleID-0/set gamma blue
/vis/modeling/trajectories/drawByParticleID-0/set e- red
/vis/modeling/trajectories/drawByParticleID-0/set e+ green
/vis/viewer/set/autoRefresh true

# Información para el usuario
echo "==================================="
echo "HDR Brachytherapy - LISTO"
echo "==================================="
echo "Comandos disponibles:"
echo "/run/beamOn 10     - Ejecutar 10 eventos"
echo "/vis/viewer/zoom 3 - Hacer zoom"
echo "/exit              - Salir"
echo "==================================="
EOF

echo "🚀 Ejecutando simulación con visualización..."
echo "La ventana OpenGL se abrirá automáticamente"
echo ""

./hdr_brachy quick_start.mac

echo "✅ Simulación completada"

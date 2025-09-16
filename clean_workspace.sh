#!/bin/bash

# Script para limpiar el workspace antes de subirlo a GitHub
# Elimina archivos temporales, resultados y mantiene solo código fuente

echo "🧹 LIMPIANDO WORKSPACE PARA GITHUB..."
echo "=========================================="

# Cambiar al directorio del proyecto
cd /home/fer/fer/brachytherapy

echo "📁 Eliminando archivos de resultados y temporales..."

# Eliminar archivos ROOT de resultados
rm -f *.root
echo "✅ Archivos *.root eliminados"

# Eliminar archivos de imagen/plots
rm -f *.png *.jpg *.jpeg *.gif *.pdf
echo "✅ Archivos de imagen eliminados"

# Eliminar archivos CSV de datos
rm -f *.csv
echo "✅ Archivos *.csv eliminados"

# Eliminar archivos de texto de resultados
rm -f *.txt
echo "✅ Archivos *.txt eliminados"

# Eliminar directorio build completo
if [ -d "build" ]; then
    rm -rf build/
    echo "✅ Directorio build/ eliminado"
fi

# Eliminar directorios de resultados/análisis
if [ -d "results" ]; then
    rm -rf results/
    echo "✅ Directorio results/ eliminado"
fi

if [ -d "output" ]; then
    rm -rf output/
    echo "✅ Directorio output/ eliminado"
fi

if [ -d "analysis" ]; then
    rm -rf analysis/
    echo "✅ Directorio analysis/ eliminado"
fi

if [ -d "comparison" ]; then
    rm -rf comparison/
    echo "✅ Directorio comparison/ eliminado"
fi

# Eliminar directorios de archivos antiguos
if [ -d "archive_old_analysis_scripts" ]; then
    rm -rf archive_old_analysis_scripts/
    echo "✅ Directorio archive_old_analysis_scripts/ eliminado"
fi

if [ -d "archive_old_ascii_files" ]; then
    rm -rf archive_old_ascii_files/
    echo "✅ Directorio archive_old_ascii_files/ eliminado"
fi

if [ -d "archive_old_results" ]; then
    rm -rf archive_old_results/
    echo "✅ Directorio archive_old_results/ eliminado"
fi

# Eliminar scripts de análisis Python (mantener solo los principales)
rm -f analisis_*.py
rm -f analyze_*.py
rm -f compare_*.py
rm -f generate_*.py
rm -f investigate_*.py
rm -f summary_*.py
rm -f visualize_*.py
echo "✅ Scripts de análisis Python eliminados"

# Eliminar archivos C de análisis ROOT
rm -f *.C
echo "✅ Archivos *.C eliminados"

# Eliminar archivos de backup
rm -f *.bak
rm -f *~
rm -f *.backup
echo "✅ Archivos de backup eliminados"

# Eliminar directorio History si existe
if [ -d "History" ]; then
    rm -rf History/
    echo "✅ Directorio History/ eliminado"
fi

# Eliminar test_macro si existe
if [ -d "test_macro" ]; then
    rm -rf test_macro/
    echo "✅ Directorio test_macro/ eliminado"
fi

echo ""
echo "📋 ARCHIVOS MANTENIDOS (código fuente esencial):"
echo "=========================================="

# Mostrar estructura limpia
find . -type f -not -path "./.git/*" | sort

echo ""
echo "✅ WORKSPACE LIMPIO PARA GITHUB"
echo "=========================================="
echo "📁 Mantenidos:"
echo "   • Código fuente C++ (src/, include/)"
echo "   • Archivos de configuración (CMakeLists.txt, Makefile)"
echo "   • Macros principales (*.mac)"
echo "   • Scripts de ejecución principales"
echo "   • Documentación (*.md)"
echo "   • Archivo principal (main.cc, Brachy.cc)"
echo ""
echo "🗑️  Eliminados:"
echo "   • Resultados de simulación (*.root)"
echo "   • Imágenes y plots (*.png, *.jpg)"
echo "   • Archivos de datos (*.csv, *.txt)"
echo "   • Directorios de compilación (build/)"
echo "   • Scripts de análisis temporales"
echo "   • Archivos de backup"
echo ""
echo "🚀 Listo para: git add . && git commit && git push"
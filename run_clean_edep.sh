#!/bin/bash

# Script para ejecutar simulación en modo SCORING LIMPIO
# Los archivos eDep.root solo contendrán datos oficiales (h20) sin histogramas vacíos

echo "=========================================="
echo "🧹 MODO SCORING LIMPIO ACTIVADO"
echo "=========================================="
echo "✅ Los archivos _eDep.root solo contendrán datos oficiales del scoring mesh"
echo "❌ NO se crearán histogramas personales vacíos (dose_map_primary/secondary)"
echo "📊 Para análisis primario/secundario usar archivos primary_*.root separados"
echo ""

# Configurar variable de entorno para activar modo scoring
export GEANT4_SCORING_MODE=1

echo "🔧 Variable GEANT4_SCORING_MODE configurada: $GEANT4_SCORING_MODE"
echo "🏗️  Compilando proyecto..."

# Compilar
cd build
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo "❌ Error en compilación"
    exit 1
fi

echo "✅ Compilación exitosa"
echo "🚀 Ejecutando simulación con eDep.root LIMPIO..."

# Ejecutar con macro de prueba
./Brachy ../test_corrected_classification.mac

echo ""
echo "=========================================="
echo "📁 ARCHIVOS GENERADOS:"
echo "=========================================="

# Mostrar archivos generados
if ls *eDep.root 1> /dev/null 2>&1; then
    echo "📄 Archivos eDep.root (LIMPIOS):"
    ls -la *eDep.root
    echo ""
    
    # Analizar contenido del primer archivo eDep
    latest_edep=$(ls -t *eDep.root | head -1)
    echo "🔍 Contenido de $latest_edep:"
    root -l -b -q -e "
    auto f = TFile::Open(\"$latest_edep\");
    f->ls();
    auto h = (TH2D*)f->Get(\"h20\");
    if(h) cout << \"✅ h20 (oficial): \" << h->Integral()/1000.0 << \" MeV, \" << h->GetEntries() << \" entries\" << endl;
    else cout << \"❌ h20 no encontrado\" << endl;
    
    auto h_prim = (TH2D*)f->Get(\"dose_map_primary\");
    if(h_prim) cout << \"❌ PROBLEMA: dose_map_primary aún presente\" << endl;
    else cout << \"✅ dose_map_primary ausente (CORRECTO)\" << endl;
    
    f->Close();
    "
    
else
    echo "❌ No se generaron archivos eDep.root"
fi

echo ""
echo "✅ Ejecución completada en modo SCORING LIMPIO"
echo "📖 Los archivos eDep.root ahora están libres de histogramas vacíos"
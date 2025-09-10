#!/usr/bin/env python3
"""
SCRIPT PARA GENERAR ARCHIVOS ROOT ÚNICOS
========================================
Modifica el código para usar variables de entorno para nombres únicos
"""

import re

def crear_version_con_variable_entorno():
    """Crear versión que usa variables de entorno"""
    
    # Leer el archivo actual
    with open('/home/fer/fer/brachytherapy/src/BrachyUserScoreWriter.cc', 'r') as f:
        content = f.read()
    
    # Versión alternativa usando variables de entorno
    codigo_alternativo = '''
// Alternativa usando variables de entorno
#include <cstdlib>

auto analysisManager = G4AnalysisManager::Instance();

// Get filename from environment variable or use default
const char* env_filename = std::getenv("BRACHY_ROOT_FILENAME");
G4String filename = env_filename ? G4String(env_filename) : "brachytherapy.root";

G4cout << "Creating ROOT file: " << filename << G4endl;

G4bool fileOpen = analysisManager -> OpenFile(filename);
if (! fileOpen) {
    G4cerr << "\\n---> The ROOT output file has not been opened "
           << analysisManager->GetFileName() << G4endl;
}
'''
    
    print("💡 ALTERNATIVA: Usar variables de entorno")
    print("="*50)
    print("1. Agregar #include <cstdlib> al inicio del archivo")
    print("2. Reemplazar el bloque de OpenFile con:")
    print(codigo_alternativo)
    print("\n🚀 EJEMPLO DE USO:")
    print("export BRACHY_ROOT_FILENAME='water_homogeneous.root'")
    print("./Brachy macro.mac")
    print("\nexport BRACHY_ROOT_FILENAME='bone_heterogeneous.root'") 
    print("./Brachy macro.mac")

if __name__ == "__main__":
    crear_version_con_variable_entorno()

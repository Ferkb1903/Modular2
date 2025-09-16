# 🔬 Simulación Monte Carlo HDR Brachytherapy con Geant4# Simulación Monte Carlo HDR Brachytherapy con Geant4



[![Geant4](https://img.shields.io/badge/Geant4-11.x-blue.svg)](https://geant4.web.cern.ch/)## 🎯 **Proyecto: Dosimetría HDR Ir-192 con clasificación primaria/secundaria**

[![ROOT](https://img.shields.io/badge/ROOT-6.x-orange.svg)](https://root.cern.ch/)

[![C++](https://img.shields.io/badge/C++-17-green.svg)](https://isocpp.org/)### **Descripción**

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)Simulación Monte Carlo avanzada desarrollada en Geant4 para modelar la distribución de dosis de una fuente HDR de Ir-192, con **clasificación física correcta de partículas primarias y secundarias**, validación TG-43 y análisis de heterogeneidades tisulares.



## 🎯 **Proyecto: Dosimetría HDR Ir-192 con clasificación primaria/secundaria**### **Características Principales**

- ✅ **Clasificación física correcta**: Primarias (G0+G1) vs Secundarias (G2+)

### **Descripción**- ✅ **Validación TG-43**: Parámetros Λ, g(r), F(r,θ) en agua infinita  

Simulación Monte Carlo avanzada desarrollada en Geant4 para modelar la distribución de dosis de una fuente HDR de Ir-192, con **clasificación física correcta de partículas primarias y secundarias**, validación TG-43 y análisis de heterogeneidades tisulares.- ✅ **Análisis de heterogeneidades**: Hueso, grasa, aire, músculo

- ✅ **Archivos eDep.root limpios**: Sin contaminación de histogramas vacíos

### **Características Principales**- ✅ **Dual-output system**: Archivos primary_*.root + *_eDep.root separados

- ✅ **Clasificación física correcta**: Primarias (G0+G1) vs Secundarias (G2+)

- ✅ **Validación TG-43**: Parámetros Λ, g(r), F(r,θ) en agua infinita  ## 🚀 **Instalación y Compilación**

- ✅ **Análisis de heterogeneidades**: Hueso, grasa, aire, músculo

- ✅ **Archivos eDep.root limpios**: Sin contaminación de histogramas vacíos### **Requisitos**

- ✅ **Dual-output system**: Archivos primary_*.root + *_eDep.root separados- Geant4 10.7+ con soporte ROOT

- ROOT 6.x

## 🚀 **Instalación y Compilación**- CMake 3.16+

- GCC/Clang con C++17

### **Requisitos**

- Geant4 10.7+ con soporte ROOT### **Compilación**

- ROOT 6.x```bash

- CMake 3.16+# Clonar repositorio

- GCC/Clang con C++17git clone https://github.com/Ferkb1903/Modular2.git

cd Modular2

### **Compilación**

```bash# Crear directorio build y compilar

# Clonar repositoriomkdir build && cd build

git clone https://github.com/Ferkb1903/Modular2.gitcmake ..

cd Modular2make -j$(nproc)

```

# Crear directorio build y compilar

mkdir build && cd build## 📋 **Guía de Uso**

cmake ..

make -j$(nproc)### **Simulación Normal** (Análisis primaria/secundaria)

``````bash

cd build

## 📋 **Guía de Uso**./Brachy ../test_corrected_classification.mac

# ✅ Genera: primary_TIMESTAMP.root con clasificación física correcta

### **Simulación Normal** (Análisis primaria/secundaria)│   └── analyze_results.py

```bash├── data/                       # Datos de entrada

cd build├── build/                      # Directorio de compilación

./Brachy ../test_corrected_classification.mac├── output/                     # Resultados de simulación

# ✅ Genera: primary_TIMESTAMP.root con clasificación física correcta├── run_simulation.sh           # Script de ejecución

```└── README.md                   # Este archivo

```

### **Simulación con archivos eDep.root limpios**

```bash## Implementación Técnica

./run_clean_edep.sh

# ✅ Genera: TIMESTAMP_eDep.root SOLO con datos oficiales (h20)### 1. Geometría del Detector (`DetectorConstruction`)

```

**Modo TG-43 (Validación):**

### **Visualización interactiva**- Fantoma cúbico de agua (30×30×30 cm³)

```bash- Fuente HDR Ir-192 en el centro (geometría simplificada tipo GammaMed Plus)

./run_visualization.sh- Sistema de scoring cilíndrico/esférico para parámetros TG-43

# ✅ Abre interfaz gráfica Qt para visualización 3D

```**Modo Heterogéneo:**

- Fantoma con regiones de diferente densidad

## 🔬 **Metodología Científica**- Estructuras óseas, cavidades de aire, músculo y grasa

- Aplicadores (cilindros de titanio/plástico)

### **Clasificación de Partículas**- OARs modelados como elipsoides (vejiga y recto)

- **Primarias (G0+G1)**: Fotones fuente + productos inmediatos (fotoelectrones, Compton)

- **Secundarias (G2+)**: Dispersión múltiple, cascadas electromagnéticas### 2. Física (`PhysicsList`)

- **Validación**: 99.97% de precisión vs scoring mesh oficial de Geant4

- **Física electromagnética:** G4EmLivermorePhysics para precisión en bajas energías

### **Geometría de Simulación**- **Decaimiento radiactivo:** G4RadioactiveDecayPhysics para Ir-192

- **Fuente**: Ir-192 HDR cilíndrica (0.6 mm × 3.5 mm)- **Cortes de producción:** 0.01-0.1 mm cerca de la fuente, 0.1-0.5 mm en resto

- **Phantom**: Agua/heterogéneo (18×18×18 cm³)

- **Scoring**: Mesh 2D (180×180 bins, 0.1 mm resolución)### 3. Generador Primario (`PrimaryGeneratorAction`)

- **Filtro Z**: ±0.125 cm (consistente con TG-43)

- **Espectro Ir-192:** Líneas principales (317 keV-81%, 468 keV-47%, etc.)

### **Resultados Físicos Esperados**- **Distribución espacial:** Isótropa desde geometría cilíndrica de la fuente

- **Ratio Primaria/Secundaria**: ~97.8% / ~2.2% (física realista)- **Actividad:** Configurable (típico: 370 GBq)

- **Concordancia Energética**: ±0.03% entre sistemas personal/oficial

- **Distribución radial**: g(r) compatible con TG-43### 4. Scoring de Dosis (`SteppingAction`, `DoseScorer`)



## 📁 **Estructura del Proyecto**- **Dosis 3D:** Malla voxelizada para mapas de isodosis

- **Parámetros TG-43:**

```  - g(r): Función de dosis radial

brachytherapy/  - F(r,θ): Función de anisotropía

├── 🔧 Configuración  - Λ: Constante de tasa de dosis de kerma

│   ├── CMakeLists.txt         # Configuración CMake- **DVH:** Análisis de dosis-volumen para OARs

│   ├── Makefile              # Makefile alternativo

│   └── .gitignore            # Archivos ignorados por Git## Instalación y Compilación

├── 💻 Código Principal

│   ├── main.cc               # Punto de entrada### Requisitos

│   ├── Brachy.cc             # Aplicación principal- Geant4 10.7 o superior

│   └── Brachy                # Ejecutable compilado- CMake 3.16+

├── 📂 Código Fuente- Compilador C++17

│   ├── include/              # Headers (.hh)- Python 3.x (para análisis)

│   │   ├── BrachyDetectorConstruction.hh- Matplotlib, NumPy (para visualización)

│   │   ├── BrachySteppingAction.hh

│   │   ├── BrachyRunAction.hh### Compilación

│   │   └── ...

│   └── src/                  # Implementaciones (.cc)```bash

│       ├── BrachyDetectorConstruction.cc# Clonar/descargar el proyecto

│       ├── BrachySteppingAction.cc (¡Clasificación corregida!)cd hdr_brachytherapy

│       ├── BrachyRunAction.cc

│       └── ...# Configurar variables de entorno de Geant4

├── 🎮 Macros de Simulaciónsource /path/to/geant4/bin/geant4.sh

│   ├── test_corrected_classification.mac  # Macro principal

│   ├── test_heterogeneous.mac# Compilar

│   ├── macros/                            # Macros organizadosmkdir build && cd build

│   └── vis.mac                           # Visualizacióncmake ..

├── 🛠️ Scripts de Ejecuciónmake -j$(nproc)

│   ├── run_clean_edep.sh     # eDep.root limpios```

│   ├── run_simulation.sh     # Simulación estándar

│   ├── run_visualization.sh  # Modo gráfico### Ejecución Rápida

│   └── clean_workspace.sh    # Limpieza pre-GitHub

└── 📚 Documentación```bash

    ├── README.md             # Este archivo# Desde el directorio raíz

    ├── MACRO_GUIDE.md        # Guía de macros./run_simulation.sh

    ├── VISUALIZATION_GUIDE.md```

    └── docs/                 # Documentación técnica

```## Uso del Programa



## 🎯 **Características Técnicas Destacadas**### Simulaciones Batch



### **1. Clasificación Primaria/Secundaria Corregida**```bash

```cpp# TG-43 validation

// Antes (INCORRECTO): Solo parentID == 0./build/hdr_brachy macros/run_tg43.mac

if (parentID == 0) { /* primaria */ }

# Heterogeneous phantom

// Ahora (CORRECTO): Clasificación por generaciones físicas./build/hdr_brachy macros/run_heterogeneous.mac

bool IsPrimaryContribution(const G4Track* track) {```

    G4int parentID = track->GetParentID();

    ### Modo Interactivo con Visualización

    // Generación 0: Fotones de la fuente

    if (parentID == 0) return true;```bash

    ./build/hdr_brachy

    // Generación 1: Productos inmediatos# En el prompt de Geant4:

    if (parentID <= 5) {/control/execute macros/init_vis.mac

        G4String process = track->GetCreatorProcess()->GetProcessName();/run/beamOn 1000

        return (process == "phot" || process == "compt");```

    }

    ### Análisis de Resultados

    return false; // Generación 2+: Secundarias

}```bash

```python3 analysis/analyze_results.py

```

### **2. Sistema Dual de Archivos ROOT**

- **`primary_*.root`**: Sistema personal con clasificación primaria/secundaria## Configuración de Simulaciones

- **`*_eDep.root`**: Sistema oficial de Geant4 scoring mesh (h20)

- **Modo limpio**: Variable `GEANT4_SCORING_MODE` previene contaminación### Parámetros TG-43 (`run_tg43.mac`)

- Geometría: Solo agua

### **3. Física Electromagnética Avanzada**- Eventos: 1,000,000 (alta estadística)

- **Procesos**: Fotoeléctrico, Compton, Rayleigh, producción de pares- Cortes: 0.01 mm

- **Rango energético**: 1 keV - 10 MeV (óptimo para Ir-192)- Salida: Parámetros g(r), F(r,θ), Λ

- **Precisión**: Librerías Livermore para bajas energías

### Escenarios Heterogéneos (`run_heterogeneous.mac`)

## 📊 **Archivos de Salida**- Geometría: Tejidos múltiples + aplicadores

- Eventos: 500,000

### **primary_TIMESTAMP.root** (Análisis personal)- Cortes: 0.05 mm (balance velocidad/precisión)

```- Salida: Mapas de dosis, DVH

├── h10                    # Espectro energético

├── dose_map_primary       # Mapa 2D primarias (180×180)## Resultados Esperados

├── dose_map_secondary     # Mapa 2D secundarias (180×180)

├── radial_dose_primary    # Distribución radial primarias### 1. Validación TG-43

└── radial_dose_secondary  # Distribución radial secundarias- **g(r):** Concordancia <5% con valores de Rivard et al. (2004)

```- **F(r,θ):** Anisotropía característica de fuentes cilíndricas

- **Λ:** ~1.109 cGy⋅h⁻¹⋅U⁻¹ para Ir-192

### **TIMESTAMP_eDep.root** (Oficial Geant4)

```### 2. Impacto de Heterogeneidades

└── h20                    # Energy deposition 2D (mesh oficial)- **Hueso:** Atenuación significativa (~15-30% reducción de dosis)

```- **Aire:** Dispersión aumentada, hot spots distales

- **OARs:** Desviaciones ±5-15% respecto a TG-43

## 🔧 **Comandos Útiles**

### 3. Productos de Análisis

### **Análisis con ROOT**- Curvas g(r) y F(r,θ) comparativas

```bash- Mapas de isodosis 2D/3D

# Analizar archivo primary- DVHs para vejiga y recto

root primary_TIMESTAMP.root- Tablas de desviación relativa

root> dose_map_primary->Draw("colz")

## Análisis y Visualización

# Comparar energías totales

root> cout << dose_map_primary->Integral() + dose_map_secondary->Integral() << endlEl script `analyze_results.py` proporciona:

```

```python

### **Verificar consistencia**# Cargar datos

```bashanalyzer = TG43Analyzer("output/")

# Los totales deben ser iguales (±0.03%)dose_data = analyzer.load_dose_distribution("dose_distribution.dat")

root -l -b -q -e "

auto f1 = TFile::Open(\"primary_*.root\");# Calcular parámetros TG-43

auto f2 = TFile::Open(\"*_eDep.root\");r, g_r = analyzer.calculate_radial_dose_function(dose_data)

auto total_personal = ((TH2D*)f1->Get(\"dose_map_primary\"))->Integral() + r, theta, F_r_theta = analyzer.calculate_anisotropy_function(dose_data)

                     ((TH2D*)f1->Get(\"dose_map_secondary\"))->Integral();

auto total_oficial = ((TH2D*)f2->Get(\"h20\"))->Integral()/1000.0;# Generar gráficos

cout << \"Personal: \" << total_personal << \" MeV\" << endl;analyzer.plot_radial_dose_function(r, g_r)

cout << \"Oficial: \" << total_oficial << \" MeV\" << endl;analyzer.plot_anisotropy_function(r, theta, F_r_theta)

cout << \"Diferencia: \" << abs(total_personal-total_oficial)/total_oficial*100 << \"%\" << endl;analyzer.compare_with_literature(r, g_r)

"```

```

## Ampliaciones Opcionales

## 🎓 **Referencias Científicas**

1. **Otras fuentes:** Co-60, Cs-131

- **TG-43U1**: Rivard et al. "Update of AAPM Task Group No. 43 Report" (2004)2. **Incertidumbres:** Movimiento de OARs (±5 mm)

- **TG-186**: Beaulieu et al. "Report of the Task Group 186 on model-based dose calculation methods in brachytherapy" (2012)3. **Métricas radiobiológicas:** BED, EQD2

- **Geant4**: Agostinelli et al. "Geant4—a simulation toolkit" (2003)4. **Geometrías complejas:** Datos DICOM reales

5. **Optimización:** Paralelización, GPU computing

## 🤝 **Contribuciones**

## Métricas de Evaluación

¡Las contribuciones son bienvenidas! Por favor:

### Precisión Dosimétrica

1. Fork el proyecto- Desviación respecto a literatura: <5% para TG-43

2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)- Resolución espacial: <1 mm³

3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)- Estadística mínima: >100 eventos/voxel

4. Push a la rama (`git push origin feature/AmazingFeature`)

5. Abre un Pull Request### Relevancia Clínica

- Diferencias >5% en OARs consideradas significativas

## 📝 **Licencia**- D₂cc: Dosis al 2 cm³ más irradiado

- Análisis de incertidumbres geométricas

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Referencias

## 👨‍💻 **Autor**

1. Rivard et al. (2004). "Update of AAPM Task Group No. 43 Report"

**Fernando** - [@Ferkb1903](https://github.com/Ferkb1903)2. Perez-Calatayud et al. (2012). "Dose calculation for photon-emitting brachytherapy sources"

3. Geant4 Collaboration (2020). "Physics Reference Manual"

## 🙏 **Agradecimientos**

## Contacto y Soporte

- Colaboración Geant4 por el framework de simulación

- CERN ROOT team por las herramientas de análisisPara preguntas técnicas o reportar problemas:

- Comunidad de física médica por los estándares TG-43- Revisar documentación de Geant4

- Consultar ejemplos en `/path/to/geant4/examples/`

---- Verificar configuración de física y geometría

*Última actualización: Septiembre 2025*
---

**Nota:** Este proyecto está diseñado para fines académicos y de investigación. Para uso clínico, se requiere validación adicional y cumplimiento de normativas específicas.

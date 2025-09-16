# Simulación Monte Carlo HDR Brachytherapy con Geant4

## 🎯 **Proyecto: Dosimetría HDR Ir-192 con clasificación primaria/secundaria**

### **Descripción**
Simulación Monte Carlo avanzada desarrollada en Geant4 para modelar la distribución de dosis de una fuente HDR de Ir-192, con **clasificación física correcta de partículas primarias y secundarias**, validación TG-43 y análisis de heterogeneidades tisulares.

### **Características Principales**
- ✅ **Clasificación física correcta**: Primarias (G0+G1) vs Secundarias (G2+)
- ✅ **Validación TG-43**: Parámetros Λ, g(r), F(r,θ) en agua infinita  
- ✅ **Análisis de heterogeneidades**: Hueso, grasa, aire, músculo
- ✅ **Archivos eDep.root limpios**: Sin contaminación de histogramas vacíos
- ✅ **Dual-output system**: Archivos primary_*.root + *_eDep.root separados

## 🚀 **Instalación y Compilación**

### **Requisitos**
- Geant4 10.7+ con soporte ROOT
- ROOT 6.x
- CMake 3.16+
- GCC/Clang con C++17

### **Compilación**
```bash
# Clonar repositorio
git clone https://github.com/Ferkb1903/Modular2.git
cd Modular2

# Crear directorio build y compilar
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## 📋 **Guía de Uso**

### **Simulación Normal** (Análisis primaria/secundaria)
```bash
cd build
./Brachy ../test_corrected_classification.mac
# ✅ Genera: primary_TIMESTAMP.root con clasificación física correcta
│   └── analyze_results.py
├── data/                       # Datos de entrada
├── build/                      # Directorio de compilación
├── output/                     # Resultados de simulación
├── run_simulation.sh           # Script de ejecución
└── README.md                   # Este archivo
```

## Implementación Técnica

### 1. Geometría del Detector (`DetectorConstruction`)

**Modo TG-43 (Validación):**
- Fantoma cúbico de agua (30×30×30 cm³)
- Fuente HDR Ir-192 en el centro (geometría simplificada tipo GammaMed Plus)
- Sistema de scoring cilíndrico/esférico para parámetros TG-43

**Modo Heterogéneo:**
- Fantoma con regiones de diferente densidad
- Estructuras óseas, cavidades de aire, músculo y grasa
- Aplicadores (cilindros de titanio/plástico)
- OARs modelados como elipsoides (vejiga y recto)

### 2. Física (`PhysicsList`)

- **Física electromagnética:** G4EmLivermorePhysics para precisión en bajas energías
- **Decaimiento radiactivo:** G4RadioactiveDecayPhysics para Ir-192
- **Cortes de producción:** 0.01-0.1 mm cerca de la fuente, 0.1-0.5 mm en resto

### 3. Generador Primario (`PrimaryGeneratorAction`)

- **Espectro Ir-192:** Líneas principales (317 keV-81%, 468 keV-47%, etc.)
- **Distribución espacial:** Isótropa desde geometría cilíndrica de la fuente
- **Actividad:** Configurable (típico: 370 GBq)

### 4. Scoring de Dosis (`SteppingAction`, `DoseScorer`)

- **Dosis 3D:** Malla voxelizada para mapas de isodosis
- **Parámetros TG-43:**
  - g(r): Función de dosis radial
  - F(r,θ): Función de anisotropía
  - Λ: Constante de tasa de dosis de kerma
- **DVH:** Análisis de dosis-volumen para OARs

## Instalación y Compilación

### Requisitos
- Geant4 10.7 o superior
- CMake 3.16+
- Compilador C++17
- Python 3.x (para análisis)
- Matplotlib, NumPy (para visualización)

### Compilación

```bash
# Clonar/descargar el proyecto
cd hdr_brachytherapy

# Configurar variables de entorno de Geant4
source /path/to/geant4/bin/geant4.sh

# Compilar
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### Ejecución Rápida

```bash
# Desde el directorio raíz
./run_simulation.sh
```

## Uso del Programa

### Simulaciones Batch

```bash
# TG-43 validation
./build/hdr_brachy macros/run_tg43.mac

# Heterogeneous phantom
./build/hdr_brachy macros/run_heterogeneous.mac
```

### Modo Interactivo con Visualización

```bash
./build/hdr_brachy
# En el prompt de Geant4:
/control/execute macros/init_vis.mac
/run/beamOn 1000
```

### Análisis de Resultados

```bash
python3 analysis/analyze_results.py
```

## Configuración de Simulaciones

### Parámetros TG-43 (`run_tg43.mac`)
- Geometría: Solo agua
- Eventos: 1,000,000 (alta estadística)
- Cortes: 0.01 mm
- Salida: Parámetros g(r), F(r,θ), Λ

### Escenarios Heterogéneos (`run_heterogeneous.mac`)
- Geometría: Tejidos múltiples + aplicadores
- Eventos: 500,000
- Cortes: 0.05 mm (balance velocidad/precisión)
- Salida: Mapas de dosis, DVH

## Resultados Esperados

### 1. Validación TG-43
- **g(r):** Concordancia <5% con valores de Rivard et al. (2004)
- **F(r,θ):** Anisotropía característica de fuentes cilíndricas
- **Λ:** ~1.109 cGy⋅h⁻¹⋅U⁻¹ para Ir-192

### 2. Impacto de Heterogeneidades
- **Hueso:** Atenuación significativa (~15-30% reducción de dosis)
- **Aire:** Dispersión aumentada, hot spots distales
- **OARs:** Desviaciones ±5-15% respecto a TG-43

### 3. Productos de Análisis
- Curvas g(r) y F(r,θ) comparativas
- Mapas de isodosis 2D/3D
- DVHs para vejiga y recto
- Tablas de desviación relativa

## Análisis y Visualización

El script `analyze_results.py` proporciona:

```python
# Cargar datos
analyzer = TG43Analyzer("output/")
dose_data = analyzer.load_dose_distribution("dose_distribution.dat")

# Calcular parámetros TG-43
r, g_r = analyzer.calculate_radial_dose_function(dose_data)
r, theta, F_r_theta = analyzer.calculate_anisotropy_function(dose_data)

# Generar gráficos
analyzer.plot_radial_dose_function(r, g_r)
analyzer.plot_anisotropy_function(r, theta, F_r_theta)
analyzer.compare_with_literature(r, g_r)
```

## Ampliaciones Opcionales

1. **Otras fuentes:** Co-60, Cs-131
2. **Incertidumbres:** Movimiento de OARs (±5 mm)
3. **Métricas radiobiológicas:** BED, EQD2
4. **Geometrías complejas:** Datos DICOM reales
5. **Optimización:** Paralelización, GPU computing

## Métricas de Evaluación

### Precisión Dosimétrica
- Desviación respecto a literatura: <5% para TG-43
- Resolución espacial: <1 mm³
- Estadística mínima: >100 eventos/voxel

### Relevancia Clínica
- Diferencias >5% en OARs consideradas significativas
- D₂cc: Dosis al 2 cm³ más irradiado
- Análisis de incertidumbres geométricas

## Referencias

1. Rivard et al. (2004). "Update of AAPM Task Group No. 43 Report"
2. Perez-Calatayud et al. (2012). "Dose calculation for photon-emitting brachytherapy sources"
3. Geant4 Collaboration (2020). "Physics Reference Manual"

## Contacto y Soporte

Para preguntas técnicas o reportar problemas:
- Revisar documentación de Geant4
- Consultar ejemplos en `/path/to/geant4/examples/`
- Verificar configuración de física y geometría

---

**Nota:** Este proyecto está diseñado para fines académicos y de investigación. Para uso clínico, se requiere validación adicional y cumplimiento de normativas específicas.

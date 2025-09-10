# Proyecto de Evaluación de Heterogeneidades en Braquiterapia

## Estructura del Proyecto

```
/home/fer/fer/brachytherapy/
├── src/                    # Código fuente de Geant4
├── include/                # Archivos de cabecera de Geant4
├── build/                  # Directorio de compilación
├── macros/                 # Archivos .mac de configuración
├── output/                 # Archivos de salida (.out, .root)
├── analysis/               # Scripts de análisis (Python, ROOT)
├── results/                # Gráficos y visualizaciones
├── docs/                   # Documentación del proyecto
└── README_ESTRUCTURA.md    # Este archivo
```

## Descripción de Carpetas

### 📁 `macros/`
Contiene todos los archivos de configuración para las simulaciones:
- `FlexiSourceMacro.mac` - Configuración principal de la fuente Flexi
- `HeterogeneityMacro.mac` - Configuración para heterogeneidades
- `*_primary.mac` - Definiciones de radiación primaria
- `*_decay.mac` - Modelado de decaimiento radiactivo

### 📁 `output/`
Archivos generados por las simulaciones:
- `EnergyDeposition_*.out` - Datos de deposición de energía
- `*.root` - Histogramas y análisis ROOT
- `brachytherapy.root` - Histograma 2D principal
- `primary.root` - Espectro de energía de fotones

### 📁 `analysis/`
Scripts para procesamiento y análisis:
- `comparison_three_materials.py` - Análisis comparativo completo
- `simple_comparison.py` - Comparación básica hetero vs homo
- `*.C` - Scripts ROOT para análisis complementario

### 📁 `results/`
Visualizaciones generadas:
- `mapa_energia_*.png` - Mapas de deposición de energía
- `*_comparison.png` - Gráficos comparativos
- `*_analysis.png` - Análisis detallados

### 📁 `docs/`
Documentación del proyecto:
- Documentos LaTeX
- Reportes técnicos
- Presentaciones

## Uso de los Scripts

### Análisis Comparativo Completo
```bash
cd analysis/
python3 comparison_three_materials.py
```

### Análisis Simple
```bash
cd analysis/
python3 simple_comparison.py
```

### Análisis con ROOT
```bash
cd analysis/
root -l macro.C
```

## Archivos de Datos Principales

### Simulaciones MEGA (10M eventos)
- `EnergyDeposition_MEGA.out` - Phantom con hueso
- `EnergyDeposition_MEGA_Fat.out` - Phantom con tejido adiposo
- `EnergyDeposition_MEGA_Water.out` - Phantom homogéneo (agua)

### Resultados Principales
- **Hueso**: +0.484% energía total (+98.51% región heterogénea)
- **Tejido Adiposo**: -0.023% energía total (-3.83% región heterogénea)
- **Agua**: Referencia homogénea

## Configuración Experimental

- **Phantom**: 30×30×30 cm de agua
- **Heterogeneidad**: Cubo 6×6×6 cm en posición (0,6,0) cm
- **Fuente**: Ir-192 HDR en origen (0,0,0)
- **Scoring**: Mesh 2D, resolución 1 mm, cobertura ±16 cm
- **Estadística**: 10M eventos por simulación

## Materiales Evaluados

1. **G4_BONE_COMPACT_ICRU** (ρ ≈ 1.92 g/cm³)
2. **G4_ADIPOSE_TISSUE_ICRP** (ρ ≈ 0.95 g/cm³)
3. **G4_WATER** (ρ = 1.00 g/cm³) - Referencia

## Notas de Implementación

- Los scripts automáticamente buscan los archivos en las rutas relativas correctas
- Las rutas están configuradas para ejecutarse desde el directorio `analysis/`
- Las figuras se guardan automáticamente en `results/`
- Los datos de entrada se leen desde `output/`

## Próximos Pasos

1. Análisis de perfiles radiales
2. Estudio de efectos direccionales
3. Validación con datos experimentales
4. Extensión a otros materiales (pulmón, muscle)

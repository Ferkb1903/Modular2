# 🎯 GUÍA DE MACROS HDR BRACHYTHERAPY
# ===================================

## 📋 MACROS DISPONIBLES PARA SIMULACIÓN

### 🔬 **Macros Científicos (No solo agua)**

#### 1. `heterogeneous_full.mac` 
**Simulación con múltiples materiales anatómicos**
```bash
cd build
./hdr_brachy ../macros/heterogeneous_full.mac
```
- ✅ Hueso cortical (costillas)
- ✅ Cavidades aéreas (pulmón/intestino)
- ✅ Músculo esquelético
- ✅ Tejido adiposo
- ✅ OARs: Vejiga y Recto
- 🎯 10,000 eventos para estadística robusta

#### 2. `heterogeneity_study.mac`
**Análisis cuantitativo de efectos de heterogeneidades**
```bash
cd build  
./hdr_brachy ../macros/heterogeneity_study.mac
```
- 🔬 Cuantifica desviaciones del TG-43
- 📊 Mapea efectos de densidad de materiales
- 🎯 Evalúa impacto clínico real
- 📈 Alta resolución: 60×60×60 voxels

#### 3. `clinical_gyn.mac`
**Escenario clínico realista - Aplicador ginecológico**
```bash
cd build
./hdr_brachy ../macros/clinical_gyn.mac  
```
- 🏥 Anatomía pélvica femenina
- 🔧 Aplicador ring + tandem
- 📍 Múltiples posiciones de parada
- 🎯 Protocolo: 3 fracciones × 7 Gy

#### 4. `comparative_study.mac` ⭐ **RECOMENDADO**
**Estudio completo: TG-43 vs Heterogéneo vs Clínico**
```bash
cd build
./hdr_brachy ../macros/comparative_study.mac
```
- 📊 Ejecuta 3 escenarios en secuencia
- 🔬 42,000 eventos totales
- 📈 Análisis estadístico completo  
- 🎯 Justifica necesidad de Monte Carlo

### 🎬 **Macros de Visualización**

#### 5. `demo_heterogeneous.mac`
**Demostración visual interactiva - Todas las geometrías**
```bash
cd build
./hdr_brachy ../macros/demo_heterogeneous.mac
```
- 🎮 Ventana OpenGL 3D interactiva
- 🌈 Colores distintivos por material
- ⚡ Trayectorias de partículas visibles
- 🎯 Perfecto para presentaciones

#### 6. `vis.mac` 
**Visualización básica estándar**
```bash
cd build
./hdr_brachy ../macros/vis.mac
```
- 🔧 Configuración OpenGL básica
- 💧 Solo fantoma de agua (TG-43)
- 🎯 Ideal para validación inicial

### 📊 **Macros de Referencia**

#### 7. `run_tg43.mac`
**Simulación TG-43 estándar (solo agua)**
```bash
cd build
./hdr_brachy ../macros/run_tg43.mac
```
- 💧 Fantoma de agua pura infinita
- ✅ Validación protocolo TG-43
- 📈 Baseline para comparaciones

#### 8. `quick_test.mac`
**Prueba rápida del sistema**
```bash
cd build  
./hdr_brachy ../macros/quick_test.mac
```
- ⚡ 100 eventos para verificación
- 🔧 Test de funcionalidad
- 🎯 Depuración rápida

## 🚀 **FLUJO DE TRABAJO RECOMENDADO**

### Para **Investigación Científica**:
```bash
# 1. Validación inicial
./hdr_brachy ../macros/run_tg43.mac

# 2. Estudio comparativo completo  
./hdr_brachy ../macros/comparative_study.mac

# 3. Análisis de resultados
python3 ../scripts/analyze_heterogeneities.py
```

### Para **Visualización/Demostración**:
```bash
# 1. Demo interactiva
./hdr_brachy ../macros/demo_heterogeneous.mac

# 2. Comandos en la interfaz:
/run/beamOn 100
/vis/viewer/zoom 3
```

### Para **Validación Clínica**:
```bash
# 1. Escenario clínico
./hdr_brachy ../macros/clinical_gyn.mac

# 2. Análisis DVH 
python3 ../scripts/clinical_analysis.py
```

## 🎯 **¿Cuál Elegir?**

- **Solo quiero ver geometrías**: `demo_heterogeneous.mac`
- **Quiero datos científicos**: `comparative_study.mac` 
- **Necesito validar TG-43**: `run_tg43.mac`
- **Escenario clínico real**: `clinical_gyn.mac`
- **Análisis de materiales**: `heterogeneity_study.mac`

## 📊 **Outputs Esperados**

Cada macro genera:
- 📁 Archivos .txt con mapas 3D de dosis
- 📈 Datos para análisis estadístico
- 🎯 Métricas clínicas (DVH, OAR constraints)
- 📊 Comparaciones cuantitativas vs TG-43

¡Todos los macros están listos para usar! 🚀

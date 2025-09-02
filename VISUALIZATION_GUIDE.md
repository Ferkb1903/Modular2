# 🎬 Guía de Visualización HDR Brachytherapy

## 🚀 Opciones de Visualización Disponibles

### 1. Modo Interactivo Completo
```bash
./run_visualization.sh
```
- ✅ Interfaz gráfica completa
- ✅ Control manual de eventos
- ✅ Comandos interactivos en tiempo real
- ✅ Ideal para exploración y ajustes

### 2. Demostración Visual Automática
```bash
./demo_visual.sh
```
- ✅ Presentación paso a paso
- ✅ Eventos individuales visibles
- ✅ Explicaciones en tiempo real
- ✅ Ideal para presentaciones

### 3. Macros de Visualización Disponibles

#### `vis.mac` - Visualización básica OpenGL
- Vista wireframe estándar
- Configuración simple
- Buena para debugging

#### `vis_qt.mac` - Visualización avanzada Qt
- Interfaz gráfica completa
- Transparencias y colores
- Controles de cámara avanzados

#### `demo_visual.mac` - Demostración espectacular
- Eventos paso a paso
- Colores optimizados
- Información en pantalla

## 🎯 Características Visuales

### Colores de Partículas
- 🔵 **Rayos Gamma**: Azul (fotones del Ir-192)
- 🔴 **Electrones**: Rojo (secundarios Compton/fotoeléctrico)
- 🟢 **Positrones**: Verde (si hay producción de pares)
- 🟡 **Protones**: Amarillo (interacciones nucleares)

### Componentes del Detector
- 🟡 **Fuente Ir-192**: Amarillo brillante (cápsula)
- 🔴 **Núcleo activo**: Rojo (material radiactivo)
- 💧 **Fantoma de agua**: Azul transparente
- ⚫ **Mundo**: Invisible (para claridad)

### Controles de Vista
- **Zoom**: `/vis/viewer/zoom [factor]`
- **Rotación**: `/vis/viewer/set/viewpointVector [x y z]`
- **Estilo**: `/vis/viewer/set/style [wireframe/surface]`
- **Refresh**: `/vis/viewer/refresh`

## 🛠️ Comandos Útiles en Modo Interactivo

### Ejecutar Simulación
```
/run/beamOn 10        # 10 eventos
/run/beamOn 100       # 100 eventos
```

### Controlar Visualización
```
/vis/viewer/zoom 2.0              # Zoom x2
/vis/viewer/set/autoRefresh true  # Auto-actualizar
/vis/scene/add/trajectories       # Mostrar trayectorias
/vis/scene/add/hits              # Mostrar deposición
```

### Cambiar Vista
```
# Vista frontal
/vis/viewer/set/viewpointVector 0 -1 0

# Vista lateral
/vis/viewer/set/viewpointVector -1 0 0

# Vista isométrica
/vis/viewer/set/viewpointVector -1 -1 1
```

### Configurar Colores
```
/vis/geometry/set/colour [volume] 0 [R G B A]
/vis/modeling/trajectories/drawByParticleID-0/set [particle] [color]
```

## 📊 Información Física Mostrada

### En Pantalla
- Tipo de simulación (HDR Brachytherapy)
- Fuente utilizada (Ir-192)
- Energía promedio (0.38 MeV)
- Geometría del fantoma

### Trayectorias
- Caminos de fotones primarios
- Electrones de retroceso Compton
- Cascadas de ionización
- Deposición de energía (hits)

## 🔧 Resolución de Problemas

### Si no se abre la ventana gráfica:
1. Verificar que estás en un entorno con X11
2. Comprobar `echo $DISPLAY`
3. Instalar dependencias Qt si es necesario

### Si la visualización es lenta:
1. Reducir número de eventos
2. Usar modo wireframe en lugar de surface
3. Desactivar auto-refresh

### Si no se ven las trayectorias:
1. Verificar que `/vis/scene/add/trajectories` está activo
2. Comprobar que las partículas no son filtradas
3. Aumentar el tamaño de los pasos de visualización

## 🎯 Próximas Mejoras de Visualización

- [ ] Malla de dosimetría 3D
- [ ] Isodosis curves
- [ ] Scoring mesh visualization
- [ ] Anatomía realista (DICOM)
- [ ] Aplicadores clínicos 3D
- [ ] Análisis temporal de eventos

¡Disfruta explorando la física del HDR! 🚀

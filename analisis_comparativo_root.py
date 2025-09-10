import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# === CONFIGURACIÓN ===
# Nombres de los archivos ROOT (ajusta si es necesario)
file_agua = "build/20250910_074137_585_eDep.root"
file_hueso = "build/20250910_074851_813_eDep.root"

# Nombre del histograma dentro del archivo ROOT (ajusta si es necesario)
hist_name = None

# --- 1. Cargar los histogramas 2D ---
def load_histogram(filename):
    with uproot.open(filename) as f:
        # Buscar el primer histograma 2D
        for key in f.keys():
            obj = f[key]
            if hasattr(obj, 'values') and len(obj.values().shape) == 2:
                return obj.values(), obj.axes[0].edges(), obj.axes[1].edges(), key
    raise RuntimeError(f"No se encontró histograma 2D en {filename}")

# Cargar ambos histogramas
agua, x_edges, y_edges, hist_name_agua = load_histogram(file_agua)
hueso, _, _, hist_name_hueso = load_histogram(file_hueso)

# --- 2. Calcular diferencia porcentual ---
# Evitar división por cero
with np.errstate(divide='ignore', invalid='ignore'):
    diff_pct = 100 * (agua - hueso) / np.where(agua != 0, agua, np.nan)

# --- 3. Visualización mapas 2D ---
fig, axes = plt.subplots(1, 3, figsize=(21, 7))

extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]

im0 = axes[0].imshow(agua.T, origin='lower', extent=extent, aspect='equal', norm=LogNorm(vmin=1e-3, vmax=np.nanmax(agua)), cmap='viridis')
im1 = axes[1].imshow(hueso.T, origin='lower', extent=extent, aspect='equal', norm=LogNorm(vmin=1e-3, vmax=np.nanmax(hueso)), cmap='viridis')
im2 = axes[2].imshow(diff_pct.T, origin='lower', extent=extent, aspect='equal', cmap='bwr', vmin=-10, vmax=10)

axes[0].set_title('Agua homogénea')
axes[1].set_title('Hueso heterogéneo')
axes[2].set_title('Diferencia porcentual (%)\n[(agua-hueso)/agua]*100')
for ax in axes:
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label='Deposición (u.a.)')
plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04, label='Deposición (u.a.)')
plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04, label='% diferencia')
plt.tight_layout()
plt.savefig('comparacion_2d_root.png', dpi=300)

# --- 4. Comparación 1D vertical (perfil en X central) ---
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
y_centers = (y_edges[:-1] + y_edges[1:]) / 2
ix_central = np.abs(x_centers).argmin()  # índice más cercano a X=0

perfil_agua = agua[ix_central, :]
perfil_hueso = hueso[ix_central, :]
with np.errstate(divide='ignore', invalid='ignore'):
    perfil_diff_pct = 100 * (perfil_agua - perfil_hueso) / np.where(perfil_agua != 0, perfil_agua, np.nan)

fig2, ax2 = plt.subplots(figsize=(8,6))
ax2.plot(y_centers, perfil_agua, label='Agua homogénea', color='blue')
ax2.plot(y_centers, perfil_hueso, label='Hueso heterogéneo', color='red')
ax2.set_xlabel('Y (mm)')
ax2.set_ylabel('Deposición (u.a.)')
ax2.set_title('Perfil vertical (X=0)')
ax2.set_yscale('log')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('perfil_vertical_comparacion_root.png', dpi=300)
plt.show()

print('Listo: comparacion_2d_root.png y perfil_vertical_comparacion_root.png generados.')

import uproot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- 1. Inspeccionar y Cargar los Datos ---
try:
    with uproot.open("brachytherapy.root") as file:
        print("📂 Contenido del archivo ROOT:")
        for key in file.keys():
            obj = file[key]
            print(f"  • {key}: {type(obj).__name__}")
        
        # Buscar TTree o usar histogramas
        tree_keys = [k for k in file.keys() if 'TTree' in str(type(file[k]))]
        hist_keys = [k for k in file.keys() if 'TH' in str(type(file[k]))]
        
        if tree_keys:
            # Si hay TTree, usar el primero
            tree_name = tree_keys[0]
            print(f"\n✅ Usando TTree: {tree_name}")
            df = file[tree_name].arrays(library="pd")
            print("¡Archivo .root cargado exitosamente!")
            print(df.head())
        elif hist_keys:
            # Si hay histogramas, usar el primero 2D
            hist_name = hist_keys[0]
            print(f"\n✅ Usando histograma: {hist_name}")
            hist = file[hist_name]
            
            # Extraer datos del histograma
            values = hist.values()
            x_edges = hist.axes[0].edges()
            y_edges = hist.axes[1].edges()
            
            # Crear centros de bins
            x_centers = (x_edges[:-1] + x_edges[1:]) / 2
            y_centers = (y_edges[:-1] + y_edges[1:]) / 2
            
            # Convertir a DataFrame para análisis
            data_list = []
            for i in range(len(x_centers)):
                for j in range(len(y_centers)):
                    if values[i, j] > 0:
                        data_list.append({
                            'x': x_centers[i],
                            'y': y_centers[j], 
                            'z': 0.0,
                            'energia': values[i, j]
                        })
            
            df = pd.DataFrame(data_list)
            print("¡Histograma convertido a DataFrame!")
            print(df.head())
        else:
            raise ValueError("No se encontraron TTrees ni histogramas válidos en el archivo ROOT.")
            
except FileNotFoundError:
    print("Error: No se encontró el archivo 'brachytherapy.root'. Asegúrate de que la ruta es correcta.")
    exit()
except Exception as e:
    print(f"Error: {e}")
    exit()

# --- 2. Crear el Mapa de Calor 2D ---
z_corte = 0.0
df_plano_central = df[np.isclose(df['z'], z_corte)]

if not df_plano_central.empty:
    # Pivotea el DataFrame para crear una matriz 2D para el mapa de calor
    heatmap_data = df_plano_central.pivot_table(index='y', columns='x', values='energia')

    # Graficar el mapa de calor
    plt.figure(figsize=(10, 8))
    plt.imshow(heatmap_data, cmap='viridis', origin='lower',
               extent=[heatmap_data.columns.min(), heatmap_data.columns.max(),
                       heatmap_data.index.min(), heatmap_data.index.max()])
    plt.colorbar(label='Deposición de Energía (MeV)')
    plt.xlabel('X (mm)')
    plt.ylabel('Y (mm)')
    plt.title('Mapa 2D de Deposición de Energía (desde .root)')
    plt.savefig('heatmap_from_root.png')
    plt.show()
    print("\nGráfico guardado como 'heatmap_from_root.png'")
else:
    print(f"\nNo se encontraron datos para el plano Z={z_corte}. Revisa los datos de tu simulación.")

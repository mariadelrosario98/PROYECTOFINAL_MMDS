import networkx as nx

def calculate_global_measures(G):
    """
    Calcula las medidas globales clave para un grafo de NetworkX (G).
    """
    if G.number_of_nodes() == 0:
        print("❌ Error: El grafo está vacío. No se pueden calcular las métricas.")
        return

    print("\n--- CÁLCULO DE MEDIDAS GLOBALES ---")

    # 1. TAMAÑO (Size): Nodos (N) y Aristas (E)
    N = G.number_of_nodes()
    E = G.number_of_edges()
    print(f"1. Tamaño del Grafo Muestreado:")
    print(f"   - Nodos (N): {N:,}")
    print(f"   - Aristas (E): {E:,}")

    # 2. DENSIDAD (Density)
    # Para grafos dirigidos (DiGraph)
    density = nx.density(G)
    print(f"2. Densidad: {density:.6f} (Mide la conectividad general)")

    # 3. COEFICIENTE DE AGRUPAMIENTO PROMEDIO (Average Clustering Coefficient)
    # Mide la tendencia de los nodos a agruparse.
    # Usa 'clustering' para DiGraph, aunque se calcula sobre la versión no dirigida
    avg_clustering = nx.average_clustering(G) 
    print(f"3. Coeficiente de Agrupamiento Promedio: {avg_clustering:.4f}")

    # --- Medidas Basadas en Rutas (Diámetro y Longitud Media de Ruta) ---
    # NOTA CRÍTICA: Estas métricas solo se pueden calcular en el Componente Conexo Gigante (GCC)
    # y son computacionalmente costosas, incluso en el subgrafo.
    
    try:
        # Encontrar el Componente Conexo Gigante (GCC)
        # Usamos WCC (Weakly Connected Components) para grafos dirigidos.
        largest_cc = max(nx.weakly_connected_components(G), key=len)
        GCC = G.subgraph(largest_cc)

        # 4. LONGITUD MEDIA DE RUTA (Average Path Length)
        # Debe calcularse sobre un grafo fuertemente conectado, pero lo calculamos sobre el GCC
        # La función exige un grafo conexo, por eso usamos el GCC.
        avg_path_length = nx.average_shortest_path_length(GCC)
        print(f"4. Longitud Media de Ruta (en el Componente Gigante): {avg_path_length:.2f}")

        # 5. DIÁMETRO (Diameter)
        # La distancia más larga entre dos nodos.
        diameter = nx.diameter(GCC)
        print(f"5. Diámetro (en el Componente Gigante): {diameter:,}")
        
    except nx.NetworkXNoPath:
        print("4/5. La Longitud Media de Ruta y el Diámetro no se pueden calcular: el Componente Conexo Gigante no es lo suficientemente conexo.")
    except Exception as e:
        print(f"Error al calcular métricas basadas en rutas: {e}")
    
    print("---------------------------------------")

# Ejemplo de uso:
# G = nx.DiGraph() # Tu objeto grafo de NetworkX
# calculate_global_measures(G)
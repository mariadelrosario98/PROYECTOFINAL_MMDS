import asyncio
import aiofiles
import os
import networkx as nx
import random
import s3fs

# --- CONFIGURACIÓN DE S3 ---
# NOTA: Debes reemplazar estos valores con los que Terraform ha creado (ej. output 's3_file_url')
S3_BUCKET_NAME = "livejournal-data-mds-007ff415" 
S3_FILE_KEY = "raw/soc-LiveJournal1.txt"
SAMPLING_RATE = 10000 # Muestrea 1 de cada 10,000 aristas (ajusta este valor)

# La ruta completa que usará aiofiles (el valor de S3_BUCKET_NAME debe ser correcto)
S3_FILE_PATH = f"s3://{S3_BUCKET_NAME}/{S3_FILE_KEY}"


# --- FUNCIÓN DE CÁLCULO DE MEDIDAS (PLACEHOLDER) ---
# Aquí incluirías la función calculate_global_measures que definimos anteriormente
def calculate_global_measures(G):
    if G.number_of_nodes() == 0:
        print("❌ Error: El grafo muestreado está vacío.")
        return
    print("\n--- ANÁLISIS DEL GRAFO ---")
    print(f"1. Nodos: {G.number_of_nodes():,}")
    print(f"2. Aristas: {G.number_of_edges():,}")
    # ... (Aquí va la lógica completa de NetworkX)
    print("--------------------------")


async def read_large_file_async(s3_path, graph_object, sampling_rate):
    """
    Lee asíncronamente las aristas desde S3, las muestrea y las agrega al grafo.
    """
    try:
        print(f"✅ Iniciando muestreo asíncrono desde S3. Tasa: 1 en {sampling_rate}")
        
        # 1. Crea el sistema de archivos S3 ASÍNCRONO
        # NOTE: This instance is the one capable of handling the async operations
        fs = s3fs.S3FileSystem() # Use the synchronous S3FileSystem
        
        # The key change: Use 's3fs.open' which returns a file-like object that
        # can be read asynchronously without needing 'aiofiles.open' wrappers.
        async with fs.open(s3_path, mode="r", encoding="utf-8") as f:
            line_count = 0
            
            # Since fs.open is now an async file-like object, we can read lines directly
            async for line in f: 
                line_count += 1
                
                # Reporte de progreso
                if line_count % 1000000 == 0:
                    # Added a newline to prevent the progress bar from overwriting the final output
                    print(f"-> Líneas procesadas: {line_count / 1000000:.0f} millones") 
                
                # Saltamos metadatos
                if line.startswith('#'):
                    continue
                
                try:
                    parts = line.split()
                    
                    if len(parts) == 2:
                        from_node = int(parts[0])
                        to_node = int(parts[1])
                        
                        # Lógica de Muestreo
                        if random.randint(1, sampling_rate) == 1:
                            graph_object.add_edge(from_node, to_node)

                except ValueError:
                    pass
            
            # Mensaje final de la lectura asíncrona
            print("\n" + "="*50)
            print(f"✅ Muestreo de datos completado. Total líneas leídas: {line_count}")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la lectura de S3: {e}")

# --- FUNCIÓN PRINCIPAL (main) ---
def main():
    # 1. Crear el objeto NetworkX (Grafo Dirigido)
    G = nx.DiGraph() 

    # 2. Ejecutar la función asíncrona, pasándole el objeto NetworkX
    asyncio.run(read_large_file_async(S3_FILE_PATH, G, SAMPLING_RATE))
    
    # 3. Analizar el grafo una vez que la lectura asíncrona termine
    calculate_global_measures(G)


if __name__ == "__main__":
    main()
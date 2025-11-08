# indicators.py
import time
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, lit
# Importar GraphFrame. Esto fallará si no se usa --packages/--py-files correctamente.
try:
    from graphframes import GraphFrame
except ImportError:
    print("--- ERROR: GraphFrames library not found ---")
    print("Por favor, asegúrese de usar el comando spark-submit CON los argumentos --packages y --py-files correctos.")
    sys.exit(1)


def calculate_graph_metrics(spark):
    """Calcula métricas de grafo sobre el dataset de LiveJournal cargado desde S3."""
    
    # ==========================================================
    # 0. SETUP AND DATA LOADING (CARGA DESDE S3)
    # ==========================================================
    
    S3_PATH = "s3://livejournal-data-mds-007ff415/raw/soc-LiveJournal1.txt"
    
    print(f"--- 0. Cargando datos desde S3: {S3_PATH} ---")
    
    # Leer el archivo de aristas desde S3
    # El archivo contiene pares de IDs de nodo (espacio separado)
    # Usamos RDDs para leer el archivo de texto y luego convertirlo a DataFrame
    edges_rdd = spark.sparkContext.textFile(S3_PATH)
    
    # Mapear el RDD a un DataFrame de aristas (src, dst)
    edges = edges_rdd.map(lambda line: line.split()) \
                     .filter(lambda parts: len(parts) == 2) \
                     .toDF(["src", "dst"])
    
    # Crear un DataFrame de nodos únicos (vértices)
    # Se obtienen todos los IDs únicos de las columnas src y dst
    vertices = edges.select(col("src").alias("id")) \
                    .union(edges.select(col("dst").alias("id"))) \
                    .distinct()
    
    # Crear el GraphFrame
    g = GraphFrame(vertices, edges)
    print("--- Grafo creado exitosamente desde S3 ---")


    # ==========================================================
    # 1. 📏 Métricas a Nivel Global (Estructura General)
    # ==========================================================
    print("\n--- 1. Métricas Globales ---")
    
    # 1.1 Número de Nodos (|V|) y Aristas (|E|)
    num_nodes = g.vertices.count()
    num_edges = g.edges.count()
    print(f"|V| (Número de Nodos): {num_nodes}")
    print(f"|E| (Número de Aristas): {num_edges}")
    
    # 1.2 Densidad del Grafo (Density)
    # Fórmula: 2|E| / |V| * (|V| - 1)
    if num_nodes > 1:
        # Nota: Usamos float() para asegurar la división
        max_possible_edges = num_nodes * (num_nodes - 1)
        density = (2 * num_edges) / max_possible_edges
        print(f"Densidad del Grafo: {density}")
    else:
        print("Densidad: 0 (Requiere > 1 nodo)")
        
    # 1.3 Coeficiente de Clustering Promedio
    # GraphFrames calcula el coeficiente de clustering local
    results_cc = g.clusteringCoefficient()
    avg_cc = results_cc.selectExpr("avg(clusteringCoefficient)").collect()[0][0]
    print(f"Coeficiente de Clustering Promedio: {avg_cc}")
    
    # 1.4 Diámetro y Centralidades (Intermediación, Cercanía)
    print("Diámetro, Intermediación y Cercanía: [Omitidas por la alta complejidad computacional en grafos muy grandes]")


    # ==========================================================
    # 2. 👑 Métricas de Centralidad (Influencia y Rol del Nodo)
    # ==========================================================
    print("\n--- 2. Métricas de Centralidad ---")
    
    # 2.1 Grado (Degree Centrality)
    total_degree = g.degrees.withColumnRenamed("degree", "Degree_Total")
    
    print("Distribución y Top 10 Nodos por Grado Total:")
    total_degree.sort(col("Degree_Total").desc()).show(10)

    # 2.2 PageRank (Proxy para Eigenvector Centrality)
    # Usamos 10 iteraciones, lo cual es estándar
    pr_result = g.pageRank(resetProbability=0.15, maxIter=10)
    
    print("Top 10 Nodos por PageRank (Influencia):")
    pr_result.vertices.select("id", "pagerank").sort(col("pagerank").desc()).show(10)


    # ==========================================================
    # 3. 🏘️ Métricas de Detección de Comunidades
    # ==========================================================
    print("\n--- 3. Métricas de Detección de Comunidades ---")

    # 3.1 Componentes Conectados (Connected Components)
    # Identifica subgrafos donde existe un camino entre todos sus pares de nodos.
    result_cc = g.connectedComponents()
    num_cc = result_cc.select("component").distinct().count()
    print(f"Número de Componentes Conectados (Total de Clusters): {num_cc}")
    
    # 3.2 Modularidad
    # Requiere un algoritmo de detección de comunidades (ej. Label Propagation)
    print("Modularidad: [Requiere correr un algoritmo de detección de comunidades (ej. LPA) primero]")
    
    
    # ==========================================================
    # 4. 🧮 Métricas de Distribución
    # ==========================================================
    print("\n--- 4. Métricas de Distribución ---")
    
    # 4.1 Distribución de Grado
    # Frecuencia de cada valor de grado
    degree_distribution = total_degree.groupBy("Degree_Total").agg(count("*").alias("Node_Count"))
    degree_distribution = degree_distribution.withColumn(
        "Frequency", col("Node_Count") / num_nodes
    ).sort("Degree_Total")
    
    print("Distribución de Grado (Valores de Grado y Frecuencia):")
    degree_distribution.show()

# ==========================================================
# 5. Medir Tiempo de Ejecución, RAM, Procesador
# ==========================================================
if __name__ == "__main__":
    start_time = time.time()
    
    # Inicializar Spark Session
    spark = SparkSession.builder.appName("GraphMetricsLiveJournal") \
        .getOrCreate()
    
    try:
        calculate_graph_metrics(spark)
    except Exception as e:
        print(f"--- ERROR FATAL EN TIEMPO DE EJECUCIÓN ---")
        print(f"Mensaje de error: {e}")
    finally:
        # Detener la sesión de Spark y medir el tiempo
        spark.stop()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        print("\n==========================================================")
        print("5. Reporte de Recursos y Tiempo")
        print("==========================================================")
        print(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")
        print("Uso de RAM/CPU/Procesador:")
        print("  - Monitorear a través de la interfaz web de Spark (puerto 4040) o herramientas del sistema (ej. htop).")
        print("==========================================================")
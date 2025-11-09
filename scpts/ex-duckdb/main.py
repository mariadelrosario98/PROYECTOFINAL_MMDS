# -*- coding: utf-8 -*-
"""
Análisis de Grafo con DuckDB: Centralidad de Grado, Grado Medio, Matriz de Adyacencia, 
Modularidad (aproximada) y Componentes Conectados (simulado).
- Lee un archivo de aristas (edges) con columnas 'source' y 'target'.
- Calcula métricas clave de grafos usando SQL.

Uso:
  python3 main.py --edges /ruta/a/archivo_de_aristas.csv
"""

import argparse
import os
import sys
import time
import duckdb

def run(edges_file: str) -> None:
    t0 = time.time()

    if not os.path.exists(edges_file):
        print(f"[duckdb] ERROR: '{edges_file}' no es un archivo válido.", file=sys.stderr)
        sys.exit(1)

    con = duckdb.connect(database=":memory:")
    
    try:
        # --- 1. Cargar datos de aristas y Nodos Únicos ---
        con.execute(f"""
            CREATE OR REPLACE TABLE edges AS
            SELECT * FROM read_csv_auto('{edges_file}');
        """)

        # Obtener todos los nodos únicos
        con.execute("""
            CREATE OR REPLACE TEMP TABLE nodes AS
            SELECT source AS node FROM edges
            UNION SELECT target AS node FROM edges;
        """)

        # --- 2. Centralidad de Grado y Distribución ---
        degree_sql = """
        WITH all_nodes AS (
          SELECT source AS node FROM edges
          UNION ALL
          SELECT target AS node FROM edges
        ),
        node_degrees AS (
          SELECT
            node,
            COUNT(*) AS degree
          FROM all_nodes
          GROUP BY node
        )
        SELECT * FROM node_degrees ORDER BY degree DESC;
        """
        degree_df = con.execute(degree_sql).df()
        
        # --- 3. Grado Medio ---
        avg_degree_sql = """
        SELECT AVG(degree) AS average_degree
        FROM (
          SELECT
            node,
            COUNT(*) AS degree
          FROM (
            SELECT source AS node FROM edges
            UNION ALL
            SELECT target AS node FROM edges
          )
          GROUP BY node
        );
        """
        avg_degree_result = con.execute(avg_degree_sql).fetchone()
        avg_degree = avg_degree_result[0] if avg_degree_result else 0.0

        # --- 4. Matriz de Adyacencia (Subconjunto) ---
        adjacency_matrix_sql = """
        WITH top_nodes AS (
            SELECT node FROM nodes
            ORDER BY node
            LIMIT 10 -- Limitar para evitar matrices gigantes
        ),
        pivoted AS (
            SELECT 
                source,
                target,
                1 AS connection
            FROM edges
            WHERE source IN (SELECT node FROM top_nodes)
              AND target IN (SELECT node FROM top_nodes)
        )
        PIVOT pivoted ON target IN (SELECT node FROM top_nodes)
        USING SUM(connection)
        ORDER BY source;
        """
        adjacency_df = con.execute(adjacency_matrix_sql).df()

        # --- 5. Modularidad (Aproximación de Densidad) ---
        # Modularidad es compleja. Aquí calculamos la densidad general 
        # (E / (N * (N-1))) como proxy de cohesión.
        modularidad_sql = """
        SELECT
            COUNT(DISTINCT source) + COUNT(DISTINCT target) AS num_nodes,
            COUNT(*) AS num_edges
        FROM edges;
        """
        mod_result = con.execute(modularidad_sql).fetchone()
        N = con.execute("SELECT COUNT(*) FROM nodes;").fetchone()[0]
        E = mod_result[1] if mod_result else 0
        
        # Densidad = E / (N * (N-1))
        # Si N=1 o N=0, la densidad es 0 para evitar división por cero.
        density = E / (N * (N - 1)) if N > 1 else 0.0

        # --- 6. Componentes Conectados (Nodos Aislados vs. Conectados) ---
        # Sin recursividad, la mejor aproximación es identificar y contar nodos aislados.
        isolated_nodes_sql = """
        SELECT COUNT(t1.node) AS isolated_count
        FROM nodes t1
        LEFT JOIN (
            SELECT node, degree 
            FROM (
                SELECT source AS node FROM edges UNION ALL SELECT target AS node FROM edges
            ) 
            GROUP BY node
        ) t2 ON t1.node = t2.node
        WHERE t2.degree IS NULL OR t2.degree = 0;
        """
        isolated_count = con.execute(isolated_nodes_sql).fetchone()[0]
        
        connected_count = N - isolated_count
        
    except duckdb.IOException as e:
        print(f"[duckdb] ERROR de lectura del archivo de aristas ({edges_file}): {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[duckdb] ERROR ejecutando consulta: {e}", file=sys.stderr)
        sys.exit(3)
    finally:
        con.close()

    elapsed = time.time() - t0

    # --- Salida de Resultados ---
    print(f"Execution time: {elapsed:.6f} seconds")
    print("\n" + "=" * 60)
    print("## 1. Centralidad de Grado (Distribución de Grados)")
    print("=" * 60)
    if not degree_df.empty:
        print(degree_df.to_string(index=False))
    else:
        print("No se encontraron nodos.")
        
    print("\n" + "-" * 60)
    
    print("## 2. Grado Medio de la Red")
    print("-" * 60)
    print(f"Grado Medio: {avg_degree:.4f}")
    
    print("\n" + "-" * 60)

    print("## 3. Modularidad (Aproximación de Densidad) 🧪")
    print("*" * 60)
    print(f"Nodos Totales (N): {N}")
    print(f"Aristas Totales (E): {E}")
    print(f"Densidad de Aristas (E / N(N-1)): {density:.6f} (Proxy de Modularidad)")
    print("> NOTA: La modularidad real requiere algoritmos de detección de comunidades no disponibles en SQL puro.")
    
    print("\n" + "-" * 60)
    
    print("## 4. Componentes Conectados (Simulación Nodos Aislados)")
    print("*" * 60)
    print(f"Nodos Totales (N): {N}")
    print(f"Nodos Aislados (Grado 0): {isolated_count}")
    print(f"Nodos Conectados (Grado > 0): {connected_count}")
    print(f"Componente Simulado: {connected_count} conectados + {isolated_count} componentes de 1 nodo.")
    
    print("\n" + "-" * 60)
    
    print("## 5. Matriz de Adyacencia (Subconjunto - Primeros 10 Nodos)")
    print("-" * 60)
    if not adjacency_df.empty:
        adjacency_df = adjacency_df.fillna(0) 
        print(adjacency_df.to_string(index=False))
    else:
        print("No se pudo generar la Matriz de Adyacencia.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", required=True, help="Ruta al archivo (CSV, Parquet, etc.) con columnas 'source' y 'target'")
    args = ap.parse_args()
    run(args.edges)

if __name__ == "__main__":
    main()
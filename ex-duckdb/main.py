#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Grafo con DuckDB: Centralidad de Grado, Grado Medio y Matriz de Adyacencia.
- Lee un archivo de aristas (edges) con columnas 'source' y 'target'.
- Calcula el grado de cada nodo, el grado medio y la matriz de adyacencia.

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

    # Validaciones básicas
    if not os.path.exists(edges_file):
        print(f"[duckdb] ERROR: '{edges_file}' no es un archivo válido.", file=sys.stderr)
        sys.exit(1)

    # Conexión a DuckDB en memoria
    con = duckdb.connect(database=":memory:")
    
    try:
        # --- 1. Cargar datos de aristas ---
        # Asume que el archivo tiene columnas 'source' y 'target'
        con.execute(f"""
            CREATE OR REPLACE TABLE edges AS
            SELECT * FROM read_csv_auto('{edges_file}');
        """)

        # --- 2. Centralidad de Grado, Grado Medio y Distribución de Grados ---

        # 2a. Grado de cada nodo (Degree Centrality)
        # Calcula el grado (in-degree + out-degree) de cada nodo.
        # Asume un grafo no dirigido (contamos aristas entrantes y salientes).
        # Para un grafo dirigido, separamos in_degree y out_degree.
        degree_sql = """
        WITH all_nodes AS (
          -- Combina nodos origen y destino para obtener todos los nodos únicos
          SELECT source AS node FROM edges
          UNION ALL
          SELECT target AS node FROM edges
        ),
        node_degrees AS (
          -- Cuenta la frecuencia de cada nodo (su grado)
          SELECT
            node,
            COUNT(*) AS degree
          FROM all_nodes
          GROUP BY node
        )
        SELECT * FROM node_degrees ORDER BY degree DESC;
        """
        degree_df = con.execute(degree_sql).df()
        
        # 2b. Grado Medio (Average Degree)
        # Suma de grados dividido por el número total de nodos únicos.
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

        # --- 3. Matriz de Adyacencia (Representación en tabla pivote) ---
        # Esto genera una matriz donde la fila es 'source', la columna es 'target' 
        # y el valor es 1 (si hay conexión) o 0 (si no).
        # Limitamos la matriz a los primeros 10 nodos para que sea manejable.
        adjacency_matrix_sql = """
        WITH top_nodes AS (
            SELECT DISTINCT source AS node FROM edges
            UNION SELECT DISTINCT target AS node FROM edges
            ORDER BY node
            LIMIT 10 -- Limitar para manejar el pivote
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

    except duckdb.IOException as e:
        print(f"[duckdb] ERROR de lectura del archivo de aristas ({edges_file}): {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[duckdb] ERROR ejecutando consulta: {e}", file=sys.stderr)
        sys.exit(3)
    finally:
        con.close()

    elapsed = time.time() - t0

    # --- Resultados ---
    print(f"Execution time: {elapsed:.6f} seconds")
    print("-" * 50)
    
    ## Centralidad de Grado y Distribución
    print("## 1. Centralidad de Grado (Distribución de Grados)")
    if not degree_df.empty:
        print(degree_df.to_string(index=False))
    else:
        print("No se encontraron nodos.")
        
    print("-" * 50)
    
    ## Grado Medio
    print("## 2. Grado Medio de la Red")
    print(f"Grado Medio: {avg_degree:.4f}")
    
    print("-" * 50)
    
    ## Matriz de Adyacencia (Subconjunto)
    print("## 3. Matriz de Adyacencia (Primeros 10 Nodos)")
    if not adjacency_df.empty:
        # Reemplazar valores nulos (sin conexión) por 0
        adjacency_df = adjacency_df.fillna(0) 
        print(adjacency_df.to_string(index=False))
    else:
        print("No se pudieron generar la Matriz de Adyacencia.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", required=True, help="Ruta al archivo (CSV, Parquet, etc.) con columnas 'source' y 'target'")
    args = ap.parse_args()
    run(args.edges)

if __name__ == "__main__":
    main()

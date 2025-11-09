import io
import time
import boto3
import polars as pl
from collections import defaultdict, deque
import random

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
BUCKET = "livejournal-data-mds-007ff415"
KEY = "raw/soc-LiveJournal1.txt"
SAMPLE_PAGERANK_EDGES = 100_000  # edges for PageRank sample
CHUNK_SIZE = 1_000_000           # process 1M lines at a time

# ==========================================================
# INICIALIZACIÓN
# ==========================================================
start_time = time.time()
print(f"--- Reading s3://{BUCKET}/{KEY} in Polars (chunked mode) ---")

s3 = boto3.client("s3")
obj = s3.get_object(Bucket=BUCKET, Key=KEY)
body = obj["Body"]

in_degree = defaultdict(int)
out_degree = defaultdict(int)
edges_total = 0
rows_buffer = []

# ==========================================================
# 1️⃣ PROCESAMIENTO POR BLOQUES (CHUNKS)
# ==========================================================
for raw_line in body.iter_lines():
    if not raw_line or raw_line.startswith(b"#"):
        continue
    try:
        src, dst = raw_line.decode("utf-8").strip().split()
        rows_buffer.append((src, dst))
    except Exception:
        continue

    # Procesar cada bloque de 1M líneas
    if len(rows_buffer) >= CHUNK_SIZE:
        df = pl.DataFrame(rows_buffer, schema=["src", "dst"])
        in_counts = df.groupby("dst").count().to_dict(as_series=False)
        out_counts = df.groupby("src").count().to_dict(as_series=False)
        for n, c in zip(in_counts["dst"], in_counts["count"]):
            in_degree[n] += c
        for n, c in zip(out_counts["src"], out_counts["count"]):
            out_degree[n] += c
        edges_total += len(rows_buffer)
        print(f"  → processed {edges_total:,} edges")
        rows_buffer = []

# Último bloque si queda algo
if rows_buffer:
    df = pl.DataFrame(rows_buffer, schema=["src", "dst"])
    in_counts = df.groupby("dst").count().to_dict(as_series=False)
    out_counts = df.groupby("src").count().to_dict(as_series=False)
    for n, c in zip(in_counts["dst"], in_counts["count"]):
        in_degree[n] += c
    for n, c in zip(out_counts["src"], out_counts["count"]):
        out_degree[n] += c
    edges_total += len(rows_buffer)

# ==========================================================
# 2️⃣ MÉTRICAS GLOBALES
# ==========================================================
nodes = set(in_degree) | set(out_degree)
num_nodes = len(nodes)
num_edges = edges_total
density = (2 * num_edges) / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0

print("\n--- MÉTRICAS GLOBALES ---")
print(f"|V| (nodes): {num_nodes:,}")
print(f"|E| (edges): {num_edges:,}")
print(f"Density: {density:.10f}")

# ==========================================================
# 3️⃣ TOP 10 NODOS POR GRADO TOTAL
# ==========================================================
degree_total = {n: in_degree.get(n, 0) + out_degree.get(n, 0) for n in nodes}
top10 = sorted(degree_total.items(), key=lambda x: x[1], reverse=True)[:10]

print("\n--- TOP 10 NODES BY TOTAL DEGREE ---")
for n, d in top10:
    print(f"Node {n}: degree={d}, in={in_degree.get(n,0)}, out={out_degree.get(n,0)}")

# ==========================================================
# 4️⃣ CONECTED COMPONENTS (APROXIMADO)
# ==========================================================
print("\n--- Connected Components (approx via BFS, sampled) ---")
sample_nodes = set(random.sample(list(nodes), min(100_000, num_nodes)))

# Construimos grafo reducido
edges_sample = []
obj = s3.get_object(Bucket=BUCKET, Key=KEY)
for raw_line in obj["Body"].iter_lines():
    if not raw_line or raw_line.startswith(b"#"):
        continue
    try:
        src, dst = raw_line.decode("utf-8").strip().split()
        if src in sample_nodes and dst in sample_nodes:
            edges_sample.append((src, dst))
    except Exception:
        continue

adj_undirected = defaultdict(list)
for s, d in edges_sample:
    adj_undirected[s].append(d)
    adj_undirected[d].append(s)

visited = set()
components = 0
for node in sample_nodes:
    if node in visited:
        continue
    components += 1
    queue = deque([node])
    while queue:
        n = queue.popleft()
        if n in visited:
            continue
        visited.add(n)
        for neighbor in adj_undirected[n]:
            if neighbor not in visited:
                queue.append(neighbor)

print(f"Approx. connected components in sample: {components:,}")

# ==========================================================
# 5️⃣ DEGREE DISTRIBUTION
# ==========================================================
print("\n--- Degree Distribution ---")
degree_freq = defaultdict(int)
for d in degree_total.values():
    degree_freq[d] += 1

for deg, count in sorted(degree_freq.items())[:15]:
    freq = count / num_nodes
    print(f"Degree={deg:3d} | Nodes={count:7d} | Freq={freq:.8f}")

# ==========================================================
# 6️⃣ SIMPLIFIED PAGERANK
# ==========================================================
print("\n--- PageRank (sampled 100K edges) ---")
pagerank_edges = random.sample(edges_sample, min(SAMPLE_PAGERANK_EDGES, len(edges_sample)))
outgoing = defaultdict(list)
for s, d in pagerank_edges:
    outgoing[s].append(d)

pr_nodes = list(set([s for s, _ in pagerank_edges] + [d for _, d in pagerank_edges]))
N = len(pr_nodes)
pagerank = {n: 1.0 / N for n in pr_nodes}
damping = 0.85

for i in range(5):
    new_pr = {n: (1 - damping) / N for n in pr_nodes}
    for s, outs in outgoing.items():
        if not outs:
            continue
        share = pagerank[s] / len(outs)
        for d_ in outs:
            new_pr[d_] += damping * share
    pagerank = new_pr
    print(f"  Iteration {i+1} complete")

top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 nodes by sampled PageRank:")
for n, pr in top_pr:
    print(f"Node {n}: PageRank={pr:.6f}")

# ==========================================================
# 7️⃣ REPORTE FINAL
# ==========================================================
elapsed = time.time() - start_time
print("\n==========================================================")
print("FINAL REPORT (POLARS FULL)")
print("==========================================================")
print(f"|V|: {num_nodes:,}")
print(f"|E|: {num_edges:,}")
print(f"Density: {density:.10e}")
print(f"Connected components (sample): {components:,}")
print(f"Total execution time: {elapsed:.2f} seconds")
print("==========================================================")

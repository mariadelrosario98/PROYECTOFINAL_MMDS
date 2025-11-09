import boto3
import time
from collections import defaultdict, deque
import random

# ==========================================================
# CONFIGURATION
# ==========================================================
BUCKET = "livejournal-data-mds-007ff415"
KEY = "raw/soc-LiveJournal1.txt"

# ==========================================================
# 0. LOAD DATA FROM S3
# ==========================================================
print(f"--- Loading graph from S3: s3://{BUCKET}/{KEY} ---")
start_time = time.time()

s3 = boto3.client("s3")
obj = s3.get_object(Bucket=BUCKET, Key=KEY)
body = obj["Body"]

in_degree = defaultdict(int)
out_degree = defaultdict(int)
edges = 0

for raw_line in body.iter_lines():
    if not raw_line or raw_line.startswith(b"#"):
        continue
    try:
        src, dst = raw_line.decode("utf-8").strip().split()
        out_degree[src] += 1
        in_degree[dst] += 1
        edges += 1
    except Exception:
        continue

nodes = set(in_degree) | set(out_degree)
num_nodes = len(nodes)
num_edges = edges

print(f"|V| = {num_nodes:,} nodes")
print(f"|E| = {num_edges:,} edges")

# ==========================================================
# 1. GLOBAL METRICS
# ==========================================================
print("\n--- 1. Global Metrics ---")
density = (2 * num_edges) / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0
print(f"Density: {density:.10f}")

# ==========================================================
# 2. CENTRALITY METRICS
# ==========================================================
print("\n--- 2. Centrality Metrics ---")

degree_total = {n: in_degree.get(n, 0) + out_degree.get(n, 0) for n in nodes}
top_degree = sorted(degree_total.items(), key=lambda x: x[1], reverse=True)[:10]

print("Top 10 nodes by total degree:")
for n, d in top_degree:
    print(f"Node {n}: degree={d}, in={in_degree.get(n,0)}, out={out_degree.get(n,0)}")

# ==========================================================
# 3. PAGE RANK (SAMPLED)
# ==========================================================
print("\n--- 3. PageRank on Sampled Subgraph (100,000 nodes) ---")
sample_size = 100_000
sample_nodes = set(random.sample(list(nodes), min(sample_size, num_nodes)))
pagerank = {n: 1.0 / len(sample_nodes) for n in sample_nodes}
damping = 0.85

# Build adjacency list only for sampled nodes
adj = defaultdict(list)
obj = s3.get_object(Bucket=BUCKET, Key=KEY)
for raw_line in obj["Body"].iter_lines():
    if not raw_line or raw_line.startswith(b"#"):
        continue
    try:
        src, dst = raw_line.decode("utf-8").strip().split()
        if src in sample_nodes and dst in sample_nodes:
            adj[src].append(dst)
    except Exception:
        continue

# Run PageRank iterations
for i in range(5):
    new_rank = {n: (1 - damping) / len(sample_nodes) for n in sample_nodes}
    for node, targets in adj.items():
        if not targets:
            continue
        share = pagerank[node] / len(targets)
        for tgt in targets:
            new_rank[tgt] += damping * share
    pagerank = new_rank
    print(f"  Iteration {i+1} complete")

top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 nodes by sampled PageRank:")
for n, pr in top_pagerank:
    print(f"Node {n}: PageRank={pr:.6f}")

# ==========================================================
# 4. CONNECTED COMPONENTS (APPROX)
# ==========================================================
print("\n--- 4. Connected Components (Approximation via BFS) ---")
visited = set()
components = 0
adj_undirected = defaultdict(list)
for src, targets in adj.items():
    for tgt in targets:
        adj_undirected[src].append(tgt)
        adj_undirected[tgt].append(src)

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

print(f"Approximate connected components in sampled graph: {components}")

# ==========================================================
# 5. DEGREE DISTRIBUTION
# ==========================================================
print("\n--- 5. Degree Distribution ---")
degree_freq = defaultdict(int)
for d in degree_total.values():
    degree_freq[d] += 1

for deg, count in sorted(degree_freq.items())[:15]:
    freq = count / num_nodes
    print(f"Degree={deg:3d} | Nodes={count:6d} | Frequency={freq:.8f}")

# ==========================================================
# 6. PERFORMANCE REPORT
# ==========================================================
elapsed = time.time() - start_time
print("\n==========================================================")
print("6. Resource and Time Report")
print("==========================================================")
print(f"Total execution time: {elapsed:.2f} seconds")
print("==========================================================")

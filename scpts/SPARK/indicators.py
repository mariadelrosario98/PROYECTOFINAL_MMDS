pyspark --packages graphframes:graphframes:0.8.2-spark3.5-s_2.12

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from graphframes import *

# The S3 path to your data
DATA_PATH = "s3a://livejournal-data-mds-007ff415/raw/"

# --- 1. Load Edges (Aristas) ---
# Assuming the files are space-separated (typical for graph datasets)
print("Loading edge data from S3...")
edges_df = spark.read.text(DATA_PATH).withColumnRenamed("value", "line")

# The data format is typically "user_id_source user_id_destination"
# We split the line, clean it, and cast IDs to String (or Long, if preferred)
edges_df = edges_df.selectExpr("split(line, ' ') as columns") \
                   .select(col("columns")[0].alias("src_raw"), 
                           col("columns")[1].alias("dst_raw")) \
                   .withColumn("src", col("src_raw").cast("string")) \
                   .withColumn("dst", col("dst_raw").cast("string")) \
                   .drop("src_raw", "dst_raw") \
                   .filter("src IS NOT NULL AND dst IS NOT NULL") # Clean up any bad rows

# Check the first few edges
print("Edges DataFrame loaded and cleaned:")
edges_df.show(5)

# --- 2. Create Nodes (Vertices) ---
# Nodes are the unique set of all 'src' and 'dst' IDs in the edges DataFrame.
print("Creating Vertices DataFrame...")
sources = edges_df.select(col("src").alias("id"))
destinations = edges_df.select(col("dst").alias("id"))

# Combine sources and destinations and find unique IDs
vertices_df = sources.union(destinations).distinct()

# Check the first few vertices
print("Vertices DataFrame created:")
vertices_df.show(5)

# --- 3. Create the GraphFrame ---
g = GraphFrame(vertices_df, edges_df)

print(f"\nGraph created with {g.vertices.count()} Nodes and {g.edges.count()} Edges.")
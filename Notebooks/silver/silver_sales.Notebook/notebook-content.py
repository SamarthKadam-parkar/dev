# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# ## **Pre-processing and cleaning products table**


# CELL ********************

from pyspark.sql import functions as F 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

TARGET_TABLE = 'products'
SOURCE_LAKEHOUSE = 'bronze'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = spark.read.table(f"{SOURCE_LAKEHOUSE}.products")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = (products
.withColumn("ProductName",F.upper(F.col("ProductName")))
.withColumn("Category",F.upper(F.col("Category")))
.select(
    F.col("ProductID").alias("PRODUCT_ID"),
    F.col("ProductName").alias("PRODUCT_NAME"),
    F.col("Category").alias("CATEGORY"),
    F.col("Price").alias("PRICE")
)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products.write\
.format('delta')\
.mode('overwrite')\
.saveAsTable(f"{TARGET_TABLE}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

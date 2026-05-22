# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "b09a12ed-928e-4d44-80c2-556c1a743dcd",
# META       "default_lakehouse_name": "silver",
# META       "default_lakehouse_workspace_id": "fd090d74-08b5-4348-89a8-15d1280f84b3",
# META       "known_lakehouses": [
# META         {
# META           "id": "11097028-1ac9-4f23-8c36-f279b0a66988"
# META         },
# META         {
# META           "id": "b09a12ed-928e-4d44-80c2-556c1a743dcd"
# META         }
# META       ]
# META     }
# META   }
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
SOURCE_LAKEHOUSE = 'bronze'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = spark.read.table(f"{SOURCE_LAKEHOUSE}.products")
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
.withColumn("ProductName",F.upper(F.col("ProductName")))
.withColumn("Category",F.upper(F.col("Category")))
.select(
    F.col("ProductID").alias("PRODUCT_ID"),
    F.col("ProductName").alias("PRODUCT_NAME"),
    F.col("Category").alias("CATEGORY"),
    F.col("Price").alias("PRICE")
)
)
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
.mode('overwrite')\
.saveAsTable(f"{TARGET_TABLE}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Edited by skadam

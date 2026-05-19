# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "11097028-1ac9-4f23-8c36-f279b0a66988",
# META       "default_lakehouse_name": "bronze",
# META       "default_lakehouse_workspace_id": "fd090d74-08b5-4348-89a8-15d1280f84b3",
# META       "known_lakehouses": [
# META         {
# META           "id": "11097028-1ac9-4f23-8c36-f279b0a66988"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# ## **Pre-processing of sales table**


# CELL ********************

from pyspark.sql import functions as F 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = spark.read.table("bronze.products")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(products)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = products.select(
    F.col("ProductID"),
    F.col("ProductName"),
    F.col("Category"),
    F.col("Price").alias("PRICE"),
)
display(products)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

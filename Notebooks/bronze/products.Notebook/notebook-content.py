# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql import functions as F

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

workspace_id = spark.conf.get("trident.workspace.id")
print("Workspace ID:", workspace_id)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products = spark.read.format('csv').option('header','true').option('inferschema','true').load('Files/products.csv')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

products.write.format('delta').saveAsTable('bronze.products')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import os
from azure.identity import ClientSecretCredential
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items,
   get_changed_items,
   append_feature_flag,
)
from dotenv import load_dotenv
load_dotenv()

append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")

TENANT_ID     = os.getenv("TENANT_ID")
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET,
)

target_workspace = FabricWorkspace(
   workspace_id=TEST_WORKSPACE_ID,
   repository_directory="./",
   environment="test",
   item_type_in_scope=[
       "Notebook",
       "DataPipeline",
       "SemanticModel",
       "Report",
   ],
   token_credential=credential,
)

changed = get_changed_items(
  target_workspace.repository_directory,
   git_compare_ref="dev",
)

print(changed)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

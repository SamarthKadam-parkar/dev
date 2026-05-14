# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.2
#   language_info:
#     name: python
# ---

# %% [markdown]
# Fabric notebook source

# %% [markdown]
# METADATA ********************

# %% [markdown]
# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "e3a21b57-160a-49bf-9a49-8d50ac00835b",
# META       "default_lakehouse_name": "raw",
# META       "default_lakehouse_workspace_id": "fd090d74-08b5-4348-89a8-15d1280f84b3",
# META       "known_lakehouses": [
# META         {
# META           "id": "e3a21b57-160a-49bf-9a49-8d50ac00835b"
# META         }
# META       ]
# META     }
# META   }
# META }

# %% [markdown]
# MARKDOWN ********************

# %% [markdown]
# ## Bronze tables creation

# %% [markdown]
# CELL ********************

# %%
from pyspark.sql import functions as F

# %% [markdown]
# METADATA ********************

# %% [markdown]
# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# %%
a = 1 
b = 2 
print(a//b)

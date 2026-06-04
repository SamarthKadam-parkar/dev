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

# CELL ********************

TARGET_CATALOG = "bronze"
#TARGET_SCHEMA = "dbo"



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.types import DateType
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.conf.set("spark.sql.session.timeZone", "Asia/Kolkata")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


run_time = datetime.now(ZoneInfo("Asia/Kolkata"))
print(f"🔔 Starting DQ Audit: {TARGET_CATALOG}.@ {run_time}")

def clean_col_name(name):
    return "_".join(name.strip().upper().split()).replace("*", "ALL")

# ============================================
# 1. DISCOVER TABLES
# ============================================
tables_df = spark.sql(f"SHOW TABLES IN {TARGET_CATALOG}")
table_names = [row['tableName'] for row in tables_df.collect()]
print(f"📂 {len(table_names)} tables found")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

audit_results = []

for t in table_names:
    full_table_name = f"{TARGET_CATALOG}.{t}"
    
    try:
        df = spark.read.table(full_table_name)
        
        # Repartition to distribute load (optional based on size)
        # df = df.repartition(200)  # Uncomment if table is huge & fragmented
        
        # 1. Get Total & Distinct (Single Pass)
        basic_stats = df.agg(
            F.count("*").alias("total_rows"),
            F.countDistinct(*df.columns).alias("distinct_rows")
        ).collect()[0]
        
        total_rows = basic_stats["total_rows"]
        true_dupes = total_rows - basic_stats["distinct_rows"]
        
        if total_rows == 0:
            continue
            
        # 2. Process columns in batches (prevents query compile overload)
        safe_types = ["string", "date", "timestamp", "int", "bigint", "long", "double", "float", "decimal", "boolean"]
        all_cols = [c for c, d in df.dtypes if d in safe_types]
        
        # Process ALL columns in one agg (Spark is smart enough to optimize)
        agg_exprs = []
        col_meta = []
        
        for col_name in all_cols:
            dtype = dict(df.dtypes).get(col_name, "string")
            safe_col = f"`{col_name}`"
            
            # Nulls
            agg_exprs.append(F.count(F.when(F.col(safe_col).isNull(), 1)).alias(f"n_{col_name}"))
            # Distincts
            agg_exprs.append(F.countDistinct(F.col(safe_col)).alias(f"d_{col_name}"))
            # Tildes (string)
            if dtype == "string":
                agg_exprs.append(F.count(F.when(F.col(safe_col).contains("~"), 1)).alias(f"t_{col_name}"))
            # Invalid Dates
            if dtype in ["date", "timestamp"]:
                agg_exprs.append(F.count(F.when(
                    (F.col(safe_col) < F.lit("1900-01-01").cast(DateType())) | 
                    (F.col(safe_col) > F.lit("2099-12-31").cast(DateType()))
                , 1)).alias(f"i_{col_name}"))
            
            col_meta.append({
                "name": col_name,
                "dtype": dtype,
                "has_tilde": dtype == "string",
                "is_date": dtype in ["date", "timestamp"]
            })
        
        # Execute single aggregation for entire table
        result = df.agg(*agg_exprs).collect()[0]
        
        # 3. Parse results
        for meta in col_meta:
            c = meta["name"]
            d = meta["dtype"]
            
            null_count = result[f"n_{c}"]
            dist_count = result[f"d_{c}"]
            tilde_count = result[f"t_{c}"] if meta["has_tilde"] else 0
            invalid_dates = result[f"i_{c}"] if meta["is_date"] else 0
            
            audit_results.append({
                "RUNTIMESTAMP": run_time,
                "TABLE_NAME": t,
                "COLUMN_NAME": c,
                "DATA_TYPE": d,
                "INVALID_DATES": invalid_dates,
                "TILDAS": tilde_count,
                "COUNT_OF_BLANKS": null_count,
                "TRUE_DUPES": true_dupes,
                "COUNT_ALL": total_rows,
                "COUNT_DISTINCT_ALL": dist_count
            })
            
    except Exception as e:
        print(f"❌ Error {t}: {str(e)[:100]}")
        # traceback.print_exc()  # Uncomment for debugging

# ============================================
# 3. DISPLAY & SAVE
# ============================================
if audit_results:
    report_df = spark.createDataFrame(audit_results)
    
    # Order columns
    final_report = report_df.select(
        "RUNTIMESTAMP", "TABLE_NAME", "COLUMN_NAME", "DATA_TYPE", 
        "INVALID_DATES", "TILDAS", "COUNT_OF_BLANKS", 
        "TRUE_DUPES", "COUNT_ALL", "COUNT_DISTINCT_ALL"
    )
    
    display(final_report)  # ✅ Shows as table in Notebook
    
    # Save to Delta
    final_report.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{TARGET_CATALOG}.update_sanity")
    
    print(f"✅ Complete! {len(audit_results)} rows in audit report.")
else:
    print("⚠️ No data.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

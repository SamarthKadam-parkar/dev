# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# DQ reports for data validation and testing
# getting counts for each and storing results in table/csv

# Import required libraries

# Import Required Libraries

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    trim,
    when,
    count,
    current_date,
    max as max_,
    lit,
    current_timestamp
)

from pyspark.sql.types import (
    StringType,
    IntegerType,
    LongType,
    DoubleType,
    FloatType,
    DateType,
    TimestampType
)

from datetime import datetime


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


dev config: 
AzureDataLakeStorage{"server":"onelake.dfs.fabric.microsoft.com","path":"/8d6b0cb1-52e3-4e5c-8a36-b47bf955cdbb/14f8a35a-5a98-4b9f-9d9a-b8c9302919c8/"}
dev:
https://app.powerbi.com/groups/8d6b0cb1-52e3-4e5c-8a36-b47bf955cdbb/datasets/fd4be8a1-5100-4e1e-bc48-eb8c5e1d3853/details?experience=power-bi
test:
https://app.powerbi.com/groups/7e906e4e-7313-4701-82b0-62064f2ccb24/datasets/4fda8594-e43d-4252-87cd-136a4f8a5220/details?experience=power-bi


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark",
# META   "frozen": true,
# META   "editable": false
# META }

# CELL ********************


# Configuration

CURRENT_WORKSPACE_NAME = notebookutils.runtime.context.get("currentWorkspaceName")

LAKEHOUSE = "bronze"
LAKEHOUSE_SCHEMA = "icims"
TABLE_NAME = "activity"

TABLE_PATH = f"abfss://{CURRENT_WORKSPACE_NAME}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}.Lakehouse/Tables/{LAKEHOUSE_SCHEMA}"

# Freshness threshold in days
MAX_ALLOWED_DAYS = 7

# Freshness column
FRESHNESS_COLUMN = "DATE_GENERATED"


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# Load Bronze Table

bronze_df = spark.read.format("delta").load(f"{TABLE_PATH}/{TABLE_NAME}")

print(f"Loaded Table: {TABLE_NAME}")
print(f"Total Rows: {bronze_df.count()}")
print(f"Total Columns: {len(bronze_df.columns)}")

display(bronze_df.limit(5))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# Validation Result Container

validation_results = []
# Row Count Validation
row_count = bronze_df.count()

validation_results.append({
    "check_name": "Row Count Check",
    "column_name": "ALL",
    "failed_count": 0 if row_count > 0 else 1,
    "status": "PASS" if row_count > 0 else "FAIL"
})

print(f"Row Count: {row_count}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Null and Blank Check for All Columns
for column_name in bronze_df.columns:

    null_count = bronze_df.filter(
        col(column_name).isNull()
    ).count()

    blank_count = 0

    if dict(bronze_df.dtypes)[column_name] == 'string':

        blank_count = bronze_df.filter(
            trim(col(column_name)) == ""
        ).count()

    total_issue_count = null_count + blank_count

    validation_results.append({
        "check_name": "Null and Blank Check",
        "column_name": column_name,
        "failed_count": total_issue_count,
        "status": "PASS" if total_issue_count == 0 else "FAIL"
    })

    print(f"{column_name} -> Nulls: {null_count}, Blanks: {blank_count}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# True Duplicate Row Check
duplicate_rows = bronze_df.groupBy(bronze_df.columns) \
    .count() \
    .filter(col("count") > 1)

duplicate_count = duplicate_rows.count()

validation_results.append({
    "check_name": "True Duplicate Row Check",
    "column_name": "ALL",
    "failed_count": duplicate_count,
    "status": "PASS" if duplicate_count == 0 else "FAIL"
})

print(f"True Duplicate Rows: {duplicate_count}")

display(duplicate_rows)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# Expected schema columns

expected_columns = [
    "claim_id",
    "member_id",
    "provider_id",
    "paid_amount",
    "claim_date"
]

actual_columns = bronze_df.columns

missing_columns = list(
    set(expected_columns) - set(actual_columns)
)

validation_results.append({
    "check_name": "Schema Validation",
    "column_name": "ALL",
    "failed_count": len(missing_columns),
    "status": "PASS" if len(missing_columns) == 0 else "FAIL"
})

print(f"Missing Columns: {missing_columns}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# Expected datatypes

expected_dtypes = {
    "claim_id": "string",
    "member_id": "string",
    "provider_id": "string",
    "paid_amount": "double",
    "claim_date": "date"
}

actual_dtypes = dict(bronze_df.dtypes)

datatype_issues = []

for column_name, expected_dtype in expected_dtypes.items():

    actual_dtype = actual_dtypes.get(column_name)

    if actual_dtype != expected_dtype:

        datatype_issues.append(
            f"{column_name}: Expected={expected_dtype}, Actual={actual_dtype}"
        )

validation_results.append({
    "check_name": "Data Type Validation",
    "column_name": "ALL",
    "failed_count": len(datatype_issues),
    "status": "PASS" if len(datatype_issues) == 0 else "FAIL"
})

print("Datatype Issues:")

for issue in datatype_issues:
    print(issue)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Freshness Check
latest_date = bronze_df.select(
    max_(FRESHNESS_COLUMN)
).collect()[0][0]

days_difference = spark.sql(f'''
SELECT datediff(current_date(), DATE("{latest_date}")) AS diff
''').collect()[0]["diff"]

validation_results.append({
    "check_name": "Freshness Check",
    "column_name": FRESHNESS_COLUMN,
    "failed_count": days_difference,
    "status": "PASS" if days_difference <= MAX_ALLOWED_DAYS else "FAIL"
})

print(f"Latest Date: {latest_date}")
print(f"Freshness Gap: {days_difference} days")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Validation Summary
validation_df = spark.createDataFrame(validation_results)

display(validation_df)

summary_df = validation_df.groupBy("status") \
    .count()

display(summary_df)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Date validation range
MIN_DATE = "1900-01-01"
MAX_DATE = "2099-12-31"

print(f"Workspace: {CURRENT_WORKSPACE_NAME}")
print(f"Lakehouse: {LAKEHOUSE}")
print(f"Schema: {LAKEHOUSE_SCHEMA}")
print(f"Table: {TABLE_NAME}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

revenue_test_df = spark.read.format("delta").load(f"{TABLE_PATH}/{TABLE_NAME}")
# display(revenue_test_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# COMMAND ----------
# Load the table
revenue_test_df = spark.read.format("delta").load(f"{TABLE_PATH}/{TABLE_NAME}")
print(f"✓ Loaded table: {TABLE_NAME}")
print(f"Total rows: {revenue_test_df.count()}")
print(f"Total columns: {len(revenue_test_df.columns)}")
display(revenue_test_df.limit(5))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC ## 1. Invalid Date Validation

# COMMAND ----------
# Get date columns
date_columns = [
    field.name for field in revenue_test_df.schema.fields 
    if str(field.dataType).lower() in ['datetype', 'timestamptype']
]

print(f"Date columns found: {date_columns}")

# Check for invalid dates
if date_columns:
    invalid_date_results = []
    
    for date_col in date_columns:
        invalid_count = revenue_test_df.filter(
            (col(date_col) < MIN_DATE) | (col(date_col) > MAX_DATE)
        ).count()
        
        invalid_date_results.append({
            'check_name': 'Invalid Dates',
            'column_name': date_col,
            'invalid_count': invalid_count,
            'total_count': revenue_test_df.count(),
            'invalid_percentage': round((invalid_count / revenue_test_df.count()) * 100, 2)
        })
    
    invalid_dates_df = spark.createDataFrame(invalid_date_results)
    print("\n✓ Invalid Date Check Results:")
    display(invalid_dates_df)
else:
    print("No date columns found")
    invalid_dates_df = spark.createDataFrame([], schema="check_name STRING, column_name STRING, invalid_count LONG, total_count LONG, invalid_percentage DOUBLE")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


failed_validations = validation_df.filter(
    col("status") == "FAIL"
).count()

if failed_validations > 0:

    raise Exception(
        f"DQ Validation Failed. Total Failed Checks: {failed_validations}"
    )

else:

    print("All Bronze DQ Validations Passed Successfully")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark",
# META   "frozen": true,
# META   "editable": false
# META }

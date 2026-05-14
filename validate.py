import os

print("Running Fabric artifact validation...")

required_folders = [
    "Notebooks",
    "Lakehouses"
]

for folder in required_folders:
    if not os.path.exists(folder):
        raise Exception(f"Missing required folder: {folder}")

print("Validation successful")
from pathlib import Path

# def list_all_files(repo_path: Path) -> list:
#     return [str(p) for p in repo_path.rglob("*") if p.is_file()]

# # Example usage:
# files = list_all_files(Path("."))
# for file in files:
#     if (file.is_dir()
#         and not any(p.startswith(".") for p in file.parts)
#         and "." in file.name): 
#             print(file)


# def scan_workspace_items(repo_path: Path) -> dict:
#     items_by_type = {}
#     for folder in repo_path.rglob("*"):
#         if (folder.is_dir()
#                 and not any(p.startswith(".") for p in folder.parts)
#                 and "." in folder.name):
#              print(folder)

# result = scan_workspace_items(Path)
# print(result)

import json
from pathlib import Path

def scan_workspace_items(repo_path: Path) -> dict:
    items_by_type = {}
    
    for folder in repo_path.rglob("*"):
        if (folder.is_dir()
                and not any(p.startswith(".") for p in folder.parts)
                and "." in folder.name):
            
            item_name, item_type = folder.name.rsplit(".", 1)
            
            if 2 <= len(item_type) <= 25:
                key = item_type.lower()
                items_by_type.setdefault(key, {"display_type": item_type, "items": []})
                full = f"{item_name}.{item_type}"
                
                if not any(i["name"] == item_name for i in items_by_type[key]["items"]):
                    # Target the .platform file inside this item folder
                    platform_file = folder / ".platform"
                    display_name = item_name  # Fallback if file missing/corrupt
                    logical_id = None        # Fallback if file missing/corrupt
                    
                    if platform_file.is_file():
                        try:
                            with open(platform_file, "r", encoding="utf-8") as f:
                                config = json.load(f)
                                # Extract properties (Fabric standard keys are often 'metadata' or root level)
                                # Adjust the keys below if your Fabric version places them inside a 'metadata' block
                                display_name = config.get("displayName", item_name)
                                logical_id = config.get("logicalId", None)
                        except (json.JSONDecodeError, KeyError, IOError):
                            # Gracefully fallback if the file is empty or unreadable
                            pass

                    items_by_type[key]["items"].append({
                        "name": item_name, 
                        "full": full,
                        "display_name": display_name,
                        "logical_id": logical_id
                    })
                    
    for key in items_by_type:
        items_by_type[key]["items"].sort(key=lambda x: x["name"])
        
    return items_by_type

scan_workspace_items(Path)

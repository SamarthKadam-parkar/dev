import os
from azure.identity import ClientSecretCredential

from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   get_changed_items
)
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROD_WORKSPACE_ID = os.getenv("PROD_WORKSPACE_ID")

credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET
)

target_workspace = FabricWorkspace(
   workspace_id=PROD_WORKSPACE_ID,
   repository_directory="./",
   environment="prod",
   item_type_in_scope=[
       "Notebook",
       "DataPipeline",
       "SemanticModel",
       "Report"
   ],
   token_credential=credential
)

changed = get_changed_items(target_workspace.repository_directory,git_compare_ref="main")
if changed:
   publish_all_items(target_workspace,items_to_include=changed)
   print("Deployment to PROD completed successfully")
else:
   print("No fabric items were added, modified or removed for current push from test to prod")

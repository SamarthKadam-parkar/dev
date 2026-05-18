import os
from azure.identity import ClientSecretCredential
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items
)
TENANT_ID = os.getenv("FABRIC_TENANT_ID")
CLIENT_ID = os.getenv("FABRIC_CLIENT_ID")
CLIENT_SECRET = os.getenv("FABRIC_CLIENT_SECRET")
WORKSPACE_ID = os.getenv("FABRIC_TEST_WORKSPACE_ID")
credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET
)
target_workspace = FabricWorkspace(
   workspace_id=WORKSPACE_ID,
   repository_directory="./",
   item_type_in_scope=[
       "Notebook",
       "DataPipeline",
       "Lakehouse",
       "SemanticModel",
       "Report"
   ],
   token_credential=credential
)
publish_all_items(target_workspace)
unpublish_all_orphan_items(target_workspace)
print("Deployment to TEST completed successfully")

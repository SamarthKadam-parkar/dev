import os
from azure.identity import ClientSecretCredential
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items,
   change_log_level
)


TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WORKSPACE_ID = os.getenv("DEV_WORKSPACE_ID")
REPOSITORY_DIRECTORY = "./"

credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET
)

change_log_level("INFO")

target_workspace = FabricWorkspace(
   workspace_id=WORKSPACE_ID,
   repository_directory=REPOSITORY_DIRECTORY,
   item_type_in_scope=[
       "Notebook",
       "DataPipeline",
       "SemanticModel",
       "Report",
       "Environment"
   ],
   token_credential=credential
)

publish_all_items(target_workspace)

# unpublish_all_orphan_items(target_workspace)
print("Deployment to DEV completed successfully")

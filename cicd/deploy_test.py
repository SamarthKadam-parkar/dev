import os
from azure.identity import ClientSecretCredential
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items
)

from dotenv import load_dotenv
load_dotenv()
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
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
publish_all_items(target_workspace)
# unpublish_all_orphan_items(target_workspace)
print("Deployment to TEST completed successfully")

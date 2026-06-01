import os
from azure.identity import ClientSecretCredential
import json
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items,
   append_feature_flag
)
from dotenv import load_dotenv
load_dotenv()
append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET,
)

with open("manifest/manifest.json","r") as f:
    manifest = json.load(f)
items_in_scope = manifest["items_in_scope"]
item_type_in_scope = manifest["item_type_in_scope"]

target_workspace = FabricWorkspace(
   workspace_id=TEST_WORKSPACE_ID,
   repository_directory="./",
   environment="test",
   item_type_in_scope= item_type_in_scope,
   token_credential=credential,
)
publish_all_items(
                  target_workspace,             
                  items_to_include=items_in_scope 
                  )
# unpublish_all_orphan_items(target_workspace)
print("Deployment to TEST completed successfully")

import os
from azure.identity import ClientSecretCredential
import json
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   append_feature_flag
)

append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")

#azure credentials 
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#prod workspace ID
PROD_WORKSPACE_ID = os.getenv("PROD_WORKSPACE_ID")

#Client Secret Credential - Tenant ID + Client ID + Client Secret
credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET
)

#Reading Manifest File to get list of items to deploy in target workspace
with open("manifest/manifest.json","r") as f:
    manifest = json.load(f)
items_in_scope = manifest["items_in_scope"]
item_type_in_scope = manifest["item_type_in_scope"]

#Initializing Target Workspace
target_workspace = FabricWorkspace(
   workspace_id=PROD_WORKSPACE_ID,
   repository_directory="./",
   environment="prod",
   item_type_in_scope=item_type_in_scope,
   token_credential=credential
)

#Publishing to Target Workspace
publish_all_items(target_workspace,items_to_include=items_in_scope)
print("Deployment to PROD completed successfully")

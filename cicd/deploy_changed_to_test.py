import os
from azure.identity import ClientSecretCredential
from fabric_cicd import (
   FabricWorkspace,
   publish_all_items,
   unpublish_all_orphan_items,
   get_changed_items,
   append_feature_flag,
)
from dotenv import load_dotenv
load_dotenv()
# ── 1. Required feature flags for selective / changed-only deployment ─────────
#
# items_to_include is an experimental feature — both flags are MANDATORY.
# Without these, passing items_to_include to publish_all_items() is silently
# ignored and a full deployment runs instead.
append_feature_flag("enable_experimental_features")
append_feature_flag("enable_items_to_include")
# ── 2. Credentials ────────────────────────────────────────────────────────────
TENANT_ID     = os.getenv("TENANT_ID")
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
credential = ClientSecretCredential(
   tenant_id=TENANT_ID,
   client_id=CLIENT_ID,
   client_secret=CLIENT_SECRET,
)
# ── 3. Workspace object ───────────────────────────────────────────────────────
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
# ── 4. Detect changed items ───────────────────────────────────────────────────
#
# get_changed_items() runs `git diff` against the given ref and returns a list
# of strings in "item_name.item_type" format, e.g.:
#   ["SalesNotebook.Notebook", "ProductsModel.SemanticModel"]
#
# git_compare_ref="dev" compares HEAD (current feature branch commit)
# against the tip of the remote dev branch — exactly what you want when
# pushing a PR merge commit from feature → dev → test.
#
# Important: only returns ADDED and MODIFIED items, not deleted ones.
# Deleted item cleanup is handled separately by unpublish_all_orphan_items().
changed = get_changed_items(
   repository_directory=target_workspace.repository_directory,
   git_compare_ref="dev",
)

print(changed)
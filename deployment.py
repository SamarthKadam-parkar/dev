"""
deploy.py
Optional deployment automation using fabric-cicd.
Publishes repository artifacts into a target Fabric workspace.
"""

import os
import logging
# from auth import TENANT_ID, CLIENT_ID, CLIENT_SECRET, WORKSPACE_ID
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
DEV_WORKSPACE_ID = os.getenv("DEV_WOWRKSPACE_ID")
token_credential = ClientSecretCredential(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, tenant_id=TENANT_ID)

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("fabric-deploy")

def main():
    logger.info("Starting deployment to Fabric workspace: %s", DEV_WORKSPACE_ID)

    # Initialize FabricWorkspace object
    workspace = FabricWorkspace(
        workspace_id=DEV_WORKSPACE_ID,
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        repository_directory=".",
        token_credential= token_credential,
        item_type_in_scope=["Notebook", "Lakehouses"]
    )

    # Publish all items from repo into workspace
    logger.info("Publishing repository items...")
    publish_all_items(workspace)
    logger.info("Publish complete.")

    # Optional: clean up orphaned items
    logger.info("Cleaning up orphan items...")
    unpublish_all_orphan_items(workspace)
    logger.info("Orphan cleanup complete.")

    logger.info("Deployment finished successfully.")

if __name__ == "__main__":
    main()

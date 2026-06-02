import sys, os
from dotenv import load_dotenv
from pathlib import Path
import json
from fabric_cicd import FabricWorkspace, get_changed_items
from azure.identity import ClientSecretCredential
from git import Repo

load_dotenv()
REPO_PATH = Path("C:/Users/samarth.kadam/dev")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Workspace IDs
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
PROD_WORKSPACE_ID = os.getenv("PROD_WORKSPACE_ID")

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

def git_commit_and_sync_with_library(commit_message="Auto-commit via GitPython"):
    try:
        repo_path = os.getcwd()
        repo = Repo(repo_path)

        if repo.bare:
            print("Could not find a valid Git repository.")
            return

        repo.git.add(A=True)
        repo.index.commit(commit_message)

        origin = repo.remote(name="origin")
        origin.pull(rebase=True)
        origin.push()

        print("Successfully committed and synced changes using GitPython!")

    except Exception as e:
        print(f"An error occurred: {e}")

def scan_workspace_items(repo_path):
    items_by_type = {}
    for folder in repo_path.rglob("*"):
        if (
            folder.is_dir()
            and not any(part.startswith(".") for part in folder.parts)
            and "." in folder.name
        ):
            item_name, item_type = folder.name.rsplit(".", 1)
            if 2 <= len(item_type) <= 25:
                type_key = item_type.lower()
                if type_key not in items_by_type:
                    items_by_type[type_key] = {
                        "display_type": item_type,
                        "items": [],
                    }
                full_string = f"{item_name}.{item_type}"
                if not any(i["name"] == item_name for i in items_by_type[type_key]["items"]):
                    items_by_type[type_key]["items"].append({"name": item_name, "full": full_string})
    for key in items_by_type:
        items_by_type[key]["items"].sort(key=lambda x: x["name"])
    return items_by_type

def select_workspace():
    print("\nSelect target workspace:")
    print("1. Test Workspace")
    print("2. Prod Workspace")
    choice = input("Enter choice (1/2): ").strip()
    if choice == "1":
        return FabricWorkspace(
            workspace_id=TEST_WORKSPACE_ID,
            repository_directory="./",
            environment="test",
            token_credential=credential,
        )
    elif choice == "2":
        return FabricWorkspace(
            workspace_id=PROD_WORKSPACE_ID,
            repository_directory="./",
            environment="prod",
            token_credential=credential,
        )
    else:
        print("Invalid choice, defaulting to Test Workspace.")
        return FabricWorkspace(
            workspace_id=TEST_WORKSPACE_ID,
            repository_directory="./",
            environment="test",
            token_credential=credential,
        )

def menu_items():
    target_workspace = select_workspace()
    items_by_type = scan_workspace_items(REPO_PATH)
    items_in_scope = []

    if not items_by_type:
        print("No Fabric items found in the specified path.")
        return

    while True:
        print("\n" + "=" * 50)
        print("          FABRIC DEPLOYMENT SCOPE BUILDER          ")
        print("=" * 50)

        menu_options = sorted(list(items_by_type.keys()))

        # Show changed items
        changed_items = get_changed_items(target_workspace.repository_directory, git_compare_ref="dev")
        print("Changed Items:", changed_items)

        # New option: Add all changed items
        print("0. Add all changed items to deployment scope")

        for index, type_key in enumerate(menu_options, start=1):
            display_name = items_by_type[type_key]["display_type"]
            count = len(items_by_type[type_key]["items"])
            print(f"{index}. View/Select {display_name} ({count} items)")

        print(f"{len(menu_options) + 1}. Proceed to Deployment / Show List")
        print(f"{len(menu_options) + 2}. Exit")
        print("-" * 50)
        print(f"Current items in scope ({len(items_in_scope)}): {items_in_scope}")
        print("-" * 50)

        choice = input("Select an option number: ").strip()

        # Exit
        if choice == str(len(menu_options) + 2):
            print("\nExiting application.")
            sys.exit()

        # Proceed to Deployment
        if choice == str(len(menu_options) + 1):
            print("FINAL DEPLOYMENT SCOPE LIST GENERATED:")
            print("=" * 50)
            item_type_in_scope = list({item.split(".")[1] for item in items_in_scope})
            manifest_data = {
                "item_type_in_scope": item_type_in_scope,
                "items_in_scope": items_in_scope,
            }
            with open("manifest/manifest.json", "w") as f:
                json.dump(manifest_data, f, indent=4)
            print("Deployment Manifest updated")
            git_commit_and_sync_with_library(f"Deployed {items_in_scope}")
            return item_type_in_scope, items_in_scope

        # Add all changed items
        if choice == "0":
            if changed_items:
                for item in changed_items:
                    if item not in items_in_scope:
                        items_in_scope.append(item)
                print("All changed items added to scope.")
            else:
                print("No changed items detected.")

        # View/select items by type
        elif choice.isdigit() and 1 <= int(choice) <= len(menu_options):
            selected_key = menu_options[int(choice) - 1]
            selected_data = items_by_type[selected_key]
            type_items = selected_data["items"]

            while True:
                print(f"\nSelect items from '{selected_data['display_type']}':")
                print("-" * 50)
                print("0. ADD ALL items from this category")

                for i, item in enumerate(type_items, start=1):
                    status = "[ADDED]" if item["full"] in items_in_scope else "[EMPTY]"
                    print(f"{i}. {status} {item['name']}")

                print(f"{len(type_items) + 1}. Return to Main Menu")
                print("-" * 50)

                sub_choice = input("Select item number to toggle/add: ").strip()

                if sub_choice == str(len(type_items) + 1):
                    break

                if sub_choice == "0":
                    for item in type_items:
                        if item["full"] not in items_in_scope:
                            items_in_scope.append(item["full"])
                    print(f"\nAll {selected_data['display_type']} items added to scope.")
                    break

                if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(type_items):
                    target_item = type_items[int(sub_choice) - 1]
                    if target_item["full"] in items_in_scope:
                        items_in_scope.remove(target_item["full"])
                        print(f"Removed: {target_item['name']}")
                    else:
                        items_in_scope.append(target_item["full"])
                        print(f"Added: {target_item['name']}")
                else:
                    print("\nInvalid selection.")
        else:
            print("\nInvalid selection. Please enter a valid menu number.")

a = menu_items()
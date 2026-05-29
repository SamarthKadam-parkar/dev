import sys
from pathlib import Path

# Replace with your actual repository path
REPO_PATH = Path("C:/Users/samarth.kadam/dev")


def scan_workspace_items(repo_path):
    """Scans the repository and groups item details by their item type."""
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
                        "items": [],  # Stores dicts of {'name': x, 'full': x.Type}
                    }

                # Construct the full standard format string required by fabric-cicd
                full_string = f"{item_name}.{item_type}"

                # Avoid duplicates
                if not any(
                    i["name"] == item_name
                    for i in items_by_type[type_key]["items"]
                ):
                    items_by_type[type_key]["items"].append(
                        {"name": item_name, "full": full_string}
                    )

    # Sort items alphabetically by name within categories
    for key in items_by_type:
        items_by_type[key]["items"].sort(key=lambda x: x["name"])

    return items_by_type


def main():
    items_by_type = scan_workspace_items(REPO_PATH)
    items_in_scope = []  # This list will hold your deployment targets

    if not items_by_type:
        print("No Fabric items found in the specified path.")
        return

    while True:
        print("\n" + "=" * 50)
        print("          FABRIC DEPLOYMENT SCOPE BUILDER          ")
        print("=" * 50)

        menu_options = sorted(list(items_by_type.keys()))

        # Display the menu with item counts
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

        # Handle Exit
        if choice == str(len(menu_options) + 2):
            print("\nExiting application.")
            sys.exit()

        # Handle Proceeding to Deployment
        if choice == str(len(menu_options) + 1):
            print("FINAL DEPLOYMENT SCOPE LIST GENERATED:")
            print("=" * 50)
            print(f"items_in_scope = {items_in_scope}")
            print("=" * 50)
            print("You can now pass this Python list directly into your deployment configuration.")
            break

        # Handle viewing and choosing items from a specific type
        if choice.isdigit() and 1 <= int(choice) <= len(menu_options):
            selected_key = menu_options[int(choice) - 1]
            selected_data = items_by_type[selected_key]
            type_items = selected_data["items"]

            while True:
                print(f"\nSelect items from '{selected_data['display_type']}':")
                print("-" * 50)
                print("0. ADD ALL items from this category")

                for i, item in enumerate(type_items, start=1):
                    status = (
                        "[ADDED]"
                        if item["full"] in items_in_scope
                        else "[EMPTY]"
                    )
                    print(f"{i}. {status} {item['name']}")

                print(f"{len(type_items) + 1}. Return to Main Menu")
                print("-" * 50)

                sub_choice = (
                    input("Select item number to toggle/add: ").strip()
                )

                if sub_choice == str(len(type_items) + 1):
                    break

                # Add all items option
                if sub_choice == "0":
                    for item in type_items:
                        if item["full"] not in items_in_scope:
                            items_in_scope.append(item["full"])
                    print(f"\nAll {selected_data['display_type']} items added to scope.")
                    break

                # Individual toggle selection logic
                if (
                    sub_choice.isdigit()
                    and 1 <= int(sub_choice) <= len(type_items)
                ):
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


if __name__ == "__main__":
    main()

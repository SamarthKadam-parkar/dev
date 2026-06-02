import os, sys, json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from dotenv import load_dotenv
from fabric_cicd import FabricWorkspace, get_changed_items
from azure.identity import ClientSecretCredential
from git import Repo

# ── Config ───────────────────────────────────────────────
load_dotenv()
REPO_PATH = Path("C:/Users/samarth.kadam/dev")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
PROD_WORKSPACE_ID = os.getenv("PROD_WORKSPACE_ID")

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

# ── Git helper ───────────────────────────────────────────
def git_commit_and_sync_with_library(commit_message="Auto-commit via GitPython"):
    try:
        repo_path = os.getcwd()
        repo = Repo(repo_path)
        if repo.bare:
            messagebox.showerror("Git Error", "Could not find a valid Git repository.")
            return
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name="origin")
        origin.pull(rebase=True)
        origin.push()
        messagebox.showinfo("Git", "Successfully committed and synced changes!")
    except Exception as e:
        messagebox.showerror("Git Error", f"An error occurred:\n{e}")

# ── Workspace scan ───────────────────────────────────────
def scan_workspace_items(repo_path: Path) -> dict:
    items_by_type = {}
    for folder in repo_path.rglob("*"):
        if folder.is_dir() and not any(part.startswith(".") for part in folder.parts) and "." in folder.name:
            item_name, item_type = folder.name.rsplit(".", 1)
            if 2 <= len(item_type) <= 25:
                type_key = item_type.lower()
                if type_key not in items_by_type:
                    items_by_type[type_key] = {"display_type": item_type, "items": []}
                full_string = f"{item_name}.{item_type}"
                if not any(i["name"] == item_name for i in items_by_type[type_key]["items"]):
                    items_by_type[type_key]["items"].append({"name": item_name, "full": full_string})
    for key in items_by_type:
        items_by_type[key]["items"].sort(key=lambda x: x["name"])
    return items_by_type

# ── Tkinter App ──────────────────────────────────────────
class FabricDeployUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fabric Deployment")
        self.geometry("1000x700")
        self.configure(bg="#f8fafc")

        # Workspace selection
        self.target_workspace = None
        self._select_workspace()

        # Data
        self.items_by_type = scan_workspace_items(REPO_PATH)
        self.items_in_scope = set()
        self.check_vars = {}

        # UI
        self._build_ui()

    def _select_workspace(self):
        choice = tk.simpledialog.askstring("Workspace", "Enter workspace (test/prod):")
        if choice and choice.lower() == "prod":
            self.target_workspace = FabricWorkspace(
                workspace_id=PROD_WORKSPACE_ID,
                repository_directory="./",
                environment="prod",
                token_credential=credential,
            )
        else:
            self.target_workspace = FabricWorkspace(
                workspace_id=TEST_WORKSPACE_ID,
                repository_directory="./",
                environment="test",
                token_credential=credential,
            )

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#f8fafc", pady=10)
        hdr.pack(fill="x")
        ttk.Label(hdr, text="Fabric Deployment Scope", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.scope_badge = ttk.Label(hdr, text="0 items")
        self.scope_badge.pack(side="right")

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        for type_key in sorted(self.items_by_type.keys()):
            self._build_tab(type_key)

        # Scope panel
        right = tk.Frame(self, bg="#ffffff", padx=10, pady=10)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Selected Items", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.scope_listbox = tk.Listbox(right, height=20, width=40)
        self.scope_listbox.pack(fill="both", expand=True)
        ttk.Button(right, text="Remove Selected", command=self._remove_selected).pack(fill="x", pady=5)

        # Footer
        footer = tk.Frame(self, bg="#f8fafc", pady=10)
        footer.pack(fill="x")
        ttk.Button(footer, text="Add Changed Items", command=self._add_changed_items).pack(side="left", padx=5)
        ttk.Button(footer, text="Save & Deploy", command=self._deploy).pack(side="right", padx=5)

    def _build_tab(self, type_key):
        data = self.items_by_type[type_key]
        items = data["items"]
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"{data['display_type']} ({len(items)})")

        for item in items:
            var = tk.BooleanVar(value=False)
            self.check_vars[item["full"]] = var
            cb = ttk.Checkbutton(frame, text=item["full"], variable=var,
                                 command=lambda f=item["full"], v=var: self._toggle_item(f, v))
            cb.pack(anchor="w")

    def _toggle_item(self, full, var):
        if var.get():
            self.items_in_scope.add(full)
        else:
            self.items_in_scope.discard(full)
        self._refresh_scope()

    def _refresh_scope(self):
        self.scope_listbox.delete(0, "end")
        for item in sorted(self.items_in_scope):
            self.scope_listbox.insert("end", item)
        self.scope_badge.config(text=f"{len(self.items_in_scope)} items")

    def _remove_selected(self):
        selection = self.scope_listbox.curselection()
        for i in selection:
            full = self.scope_listbox.get(i)
            self.items_in_scope.discard(full)
            if full in self.check_vars:
                self.check_vars[full].set(False)
        self._refresh_scope()

    def _add_changed_items(self):
        changed = get_changed_items(self.target_workspace.repository_directory, git_compare_ref="dev")
        if not changed:
            messagebox.showinfo("Changed Items", "No changed items detected.")
            return
        for item in changed:
            self.items_in_scope.add(item)
        self._refresh_scope()
        messagebox.showinfo("Changed Items", "All changed items added to scope.")

    def _deploy(self):
        if not self.items_in_scope:
            messagebox.showwarning("Empty Scope", "Please select at least one item.")
            return
        scope_list = sorted(self.items_in_scope)
        item_types = sorted({item.split(".")[1] for item in scope_list})
        manifest_data = {"item_type_in_scope": item_types, "items_in_scope": scope_list}
        Path("manifest").mkdir(exist_ok=True)
        with open("manifest/manifest.json", "w") as f:
            json.dump(manifest_data, f, indent=4)
        git_commit_and_sync_with_library(f"Deployed {scope_list}")
        messagebox.showinfo("Deployment", f"Manifest saved and synced!\nTypes: {item_types}\nTotal: {len(scope_list)}")

if __name__ == "__main__":
    app = FabricDeployUI()
    app.mainloop()

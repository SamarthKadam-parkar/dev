import os, sys, json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from dotenv import load_dotenv
from fabric_cicd import FabricWorkspace, get_changed_items
from azure.identity import ClientSecretCredential
from git import Repo

# ── Modern Fabric Palette (Teal + Sage) ──────────────────────────────────────
PRIMARY    = "#0d9488"      # Teal
SECONDARY  = "#6b7280"      # Sage Gray
ACCENT     = "#14b8a6"      # Light Teal
BG         = "#f8fafc"      # Almost white
BG_CARD    = "#ffffff"      # Pure white cards
BG_HOVER   = "#f1f5f9"      # Hover state
FG         = "#1e293b"      # Dark text
FG_LIGHT   = "#64748b"      # Light text
BORDER     = "#e2e8f0"      # Light border
SUCCESS    = "#10b981"      # Green confirmation

FONT_MAIN  = ("Segoe UI", 10)
FONT_HEAD  = ("Segoe UI", 11, "bold")
FONT_BIG   = ("Segoe UI", 14, "bold")

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
        self.geometry("1100x720")
        self.configure(bg=BG)

        # Workspace selection
        self.target_workspace = None
        self._select_workspace()

        # Data
        self.items_by_type = scan_workspace_items(REPO_PATH)
        self.items_in_scope = set()
        self.check_vars = {}

        # Styles
        self._apply_styles()

        # UI
        self._build_ui()

    def _select_workspace(self):
        choice = simpledialog.askstring("Workspace", "Enter workspace (test/prod):")
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

    def _apply_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_LIGHT,
                    font=FONT_MAIN, padding=[12, 6], borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", PRIMARY)], foreground=[("selected", "#ffffff")])
        s.configure("TLabel", background=BG, foreground=FG, font=FONT_MAIN)
        s.configure("Title.TLabel", background=BG, foreground=PRIMARY, font=FONT_BIG)
        s.configure("Head.TLabel", background=BG_CARD, foreground=PRIMARY, font=FONT_HEAD)
        s.configure("TButton", background=BG_CARD, foreground=FG, font=FONT_MAIN,
                    borderwidth=0, padding=[10, 6], relief="flat")
        s.map("TButton", background=[("active", BG_HOVER), ("pressed", BG_HOVER)])
        s.configure("Primary.TButton", background=PRIMARY, foreground="#ffffff", font=FONT_HEAD,
                    padding=[12, 6], borderwidth=0)
        s.map("Primary.TButton", background=[("active", "#0d8a7a"), ("pressed", "#0d8a7a")])

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=20, padx=24)
        hdr.pack(fill="x")

        ttk.Label(hdr, text="Fabric Deployment Scope", style="Title.TLabel").pack(side="left")
        self.scope_badge = ttk.Label(hdr, text="0 items", style="TLabel")
        self.scope_badge.pack(side="right")

        # Workspace selector (radio buttons)
        ws_frame = tk.Frame(self, bg=BG, pady=10)
        ws_frame.pack(fill="x", padx=24)

        ttk.Label(ws_frame, text="Select Workspace:", style="Head.TLabel").pack(side="left", padx=(0,10))

        self.workspace_choice = tk.StringVar(value="test")
        ttk.Radiobutton(ws_frame, text="Test", value="test", variable=self.workspace_choice,
                        command=self._switch_workspace).pack(side="left", padx=5)
        ttk.Radiobutton(ws_frame, text="Prod", value="prod", variable=self.workspace_choice,
                        command=self._switch_workspace).pack(side="left", padx=5)

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        for type_key in sorted(self.items_by_type.keys()):
            self._build_tab(type_key)

        # Scope panel
        right = tk.Frame(self, bg=BG_CARD, padx=16, pady=12, relief="solid", borderwidth=1)
        right.pack(side="right", fill="y", padx=(10, 20))
        ttk.Label(right, text="Selected Items", style="Head.TLabel").pack(anchor="w", pady=(0, 8))
        self.scope_listbox = tk.Listbox(right, bg=BG_CARD, fg=FG, font=FONT_MAIN,
                                        selectbackground=PRIMARY, selectforeground="#ffffff",
                                        borderwidth=1, relief="solid", height=20, width=30)
        self.scope_listbox.pack(fill="both", expand=True, pady=(8, 8))
        ttk.Button(right, text="Remove Selected", command=self._remove_selected).pack(fill="x", pady=5)

        # Footer
        footer = tk.Frame(self, bg=BG, pady=12, padx=24)
        footer.pack(fill="x")
        ttk.Button(footer, text="Add Changed Items", style="TButton", command=self._add_changed_items).pack(side="left", padx=5)
        ttk.Button(footer, text="Save & Deploy", style="Primary.TButton", command=self._deploy).pack(side="right", padx=5)

    def _switch_workspace(self):
        choice = self.workspace_choice.get()
        if choice == "prod":
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
        messagebox.showinfo("Workspace Changed", f"Switched to {choice.upper()} workspace")

    def _build_tab(self, type_key):
        data = self.items_by_type[type_key]
        items = data["items"]
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"{data['display_type']} ({len(items)})")

        # Search bar
        search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=search_var, width=30)
        search_entry.pack(fill="x", padx=10, pady=5)

        list_frame = tk.Frame(frame, bg=BG)
        list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        row_widgets = []
        for item in items:
            var = tk.BooleanVar(value=False)
            self.check_vars[item["full"]] = var
            cb = ttk.Checkbutton(inner, text=item["full"], variable=var,
                                 command=lambda f=item["full"], v=var: self._toggle_item(f, v))
            cb.pack(anchor="w", padx=10, pady=2)
            row_widgets.append((cb, item["full"], var))

        # Filtering logic
        def _filter(*_):
            q = search_var.get().lower()
            for cb, full, var in row_widgets:
                if q in full.lower():
                    cb.pack(anchor="w", padx=10, pady=2)
                else:
                    cb.pack_forget()

        search_var.trace_add("write", _filter)

        # Update scroll region
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

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

import sys, os, json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from dotenv import load_dotenv
from fabric_cicd import FabricWorkspace
from azure.identity import ClientSecretCredential
from git import Repo

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
REPO_PATH         = Path("/Users/samarthkadam/dev")
MANIFEST_PATH     = Path("manifest/manifest.json")
TENANT_ID         = os.getenv("TENANT_ID")
CLIENT_ID         = os.getenv("CLIENT_ID")
CLIENT_SECRET     = os.getenv("CLIENT_SECRET")
TEST_WORKSPACE_ID = os.getenv("TEST_WORKSPACE_ID")
PROD_WORKSPACE_ID = os.getenv("PROD_WORKSPACE_ID")

credential = ClientSecretCredential(
    tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

# ── Theme ─────────────────────────────────────────────────────────────────────
PRIMARY   = "#0d9488"
SECONDARY = "#6b7280"
BG        = "#f8fafc"
BG_CARD   = "#ffffff"
BG_HOVER  = "#f1f5f9"
FG        = "#1e293b"
FG_LIGHT  = "#64748b"
BORDER    = "#e2e8f0"
WARN      = "#f59e0b"
DANGER    = "#dc2626"

FONT_MAIN = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 11, "bold")
FONT_BIG  = ("Segoe UI", 14, "bold")
FONT_MONO = ("Consolas", 9)

# ── Backend helpers ───────────────────────────────────────────────────────────
def scan_workspace_items(repo_path: Path) -> dict:
    items_by_type = {}
    for folder in repo_path.rglob("*"):
        if (folder.is_dir()
                and not any(p.startswith(".") for p in folder.parts)
                and "." in folder.name):
            item_name, item_type = folder.name.rsplit(".", 1)
            if 2 <= len(item_type) <= 25:
                key = item_type.lower()
                items_by_type.setdefault(key, {"display_type": item_type, "items": []})
                full = f"{item_name}.{item_type}"
                if not any(i["name"] == item_name for i in items_by_type[key]["items"]):
                    items_by_type[key]["items"].append({"name": item_name, "full": full})
    for key in items_by_type:
        items_by_type[key]["items"].sort(key=lambda x: x["name"])
    return items_by_type

def save_manifest(items_in_scope: list) -> None:
    item_types = list({i.split(".")[1] for i in items_in_scope})
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump({"item_type_in_scope": item_types, "items_in_scope": items_in_scope}, f, indent=4)

def git_commit_and_push(commit_message: str) -> str:
    try:
        repo = Repo(os.getcwd())
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name="origin")
        origin.pull(rebase=True)
        origin.push()
        return "Committed and pushed to origin successfully."
    except Exception as e:
        return f"Git error: {e}"

def get_changed_items_vs_dev(repo_path: Path) -> list:
    """
    Returns Fabric items present in the current branch (feature/dev)
    but not yet in origin/dev (the GitHub dev branch / test workspace).
    Uses three-dot diff: changes in HEAD that are not in origin/dev.
    """
    repo = Repo(str(repo_path))
    try:
        repo.remotes.origin.fetch()
    except Exception:
        pass  # continue with cached remote refs if fetch fails

    diff_output = repo.git.diff("origin/dev...HEAD", "--name-only", "--diff-filter=ACM")
    if not diff_output.strip():
        return []

    items = set()
    for file_path in diff_output.strip().split("\n"):
        # Find the Fabric item folder in the path (e.g. MyReport.Report)
        for part in Path(file_path).parts:
            if "." in part:
                name, ext = part.rsplit(".", 1)
                if 2 <= len(ext) <= 25 and name:
                    items.add(f"{name}.{ext}")
                    break
    return sorted(items)

def build_workspace(workspace_id: str, env: str) -> FabricWorkspace:
    return FabricWorkspace(
        workspace_id=workspace_id,
        repository_directory="./",
        environment=env,
        token_credential=credential,
    )

# ── App ───────────────────────────────────────────────────────────────────────
class FabricDeployUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fabric Deployment")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.configure(bg=BG)

        self.items_by_type: dict = scan_workspace_items(REPO_PATH)
        self.items_in_scope: set = set()
        # check_vars: {type_key: {full_string: (BooleanVar, symbol_Label)}}
        self.check_vars: dict    = {}
        self.changed_items: list = []
        self.workspace_var       = tk.StringVar(value="test")

        self._apply_styles()
        self._show_workspace_selector()

    # ── Styles ────────────────────────────────────────────────────────────────
    def _apply_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_LIGHT,
                    font=FONT_MAIN, padding=[16, 8], borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", PRIMARY)], foreground=[("selected", "#fff")])
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG, font=FONT_MAIN)
        s.configure("Title.TLabel", background=BG, foreground=PRIMARY, font=FONT_BIG)
        s.configure("Sub.TLabel",   background=BG, foreground=FG_LIGHT, font=("Segoe UI", 9))
        s.configure("TButton", background=BG_CARD, foreground=FG, font=FONT_MAIN,
                    borderwidth=0, padding=[12, 6], relief="flat", focuscolor="none")
        s.map("TButton", background=[("active", BG_HOVER)])
        s.configure("Primary.TButton", background=PRIMARY, foreground="#fff",
                    font=FONT_HEAD, padding=[14, 8], borderwidth=0)
        s.map("Primary.TButton", background=[("active", "#0b7a70")])
        s.configure("Warn.TButton", background=WARN, foreground="#fff",
                    font=FONT_MAIN, padding=[10, 6], borderwidth=0)
        s.map("Warn.TButton", background=[("active", "#d97706")])
        s.configure("TRadiobutton", background=BG_CARD, foreground=FG,
                    font=FONT_MAIN, focuscolor="none")
        s.map("TRadiobutton", background=[("active", BG_HOVER)])
        s.configure("TEntry", fieldbackground=BG_CARD, foreground=FG,
                    insertcolor=PRIMARY, borderwidth=1, relief="solid",
                    font=FONT_MAIN, padding=6)
        s.configure("TScrollbar", background=BORDER, troughcolor=BG,
                    borderwidth=0, arrowcolor=SECONDARY)

    # ── Step 1: Workspace selector ────────────────────────────────────────────
    def _show_workspace_selector(self):
        self.sel_frame = tk.Frame(self, bg=BG)
        self.sel_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.sel_frame, text="Fabric Deployment",
                 bg=BG, fg=PRIMARY, font=FONT_BIG).pack(pady=(0, 4))
        tk.Label(self.sel_frame, text="Select a target workspace to continue",
                 bg=BG, fg=FG_LIGHT, font=FONT_MAIN).pack(pady=(0, 24))

        card = tk.Frame(self.sel_frame, bg=BG_CARD, padx=32, pady=28,
                        relief="solid", borderwidth=1)
        card.pack()

        tk.Label(card, text="Target Workspace", bg=BG_CARD,
                 fg=PRIMARY, font=FONT_HEAD).pack(anchor="w", pady=(0, 16))

        for label, val, color in [("Test Workspace", "test", PRIMARY),
                                   ("Prod Workspace", "prod",  WARN)]:
            row = tk.Frame(card, bg=BG_CARD, pady=6)
            row.pack(fill="x")
            ttk.Radiobutton(row, text=label, variable=self.workspace_var,
                            value=val).pack(side="left")
            tk.Label(row, text=val.upper(), bg=color, fg="#fff",
                     font=("Segoe UI", 8, "bold"), padx=8, pady=2).pack(side="left", padx=(12, 0))

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=16)
        ttk.Button(card, text="✓  Connect & Continue", style="Primary.TButton",
                   command=self._connect_workspace).pack(fill="x")

    def _connect_workspace(self):
        env   = self.workspace_var.get()
        ws_id = TEST_WORKSPACE_ID if env == "test" else PROD_WORKSPACE_ID
        try:
            self.target_workspace = build_workspace(ws_id, env)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect:\n{e}")
            return
        self.sel_frame.destroy()
        self._build_main_ui()
        self._load_changed_items()

    # ── Step 2: Main UI ───────────────────────────────────────────────────────
    def _build_main_ui(self):
        env       = self.workspace_var.get()
        env_color = PRIMARY if env == "test" else WARN

        # ── Header ──
        hdr = tk.Frame(self, bg=BG, pady=16, padx=24)
        hdr.pack(fill="x")
        ttk.Label(hdr, text="Fabric Deployment Scope",
                  style="Title.TLabel").pack(side="left")
        badge_wrap = tk.Frame(hdr, bg=BG)
        badge_wrap.pack(side="right")
        tk.Label(badge_wrap, text=env.upper(), bg=env_color, fg="#fff",
                 font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(side="right", padx=(8, 0))
        self.scope_badge = tk.Label(badge_wrap, text="0 items",
                                    bg=BG, fg=FG_LIGHT, font=("Segoe UI", 9))
        self.scope_badge.pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Changed items banner ──
        banner = tk.Frame(self, bg=BG_CARD, padx=24, pady=10)
        banner.pack(fill="x")
        self.changed_label = tk.Label(
            banner, text="Fetching changes vs origin/dev...",
            bg=BG_CARD, fg=FG_LIGHT, font=FONT_MONO)
        self.changed_label.pack(side="left")
        ttk.Button(banner, text="✓  Add All Changed", style="Warn.TButton",
                   command=self._add_all_changed).pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Body (uses grid so both sides get defined space) ──
        body = tk.Frame(self, bg=BG, padx=24, pady=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        # Left: notebook
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew")
        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill="both", expand=True)
        for type_key in sorted(self.items_by_type.keys()):
            self._build_tab(type_key)

        # Right: scope panel — fixed width frame
        right = tk.Frame(body, bg=BG_CARD, padx=12, pady=12,
                         relief="solid", borderwidth=1, width=260)
        right.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        right.pack_propagate(False)           # keep fixed width
        self._build_scope_panel(right)

        # ── Footer ──
        footer = tk.Frame(self, bg=BG, pady=12, padx=24)
        footer.pack(fill="x")
        ttk.Button(footer, text="✓  Save & Deploy", style="Primary.TButton",
                   command=self._deploy).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Clear All", style="TButton",
                   command=self._clear_all_global).pack(side="right")

        if not self.items_by_type:
            messagebox.showwarning("No items found",
                                   f"No Fabric items found under:\n{REPO_PATH}")

    # ── Changed items ─────────────────────────────────────────────────────────
    def _load_changed_items(self):
        try:
            self.changed_items = get_changed_items_vs_dev(REPO_PATH)
            if self.changed_items:
                preview = ", ".join(self.changed_items[:4])
                extra   = f"  +{len(self.changed_items)-4} more" if len(self.changed_items) > 4 else ""
                self.changed_label.config(
                    text=f"Changes vs origin/dev ({len(self.changed_items)}): {preview}{extra}",
                    fg=WARN)
            else:
                self.changed_label.config(
                    text="No changes detected vs origin/dev — branch is up to date.", fg=FG_LIGHT)
        except Exception as e:
            self.changed_items = []
            self.changed_label.config(text=f"Could not fetch changes: {e}", fg=DANGER)

    def _add_all_changed(self):
        if not self.changed_items:
            messagebox.showinfo("No Changes", "No changed items detected vs origin/dev.")
            return
        added = 0
        for full in self.changed_items:
            if full not in self.items_in_scope:
                self.items_in_scope.add(full)
                added += 1
                type_key = full.split(".", 1)[1].lower()
                if type_key in self.check_vars and full in self.check_vars[type_key]:
                    var, sym = self.check_vars[type_key][full]
                    var.set(True)
                    sym.config(text="✓", fg=PRIMARY)
        self._refresh_scope_panel()
        messagebox.showinfo("Added", f"✓ {added} changed item(s) added to scope.")

    # ── Tab builder ───────────────────────────────────────────────────────────
    def _build_tab(self, type_key: str):
        data  = self.items_by_type[type_key]
        items = data["items"]
        outer = ttk.Frame(self.notebook)
        self.notebook.add(outer, text=f"{data['display_type']}  ({len(items)})")

        # Toolbar
        toolbar = tk.Frame(outer, bg=BG_CARD, pady=10, padx=12, height=50)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        tk.Label(toolbar, text="🔍", bg=BG_CARD, fg=SECONDARY,
                 font=FONT_MAIN).pack(side="left", padx=(0, 6))
        search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=search_var, width=24).pack(side="left", padx=(0, 12))
        ttk.Button(toolbar, text="Select All",
                   command=lambda k=type_key: self._select_all(k)).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Clear All",
                   command=lambda k=type_key: self._clear_all(k)).pack(side="left", padx=4)
        count_lbl = tk.Label(toolbar, text=f"{len(items)} items",
                             bg=BG_CARD, fg=FG_LIGHT, font=("Segoe UI", 9))
        count_lbl.pack(side="right", padx=8)

        # Scrollable canvas
        cf     = tk.Frame(outer, bg=BG)
        cf.pack(fill="both", expand=True)
        canvas = tk.Canvas(cf, bg=BG, highlightthickness=0, bd=0)
        vsb    = ttk.Scrollbar(cf, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.check_vars[type_key] = {}
        row_widgets = []

        for item in items:
            var = tk.BooleanVar(value=item["full"] in self.items_in_scope)

            # ── Row frame (child of inner) ──────────────────────────────────
            row = tk.Frame(inner, bg=BG, pady=6, padx=10, cursor="hand2")
            row.pack(fill="x")

            # Symbol label is a direct child of row — no re-parenting tricks
            sym = tk.Label(row, width=2, font=("Segoe UI", 13), bg=BG,
                           text="✓" if var.get() else "☐",
                           fg=PRIMARY if var.get() else SECONDARY)
            sym.pack(side="left", padx=(0, 10))

            name_lbl = tk.Label(row, text=item["name"], bg=BG, fg=FG,
                                font=FONT_MAIN, anchor="w", cursor="hand2")
            name_lbl.pack(side="left", fill="x", expand=True)

            tk.Label(row, text=f".{data['display_type']}", bg=BG,
                     fg=FG_LIGHT, font=("Segoe UI", 8)).pack(side="left", padx=(6, 0))

            # Divider
            tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=10)

            # Store (var, sym) together
            self.check_vars[type_key][item["full"]] = (var, sym)

            # Toggle closure
            def make_toggle(full, v, s):
                def _toggle(e=None):
                    v.set(not v.get())
                    s.config(text="✓" if v.get() else "☐",
                             fg=PRIMARY if v.get() else SECONDARY)
                    self._toggle_item(full, v)
                return _toggle

            toggle = make_toggle(item["full"], var, sym)
            row.bind("<Button-1>", toggle)
            sym.bind("<Button-1>", toggle)
            name_lbl.bind("<Button-1>", toggle)

            row_widgets.append((row, sym, item["full"], item["name"], var))

        # Search filter
        def _filter(*_):
            q, visible = search_var.get().lower(), 0
            for row, sym, full, name, var in row_widgets:
                if q in name.lower() or q in full.lower():
                    row.pack(fill="x"); visible += 1
                else:
                    row.pack_forget()
            count_lbl.config(text=f"{visible} / {len(items)} items")

        search_var.trace_add("write", _filter)

    # ── Scope panel ───────────────────────────────────────────────────────────
    def _build_scope_panel(self, parent):
        tk.Label(parent, text="IN SCOPE", bg=BG_CARD, fg=PRIMARY,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, 8))

        # Listbox + scrollbar in their own container
        lb_frame = tk.Frame(parent, bg=BG_CARD)
        lb_frame.pack(fill="both", expand=True, pady=(0, 8))

        vsb = ttk.Scrollbar(lb_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        self.scope_listbox = tk.Listbox(
            lb_frame, bg=BG_CARD, fg=FG, font=FONT_MONO,
            selectbackground=PRIMARY, selectforeground="#fff",
            borderwidth=1, relief="solid",
            yscrollcommand=vsb.set
        )
        vsb.configure(command=self.scope_listbox.yview)
        self.scope_listbox.pack(side="left", fill="both", expand=True)

        ttk.Button(parent, text="Remove Selected",
                   command=self._remove_selected).pack(fill="x")

    def _refresh_scope_panel(self):
        self.scope_listbox.delete(0, "end")
        for item in sorted(self.items_in_scope):
            self.scope_listbox.insert("end", item)
        c = len(self.items_in_scope)
        self.scope_badge.config(text=f"{c} item{'s' if c != 1 else ''}")

    # ── Toggle helpers ────────────────────────────────────────────────────────
    def _toggle_item(self, full: str, var: tk.BooleanVar):
        (self.items_in_scope.add(full) if var.get() else self.items_in_scope.discard(full))
        self._refresh_scope_panel()

    def _select_all(self, type_key: str):
        for full, (var, sym) in self.check_vars[type_key].items():
            var.set(True)
            sym.config(text="✓", fg=PRIMARY)
            self.items_in_scope.add(full)
        self._refresh_scope_panel()

    def _clear_all(self, type_key: str):
        for full, (var, sym) in self.check_vars[type_key].items():
            var.set(False)
            sym.config(text="☐", fg=SECONDARY)
            self.items_in_scope.discard(full)
        self._refresh_scope_panel()

    def _clear_all_global(self):
        for type_key in self.check_vars:
            self._clear_all(type_key)

    def _remove_selected(self):
        for i in self.scope_listbox.curselection():
            full     = self.scope_listbox.get(i)
            type_key = full.split(".", 1)[1].lower()
            self.items_in_scope.discard(full)
            if type_key in self.check_vars and full in self.check_vars[type_key]:
                var, sym = self.check_vars[type_key][full]
                var.set(False)
                sym.config(text="☐", fg=SECONDARY)
        self._refresh_scope_panel()

    # ── Deploy / review ───────────────────────────────────────────────────────
    def _deploy(self):
        if not self.items_in_scope:
            messagebox.showwarning("Empty Scope", "Select at least one item.")
            return
        self._show_review_window()

    def _show_review_window(self):
        scope_list = sorted(self.items_in_scope)
        item_types = sorted({i.split(".")[1] for i in scope_list})
        env        = self.workspace_var.get()
        env_color  = PRIMARY if env == "test" else WARN

        win = tk.Toplevel(self)
        win.title("Review & Deploy")
        win.geometry("640x580")
        win.configure(bg=BG)
        win.grab_set()

        # Header
        hdr = tk.Frame(win, bg=PRIMARY, padx=20, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Review Deployment Scope",
                 bg=PRIMARY, fg="#fff", font=FONT_BIG).pack(side="left")
        tk.Label(hdr, text=env.upper(), bg=env_color, fg="#fff",
                 font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(side="right")

        # Summary card
        sc = tk.Frame(win, bg=BG_CARD, padx=16, pady=14, relief="solid", borderwidth=1)
        sc.pack(fill="x", padx=16, pady=12)
        for row_text, val in [
            ("Total Items", str(len(scope_list))),
            ("Types",       ", ".join(item_types)),
            ("Target",      f"{env.capitalize()} Workspace"),
        ]:
            r = tk.Frame(sc, bg=BG_CARD)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=f"{row_text}:", bg=BG_CARD, fg=FG_LIGHT,
                     font=FONT_MAIN, width=12, anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=BG_CARD, fg=PRIMARY,
                     font=FONT_HEAD).pack(side="left")

        # Items list
        lf = tk.Frame(win, bg=BG)
        lf.pack(fill="both", expand=True, padx=16, pady=(0, 4))
        tk.Label(lf, text="Items for deployment:", bg=BG, fg=FG,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        lb_frame = tk.Frame(lf, bg=BG)
        lb_frame.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(lb_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        lb = tk.Listbox(lb_frame, bg=BG_CARD, fg=FG, font=FONT_MONO,
                        selectbackground=PRIMARY, selectforeground="#fff",
                        borderwidth=1, relief="solid", yscrollcommand=vsb.set)
        vsb.configure(command=lb.yview)
        lb.pack(side="left", fill="both", expand=True)
        for item in scope_list:
            lb.insert("end", f"✓  {item}")

        # Commit message
        cf = tk.Frame(win, bg=BG, padx=16, pady=6)
        cf.pack(fill="x")
        tk.Label(cf, text="Commit message:", bg=BG, fg=FG,
                 font=FONT_MAIN).pack(anchor="w")
        commit_var = tk.StringVar(value=f"Deployed {len(scope_list)} item(s) to {env}")
        ttk.Entry(cf, textvariable=commit_var).pack(fill="x", pady=4)

        status_lbl = tk.Label(win, text="", bg=BG, fg=FG_LIGHT, font=FONT_MONO)
        status_lbl.pack(padx=16, anchor="w")

        # Buttons
        bf = tk.Frame(win, bg=BG, pady=12, padx=16)
        bf.pack(fill="x")

        def confirm():
            scope = sorted(self.items_in_scope)
            types = sorted({i.split(".")[1] for i in scope})
            status_lbl.config(text="Saving manifest...", fg=FG_LIGHT); win.update()
            try:
                save_manifest(scope)
                status_lbl.config(text="✓ Manifest saved. Pushing...", fg=PRIMARY); win.update()
                git_msg = git_commit_and_push(commit_var.get())
                status_lbl.config(text=f"✓ {git_msg}", fg=PRIMARY); win.update()
            except Exception as e:
                status_lbl.config(text=f"Error: {e}", fg=DANGER)
                return
            self.result = (types, scope)
            messagebox.showinfo("Deployment Complete",
                f"✓ {len(scope)} item(s) deployed to {env.capitalize()} Workspace.\n\n{git_msg}")
            win.destroy()

        ttk.Button(bf, text="✓  Confirm & Deploy", style="Primary.TButton",
                   command=confirm).pack(side="right", padx=(8, 0))
        ttk.Button(bf, text="Cancel", style="TButton",
                   command=win.destroy).pack(side="right")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = FabricDeployUI()
    app.mainloop()
    if hasattr(app, "result"):
        item_type_in_scope, items_in_scope = app.result
        print("\nitem_type_in_scope =", item_type_in_scope)
        print("items_in_scope     =", items_in_scope)
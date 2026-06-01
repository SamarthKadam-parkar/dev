import sys

import json

import tkinter as tk

from tkinter import ttk, messagebox

from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

REPO_PATH = Path("C:/Users/samarth.kadam/dev")

MANIFEST_PATH = Path("manifest/manifest.json")

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

# ── Backend logic ────────────────────────────────────────────────────────────

def scan_workspace_items(repo_path: Path) -> dict:

    items_by_type = {}

    for folder in repo_path.rglob("*"):

        if (folder.is_dir() and not any(part.startswith(".") for part in folder.parts) 

            and "." in folder.name):

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

def save_manifest(items_in_scope: list) -> None:

    item_type_in_scope = list({item.split(".")[1] for item in items_in_scope})

    manifest_data = {"item_type_in_scope": item_type_in_scope, "items_in_scope": items_in_scope}

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_PATH, "w") as f:

        json.dump(manifest_data, f, indent=4)

# ── Main Application ──────────────────────────────────────────────────────────

class FabricDeployUI(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Fabric Deployment")

        self.geometry("1100x720")

        self.minsize(900, 600)

        self.configure(bg=BG)

        self.items_by_type = scan_workspace_items(REPO_PATH)

        self.items_in_scope = set()

        self.check_vars = {}

        self._apply_styles()

        self._build_ui()

        if not self.items_by_type:

            messagebox.showwarning("No items found", 

                f"No Fabric items found under:\n{REPO_PATH}\n\nUpdate REPO_PATH at the top of the script.")

    def _apply_styles(self):

        s = ttk.Style(self)

        s.theme_use("clam")

        s.configure("TNotebook", background=BG, borderwidth=0)

        s.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_LIGHT,

                    font=FONT_MAIN, padding=[16, 8], borderwidth=0)

        s.map("TNotebook.Tab", background=[("selected", PRIMARY)], foreground=[("selected", "#ffffff")])

        s.configure("TFrame", background=BG)

        s.configure("Card.TFrame", background=BG_CARD, relief="flat", borderwidth=0)

        s.configure("TLabel", background=BG, foreground=FG, font=FONT_MAIN)

        s.configure("Title.TLabel", background=BG, foreground=PRIMARY, font=FONT_BIG)

        s.configure("Sub.TLabel", background=BG, foreground=FG_LIGHT, font=("Segoe UI", 9))

        s.configure("Head.TLabel", background=BG_CARD, foreground=PRIMARY, font=FONT_HEAD)

        s.configure("TCheckbutton", background=BG_CARD, foreground=FG, font=FONT_MAIN, focuscolor="none")

        s.map("TCheckbutton", background=[("active", BG_HOVER)])

        s.configure("TButton", background=BG_CARD, foreground=FG, font=FONT_MAIN,

                    borderwidth=0, padding=[12, 6], relief="flat", focuscolor="none")

        s.map("TButton", background=[("active", BG_HOVER)])

        s.configure("Primary.TButton", background=PRIMARY, foreground="#ffffff", font=FONT_HEAD,

                    padding=[14, 8], borderwidth=0)

        s.map("Primary.TButton", background=[("active", "#0d8a7a")])

        s.configure("TEntry", fieldbackground=BG_CARD, foreground=FG, insertcolor=PRIMARY,

                    borderwidth=1, relief="solid", font=FONT_MAIN, padding=6)

        s.configure("TScrollbar", background=BORDER, troughcolor=BG, borderwidth=0, arrowcolor=SECONDARY)

    def _build_ui(self):

        # Header

        hdr = tk.Frame(self, bg=BG, pady=20, padx=24)

        hdr.pack(fill="x")

        ttk.Label(hdr, text="Fabric Deployment Scope", style="Title.TLabel").pack(side="left")

        self.scope_badge = ttk.Label(hdr, text="0 items", style="Sub.TLabel")

        self.scope_badge.pack(side="right")

        sep = tk.Frame(self, bg=BORDER, height=1)

        sep.pack(fill="x")

        # Body

        body = tk.Frame(self, bg=BG, padx=24, pady=16)

        body.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(body)

        self.notebook.pack(side="left", fill="both", expand=True)

        for type_key in sorted(self.items_by_type.keys()):

            self._build_tab(type_key)

        right = tk.Frame(body, bg=BG_CARD, padx=16, pady=12, relief="flat", borderwidth=1)

        right.pack(side="right", fill="y", padx=(16, 0), ipadx=0)

        self._build_scope_panel(right)

        # Footer

        footer = tk.Frame(self, bg=BG, pady=12, padx=24)

        footer.pack(fill="x")

        ttk.Button(footer, text="✓  Save & Deploy", style="Primary.TButton",

                   command=self._deploy).pack(side="right", padx=(8, 0))

        ttk.Button(footer, text="✓  Clear All", style="TButton",

                   command=self._clear_all_global).pack(side="right")

    def _build_tab(self, type_key: str):

        data, items = self.items_by_type[type_key], self.items_by_type[type_key]["items"]

        outer = ttk.Frame(self.notebook)

        self.notebook.add(outer, text=f"{data['display_type']}  ({len(items)})")

        toolbar = tk.Frame(outer, bg=BG_CARD, pady=10, padx=12, height=50)

        toolbar.pack(fill="x", side="top")

        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="🔍", bg=BG_CARD, fg=SECONDARY, font=FONT_MAIN).pack(side="left", padx=(0, 8))

        search_var = tk.StringVar()

        search_entry = ttk.Entry(toolbar, textvariable=search_var, width=24)

        search_entry.pack(side="left", padx=(0, 12))

        ttk.Button(toolbar, text="Select All", 

                   command=lambda k=type_key: self._select_all(k)).pack(side="left", padx=4)

        ttk.Button(toolbar, text="Clear All",

                   command=lambda k=type_key: self._clear_all(k)).pack(side="left", padx=4)

        count_lbl = tk.Label(toolbar, text=f"{len(items)} items", bg=BG_CARD, fg=FG_LIGHT, font=("Segoe UI", 9))

        count_lbl.pack(side="right", padx=8)

        canvas_frame = tk.Frame(outer, bg=BG)

        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0, bd=0)

        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")

        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)

        canvas.create_window((0, 0), window=inner, anchor="nw")

        self.check_vars[type_key] = {}

        row_widgets = []

        for item in items:

            var = tk.BooleanVar(value=item["full"] in self.items_in_scope)

            self.check_vars[type_key][item["full"]] = var

            row = tk.Frame(inner, bg=BG, pady=8, padx=8, cursor="hand2")

            row.pack(fill="x")

            # Custom checkbox with checkmark

            check_symbol = tk.Label(row, text="☐", bg=BG, fg=SECONDARY, font=("Segoe UI", 12), width=2)

            check_symbol.pack(side="left", padx=(0, 8))

            def make_toggle(full, v, symbol_widget):

                def toggle():

                    v.set(not v.get())

                    symbol_widget.config(text="✓" if v.get() else "☐", 

                                       fg=PRIMARY if v.get() else SECONDARY)

                    self._toggle_item(full, v)

                return toggle

            toggle_cmd = make_toggle(item["full"], var, check_symbol)

            row.bind("<Button-1>", lambda e, cmd=toggle_cmd: cmd())

            check_symbol.bind("<Button-1>", lambda e, cmd=toggle_cmd: cmd())

            name_lbl = tk.Label(row, text=item["name"], bg=BG, fg=FG, font=FONT_MAIN, cursor="hand2")

            name_lbl.pack(side="left")

            name_lbl.bind("<Button-1>", lambda e, cmd=toggle_cmd: cmd())

            tag = tk.Label(row, text=f".{data['display_type']}", bg=BG, fg=FG_LIGHT, font=("Segoe UI", 8))

            tag.pack(side="left", padx=(8, 0))

            check_symbol.config(text="✓" if var.get() else "☐", 

                              fg=PRIMARY if var.get() else SECONDARY)

            row_widgets.append((row, check_symbol, item["full"], item["name"], var))

        def _filter(*_):

            q = search_var.get().lower()

            visible = 0

            for row, symbol, full, name, var in row_widgets:

                show = q in name.lower() or q in full.lower()

                if show:

                    row.pack(fill="x")

                    visible += 1

                else:

                    row.pack_forget()

            count_lbl.config(text=f"{visible} / {len(items)} items")

        search_var.trace_add("write", _filter)

        inner.update_idletasks()

        canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _build_scope_panel(self, parent: tk.Frame):

        tk.Label(parent, text="SELECTED", bg=BG_CARD, fg=PRIMARY, font=FONT_HEAD).pack(anchor="w", pady=(0, 8))

        self.scope_listbox = tk.Listbox(parent, bg=BG_CARD, fg=FG, font=("Segoe UI", 9),

                                        selectbackground=PRIMARY, selectforeground="#ffffff",

                                        borderwidth=1, relief="solid", height=20, width=24)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.scope_listbox.yview)

        self.scope_listbox.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", padx=(4, 0))

        self.scope_listbox.pack(side="left", fill="both", expand=True, pady=(8, 8))

        ttk.Button(parent, text="Remove Selected", command=self._remove_selected_from_scope).pack(fill="x", pady=(0, 8))

    def _refresh_scope_panel(self):

        self.scope_listbox.delete(0, "end")

        for item in sorted(self.items_in_scope):

            self.scope_listbox.insert("end", item)

        count = len(self.items_in_scope)

        self.scope_badge.config(text=f"{count} item{'s' if count != 1 else ''}")

    def _toggle_item(self, full: str, var: tk.BooleanVar):

        (self.items_in_scope.add(full) if var.get() else self.items_in_scope.discard(full))

        self._refresh_scope_panel()

    def _select_all(self, type_key: str):

        for full, var in self.check_vars[type_key].items():

            var.set(True)

            self.items_in_scope.add(full)

        self._refresh_scope_panel()

    def _clear_all(self, type_key: str):

        for full, var in self.check_vars[type_key].items():

            var.set(False)

            self.items_in_scope.discard(full)

        self._refresh_scope_panel()

    def _clear_all_global(self):

        for type_key in self.check_vars:

            for full, var in self.check_vars[type_key].items():

                var.set(False)

        self.items_in_scope.clear()

        self._refresh_scope_panel()

    def _remove_selected_from_scope(self):

        selection = self.scope_listbox.curselection()

        if not selection:

            return

        for i in selection:

            full = self.scope_listbox.get(i)

            self.items_in_scope.discard(full)

            type_key = full.split(".", 1)[1].lower()

            if type_key in self.check_vars and full in self.check_vars[type_key]:

                self.check_vars[type_key][full].set(False)

        self._refresh_scope_panel()

    def _deploy(self):

        if not self.items_in_scope:

            messagebox.showwarning("Empty Scope", "Please select at least one item.")

            return

        self._show_review_window()

    def _show_review_window(self):

        review = tk.Toplevel(self)

        review.title("Review Deployment Scope")

        review.geometry("600x500")

        review.configure(bg=BG)

        hdr = tk.Frame(review, bg=PRIMARY, padx=20, pady=16)

        hdr.pack(fill="x")

        tk.Label(hdr, text="Review Selected Items", bg=PRIMARY, fg="#ffffff", font=FONT_BIG).pack(anchor="w")

        scope_list = sorted(self.items_in_scope)

        item_types = sorted({item.split(".")[1] for item in scope_list})

        summary = tk.Frame(review, bg=BG_CARD, padx=16, pady=12)

        summary.pack(fill="x", padx=16, pady=12)

        tk.Label(summary, text=f"Total Items: {len(scope_list)}", bg=BG_CARD, fg=PRIMARY, font=FONT_HEAD).pack(anchor="w", pady=4)

        tk.Label(summary, text=f"Types: {', '.join(item_types)}", bg=BG_CARD, fg=FG_LIGHT, font=FONT_MAIN).pack(anchor="w", pady=4)

        list_frame = tk.Frame(review, bg=BG)

        list_frame.pack(fill="both", expand=True, padx=16, pady=12)

        tk.Label(list_frame, text="Items for deployment:", bg=BG, fg=FG, font=FONT_HEAD).pack(anchor="w", pady=(0, 8))

        listbox = tk.Listbox(list_frame, bg=BG_CARD, fg=FG, font=("Segoe UI", 9),

                            selectbackground=PRIMARY, selectforeground="#ffffff",

                            borderwidth=1, relief="solid")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)

        listbox.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", padx=(4, 0))

        listbox.pack(side="left", fill="both", expand=True)

        for item in scope_list:

            listbox.insert("end", f"✓ {item}")

        btn_frame = tk.Frame(review, bg=BG, pady=12, padx=16)

        btn_frame.pack(fill="x")

        def confirm_deploy():

            try:

                save_manifest(scope_list)

                msg = f"✓ Manifest saved to:\n{MANIFEST_PATH}"

            except Exception as e:

                msg = f"⚠ Could not save manifest:\n{e}"

            messagebox.showinfo("Deployment Complete", 

                              f"Scope deployed successfully!\n\n{msg}")

            self.result = (item_types, scope_list)

            review.destroy()

        ttk.Button(btn_frame, text="✓  Confirm & Deploy", style="Primary.TButton",

                   command=confirm_deploy).pack(side="right", padx=(8, 0))

        ttk.Button(btn_frame, text="✓  Cancel", style="TButton",

                   command=review.destroy).pack(side="right")

if __name__ == "__main__":

    app = FabricDeployUI()

    app.mainloop()

    if hasattr(app, "result"):

        item_type_in_scope, items_in_scope = app.result

        print("\nitem_type_in_scope =", item_type_in_scope)

        print("items_in_scope     =", items_in_scope)
 
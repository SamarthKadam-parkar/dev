# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

2026-06-05 15:39:12,713 - INFO - fabric_cicd._common._validate_input - Relative directory path '.' resolved as 'C:\Users\samarth.kadam\dev'
2026-06-05 15:39:12,766 - INFO - fabric_cicd.fabric_workspace - 
2026-06-05 15:39:12,766 - INFO - fabric_cicd.fabric_workspace - [32m[1m####################################################################################################[0m
2026-06-05 15:39:12,766 - INFO - fabric_cicd.fabric_workspace - [32m[1m########## Validating Parameter File ###############################################################[0m
2026-06-05 15:39:12,766 - INFO - fabric_cicd.fabric_workspace - [32m[1m####################################################################################################[0m
2026-06-05 15:39:12,766 - INFO - fabric_cicd.fabric_workspace - 
2026-06-05 15:39:12,772 - INFO - fabric_cicd._parameter._parameter - Parameter file validation passed
2026-06-04 19:23:03,064 - INFO - fabric_cicd._common._validate_input - Relative directory path '.' resolved as 'C:\Users\samarth.kadam\dev'
2026-06-04 19:23:03,291 - INFO - fabric_cicd.fabric_workspace - 
2026-06-04 19:23:03,293 - INFO - fabric_cicd.fabric_workspace - [32m[1m####################################################################################################[0m
2026-06-04 19:23:03,293 - INFO - fabric_cicd.fabric_workspace - [32m[1m########## Validating Parameter File ###############################################################[0m
2026-06-04 19:23:03,294 - INFO - fabric_cicd.fabric_workspace - [32m[1m####################################################################################################[0m
2026-06-04 19:23:03,294 - INFO - fabric_cicd.fabric_workspace - 
2026-06-04 19:23:03,313 - INFO - fabric_cicd._parameter._parameter - Parameter file validation passed


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


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

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

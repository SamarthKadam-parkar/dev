# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# new Test notebook with changes 


# CELL ********************

def get_changed_items_vs_dev(repo_path: Path, known_items: set) -> list:
    """
    Returns Fabric items changed in the current branch vs origin/dev,
    filtered strictly against known Fabric item folders scanned from the repo.

    Each changed file lives inside a Fabric item folder, e.g.:
        MyReport.Report/report.json   ->  first component = MyReport.Report
        MyModel.SemanticModel/item.bim -> first component = MyModel.SemanticModel

    By checking only the first path component against known_items we avoid
    matching arbitrary dotted files like config.json or README.md.
    """
    repo = Repo(str(repo_path))
    try:
        repo.remotes.origin.fetch()
    except Exception:
        pass  # use cached remote refs if fetch fails

    diff_output = repo.git.diff("origin/dev..HEAD", "--name-only", "--diff-filter=ACMR")
    if not diff_output.strip():
        return []

    changed = set()
    for file_path in diff_output.strip().split("\n"):
        parts = Path(file_path).parts
        if parts and parts[0] in known_items:
            changed.add(parts[0])

    return sorted(changed)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

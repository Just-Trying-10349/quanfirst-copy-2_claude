# ============================================================
# QUANT RESEARCH AUTOMATION — LEVEL 5 (FIXED v3)
# ============================================================
#
# v3 ADDITION:
# Your leaderboard order is actually correct — GITHUB_RUN_ID strictly
# increases over time, so row order = true execution order. The
# confusion was not being able to see WHICH commit/push produced
# each row. This version adds two columns so you never have to guess:
#
#   - commit_sha:    the exact git commit that was checked out for
#                     that run (compare it directly against your
#                     GitHub commit history / `git log`)
#   - timestamp_utc: when the experiment actually ran
#
# Everything else (unique IDs via GITHUB_RUN_ID, skip-if-unchanged
# via parameters_hash) is unchanged from the previous fix.
# ============================================================

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

print("=" * 70)
print("QUANT RESEARCH EXPERIMENT — LEVEL 5 (FIXED v3)")
print("=" * 70)

# ------------------------------------------------------------
# STEP 1
# LOAD PARAMETERS
# ------------------------------------------------------------

parameters_file = Path("parameters.json")

with parameters_file.open("r", encoding="utf-8") as file:
    parameters = json.load(file)

parameters_hash = hashlib.sha256(
    json.dumps(parameters, sort_keys=True).encode("utf-8")
).hexdigest()

# ------------------------------------------------------------
# STEP 2
# SKIP IF PARAMETERS HAVEN'T CHANGED SINCE THE LAST EXPERIMENT
# ------------------------------------------------------------

leaderboard_file = Path("leaderboard.csv")
force_rerun = os.environ.get("FORCE_RERUN", "false").strip().lower() == "true"

FIELDNAMES = [
    "experiment_id",
    "return_percent",
    "profit",
    "status",
    "parameters_hash",
    "commit_sha",
    "timestamp_utc",
]

existing_rows = []
if leaderboard_file.exists():
    with leaderboard_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_rows = [row for row in reader if row.get("experiment_id")]

last_row = existing_rows[-1] if existing_rows else None
last_hash = last_row.get("parameters_hash") if last_row else None

if last_hash == parameters_hash and not force_rerun:
    print()
    print("parameters.json is unchanged since the last recorded experiment")
    print(f"({last_row['experiment_id']}). Skipping to avoid a duplicate row.")
    print("Set FORCE_RERUN=true to run anyway.")
    raise SystemExit(0)

# ------------------------------------------------------------
# STEP 3
# CREATE A GUARANTEED-UNIQUE EXPERIMENT ID
# ------------------------------------------------------------

experiment_folder = Path("experiments")
experiment_folder.mkdir(exist_ok=True)

github_run_id = os.environ.get("GITHUB_RUN_ID")
github_run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
commit_sha = os.environ.get("GITHUB_SHA", "unknown")
run_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if github_run_id:
    experiment_id = f"EXP-{github_run_id}-{github_run_attempt}"
else:
    experiment_id = f"EXP-LOCAL-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

print()
print("Experiment ID:")
print(experiment_id)
print(f"Commit SHA: {commit_sha}")
print(f"Timestamp (UTC): {run_timestamp}")

# ------------------------------------------------------------
# STEP 4
# CREATE EXPERIMENT DIRECTORY
# ------------------------------------------------------------

current_experiment = experiment_folder / experiment_id
current_experiment.mkdir(exist_ok=True)

print()
print("Experiment folder created:")
print(current_experiment)

# ------------------------------------------------------------
# STEP 5
# RUN SIMPLE EXPERIMENT
# ------------------------------------------------------------

capital = parameters["starting_capital"]
strategy_return = parameters["strategy_return"]

ending_capital = capital * (1 + strategy_return)
profit = ending_capital - capital
return_percent = (profit / capital) * 100

# ------------------------------------------------------------
# STEP 6
# SAVE RESULT
# ------------------------------------------------------------

result_file = current_experiment / "experiment_result.txt"

with result_file.open("w", encoding="utf-8") as file:
    file.write("QUANT RESEARCH EXPERIMENT\n")
    file.write("=" * 70 + "\n")
    file.write(f"Experiment ID: {experiment_id}\n")
    file.write(f"Commit SHA: {commit_sha}\n")
    file.write(f"Timestamp (UTC): {run_timestamp}\n\n")
    file.write("PARAMETERS\n")

    for key, value in parameters.items():
        file.write(f"{key}: {value}\n")

    file.write("\nRESULTS\n")
    file.write(f"Starting capital: {capital}\n")
    file.write(f"Ending capital: {ending_capital}\n")
    file.write(f"Profit: {profit}\n")
    file.write(f"Return: {return_percent}%\n")

# ------------------------------------------------------------
# STEP 7
# COPY IMPORTANT FILES
# ------------------------------------------------------------

shutil.copy("parameters.json", current_experiment / "parameters.json")
shutil.copy("hello.py", current_experiment / "hello.py")

# ------------------------------------------------------------
# STEP 8
# UPDATE LEADERBOARD
# ------------------------------------------------------------

rows = existing_rows
existing_ids = {row["experiment_id"] for row in rows}

if experiment_id not in existing_ids:
    rows.append(
        {
            "experiment_id": experiment_id,
            "return_percent": round(return_percent, 2),
            "profit": round(profit, 2),
            "status": "completed",
            "parameters_hash": parameters_hash,
            "commit_sha": commit_sha,
            "timestamp_utc": run_timestamp,
        }
    )
else:
    print(f"WARNING: {experiment_id} already in leaderboard.csv, skipping append.")

with leaderboard_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

print()
print("Leaderboard updated:")
print(leaderboard_file)

# ------------------------------------------------------------
# FINISH
# ------------------------------------------------------------

print()
print("=" * 70)
print("EXPERIMENT COMPLETE")
print("=" * 70)
print()
print("Saved:")
print(current_experiment)

# ============================================================
# QUANT RESEARCH AUTOMATION — LEVEL 5
# EXPERIMENT MEMORY SYSTEM
# ============================================================
#
# PURPOSE:
#
# Every successful experiment receives a clean sequential ID:
#
#     EXP-0001
#     EXP-0002
#     EXP-0003
#     ...
#
# The system also records:
#
#     - strategy result
#     - profit
#     - parameters
#     - exact Python code
#     - parameter hash
#     - Git commit SHA
#     - East Africa Time (UTC+3)
#
# IMPORTANT:
#
# Experiment numbers are determined from the EXISTING
# experiment folders, not from GitHub Run IDs.
#
# This prevents EXP-0001 from being recreated after
# leaderboard rows are manually deleted.
#
# ============================================================


import csv
import hashlib
import json
import os
import re
import shutil

from datetime import datetime, timezone, timedelta
from pathlib import Path


print("=" * 70)
print("QUANT RESEARCH EXPERIMENT — LEVEL 5")
print("=" * 70)


# ============================================================
# STEP 1
# LOAD PARAMETERS
# ============================================================

parameters_file = Path("parameters.json")


with parameters_file.open(
    "r",
    encoding="utf-8"
) as file:

    parameters = json.load(file)


print()
print("Parameters loaded successfully.")


# ============================================================
# STEP 2
# CREATE PARAMETERS HASH
# ============================================================
#
# The hash allows us to determine whether the parameters
# are identical to the last recorded experiment.
#
# This helps prevent accidental duplicate experiments.
#
# ============================================================

parameters_hash = hashlib.sha256(
    json.dumps(
        parameters,
        sort_keys=True
    ).encode("utf-8")
).hexdigest()


print()
print("Parameters hash:")
print(parameters_hash)


# ============================================================
# STEP 3
# LOAD LEADERBOARD HISTORY
# ============================================================

leaderboard_file = Path("leaderboard.csv")


FIELDNAMES = [
    "experiment_id",
    "return_percent",
    "profit",
    "status",
    "parameters_hash",
    "commit_sha",
    "timestamp_eat",
]


existing_rows = []


if leaderboard_file.exists():

    with leaderboard_file.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row.get("experiment_id"):

                existing_rows.append(row)


print()
print("Previous leaderboard records:")
print(len(existing_rows))


# ============================================================
# STEP 4
# CHECK FOR DUPLICATE PARAMETERS
# ============================================================
#
# Unless FORCE_RERUN=true, the same parameters will not
# automatically create another experiment.
#
# ============================================================

force_rerun = (
    os.environ
    .get("FORCE_RERUN", "false")
    .strip()
    .lower()
    == "true"
)


last_row = (
    existing_rows[-1]
    if existing_rows
    else None
)


last_hash = (
    last_row.get("parameters_hash")
    if last_row
    else None
)


if (
    last_hash == parameters_hash
    and not force_rerun
):

    print()
    print("=" * 70)
    print("DUPLICATE PARAMETERS DETECTED")
    print("=" * 70)

    print()
    print(
        "These parameters were already used by:"
    )

    print(
        last_row["experiment_id"]
    )

    print()
    print(
        "No new experiment was created."
    )

    print()
    print(
        "To deliberately run the same parameters again,"
    )

    print(
        "use FORCE_RERUN=true."
    )

    print()

    raise SystemExit(0)


# ============================================================
# STEP 5
# CREATE EXPERIMENT ROOT DIRECTORY
# ============================================================

experiment_folder = Path("experiments")


experiment_folder.mkdir(
    exist_ok=True
)


# ============================================================
# STEP 6
# FIND HIGHEST EXISTING EXPERIMENT NUMBER
# ============================================================
#
# IMPORTANT:
#
# We look directly at the experiment folders.
#
# Example:
#
# experiments/
#     EXP-0001/
#     EXP-0002/
#     EXP-0007/
#
# The next experiment becomes:
#
#     EXP-0008
#
# This means deleting a leaderboard row will NOT cause
# an old experiment number to be reused.
#
# ============================================================

highest_experiment_number = 0


experiment_pattern = re.compile(
    r"^EXP-(\d+)$"
)


for item in experiment_folder.iterdir():

    if not item.is_dir():

        continue


    match = experiment_pattern.match(
        item.name
    )


    if match:

        number = int(
            match.group(1)
        )


        if number > highest_experiment_number:

            highest_experiment_number = number


# ============================================================
# STEP 7
# CREATE NEXT EXPERIMENT ID
# ============================================================

experiment_number = (
    highest_experiment_number + 1
)


experiment_id = (
    f"EXP-{experiment_number:04d}"
)


print()
print("New Experiment ID:")
print(experiment_id)


# ============================================================
# STEP 8
# GITHUB INFORMATION
# ============================================================

commit_sha = os.environ.get(
    "GITHUB_SHA",
    "local"
)


github_run_id = os.environ.get(
    "GITHUB_RUN_ID",
    "local"
)


print()
print("Git commit:")
print(commit_sha)


print()
print("GitHub run ID:")
print(github_run_id)


# ============================================================
# STEP 9
# EAST AFRICA TIME
# ============================================================
#
# Kenya uses UTC+3.
#
# We explicitly create a UTC+3 timezone rather than depending
# on the temporary GitHub runner's local timezone.
#
# ============================================================

east_africa_timezone = timezone(
    timedelta(hours=3)
)


run_timestamp = datetime.now(
    east_africa_timezone
).strftime(
    "%Y-%m-%dT%H:%M:%S%z"
)


print()
print("East Africa Time:")
print(run_timestamp)


# ============================================================
# STEP 10
# CREATE EXPERIMENT DIRECTORY
# ============================================================

current_experiment = (
    experiment_folder /
    experiment_id
)


# Safety check.
#
# This should never happen because we determined the next ID
# from the existing folders.
#
# But if it somehow does, we stop rather than overwrite data.

if current_experiment.exists():

    raise RuntimeError(
        f"SAFETY ERROR: "
        f"{current_experiment} already exists. "
        f"Experiment data will NOT be overwritten."
    )


current_experiment.mkdir()


print()
print("Experiment folder created:")
print(current_experiment)


# ============================================================
# STEP 11
# RUN SIMPLE EXPERIMENT
# ============================================================

capital = parameters[
    "starting_capital"
]


strategy_return = parameters[
    "strategy_return"
]


ending_capital = (
    capital *
    (1 + strategy_return)
)


profit = (
    ending_capital -
    capital
)


return_percent = (
    profit /
    capital
) * 100


print()
print("Experiment result:")
print(
    f"Return: {return_percent}%"
)

print(
    f"Profit: {profit}"
)


# ============================================================
# STEP 12
# SAVE RESULT
# ============================================================

result_file = (
    current_experiment /
    "experiment_result.txt"
)


with result_file.open(
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "QUANT RESEARCH EXPERIMENT\n"
    )

    file.write(
        "=" * 70 +
        "\n"
    )

    file.write(
        f"Experiment ID: "
        f"{experiment_id}\n"
    )

    file.write(
        f"GitHub Run ID: "
        f"{github_run_id}\n"
    )

    file.write(
        f"Commit SHA: "
        f"{commit_sha}\n"
    )

    file.write(
        f"East Africa Time: "
        f"{run_timestamp}\n\n"
    )


    file.write(
        "PARAMETERS\n"
    )

    file.write(
        "-" * 70 +
        "\n"
    )


    for key, value in parameters.items():

        file.write(
            f"{key}: {value}\n"
        )


    file.write("\n")


    file.write(
        "RESULTS\n"
    )

    file.write(
        "-" * 70 +
        "\n"
    )

    file.write(
        f"Starting capital: "
        f"{capital}\n"
    )

    file.write(
        f"Ending capital: "
        f"{ending_capital}\n"
    )

    file.write(
        f"Profit: "
        f"{profit}\n"
    )

    file.write(
        f"Return: "
        f"{return_percent}%\n"
    )


# ============================================================
# STEP 13
# SAVE PARAMETERS AND PYTHON CODE
# ============================================================

shutil.copy(
    "parameters.json",
    current_experiment /
    "parameters.json"
)


shutil.copy(
    "hello.py",
    current_experiment /
    "hello.py"
)


print()
print("Saved experiment files:")

print(
    current_experiment /
    "experiment_result.txt"
)

print(
    current_experiment /
    "parameters.json"
)

print(
    current_experiment /
    "hello.py"
)


# ============================================================
# STEP 14
# UPDATE LEADERBOARD
# ============================================================

rows = existing_rows.copy()


rows.append(
    {
        "experiment_id": experiment_id,

        "return_percent":
            round(
                return_percent,
                2
            ),

        "profit":
            round(
                profit,
                2
            ),

        "status":
            "completed",

        "parameters_hash":
            parameters_hash,

        "commit_sha":
            commit_sha,

        "timestamp_eat":
            run_timestamp,
    }
)


# ============================================================
# STEP 15
# WRITE CLEAN LEADERBOARD
# ============================================================

with leaderboard_file.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=FIELDNAMES
    )

    writer.writeheader()

    writer.writerows(rows)


print()
print("Leaderboard updated:")
print(leaderboard_file)


# ============================================================
# STEP 16
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("EXPERIMENT COMPLETE")
print("=" * 70)

print()

print(
    f"Experiment ID: {experiment_id}"
)

print(
    f"Return: {return_percent}%"
)

print(
    f"Profit: {profit}"
)

print(
    f"Time: {run_timestamp}"
)

print()

print("Saved:")
print(current_experiment)

print()

print(
    "The experiment number was generated from "
    "existing experiment folders."
)

print(
    "Previous experiment folders will never be "
    "reused automatically."
)

print("=" * 70)

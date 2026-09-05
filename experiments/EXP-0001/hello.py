# ============================================================
# QUANT RESEARCH AUTOMATION — LEVEL 5
# ============================================================
#
# EXPERIMENT MEMORY SYSTEM — SEQUENTIAL IDs
#
# This version combines:
#
# 1. Simple experiment IDs:
#
#       EXP-0001
#       EXP-0002
#       EXP-0003
#
# 2. Duplicate protection:
#
#       Do not record the same parameters twice
#       unless FORCE_RERUN=true
#
# 3. Research traceability:
#
#       commit SHA
#       timestamp
#       parameters hash
#
# 4. Experiment preservation:
#
#       experiments/EXP-0001/
#           hello.py
#           parameters.json
#           experiment_result.txt
#
#
# IMPORTANT:
#
# The experiment number is NOT based on GITHUB_RUN_ID.
#
# Instead we find the highest existing EXP number and add 1.
#
# This keeps the experiment numbering simple and human-readable.
#
# ============================================================


import csv
import hashlib
import json
import os
import re
import shutil

from datetime import datetime, timezone
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


# ------------------------------------------------------------
# Create a fingerprint of the parameters.
#
# This allows us to recognize:
#
# "Have I already tested these exact parameters?"
#
# ------------------------------------------------------------

parameters_hash = hashlib.sha256(
    json.dumps(
        parameters,
        sort_keys=True
    ).encode("utf-8")
).hexdigest()


print()
print("Parameters loaded.")

print(
    "Parameters hash:"
)

print(parameters_hash)


# ============================================================
# STEP 2
# LOAD EXISTING EXPERIMENT HISTORY
# ============================================================


experiment_folder = Path("experiments")

experiment_folder.mkdir(
    exist_ok=True
)


leaderboard_file = Path(
    "leaderboard.csv"
)


force_rerun = (
    os.environ.get(
        "FORCE_RERUN",
        "false"
    )
    .strip()
    .lower()
    == "true"
)


FIELDNAMES = [

    "experiment_id",

    "return_percent",

    "profit",

    "status",

    "parameters_hash",

    "commit_sha",

    "timestamp_utc",
]


# ------------------------------------------------------------
# Read existing leaderboard rows.
# ------------------------------------------------------------

existing_rows = []


if leaderboard_file.exists():

    with leaderboard_file.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row.get(
                "experiment_id"
            ):

                existing_rows.append(
                    row
                )


# ============================================================
# STEP 3
# PREVENT DUPLICATE PARAMETER EXPERIMENTS
# ============================================================
#
# If these exact parameters have already been tested,
# do not create another experiment.
#
# EXCEPTION:
#
# FORCE_RERUN=true
#
# allows us to deliberately repeat the experiment.
#
# ============================================================


already_tested = False

previous_experiment_id = None


for row in existing_rows:

    if row.get(
        "parameters_hash"
    ) == parameters_hash:

        already_tested = True

        previous_experiment_id = (
            row.get("experiment_id")
        )

        break


if already_tested and not force_rerun:

    print()
    print("=" * 70)

    print(
        "DUPLICATE PARAMETERS DETECTED"
    )

    print("=" * 70)

    print()

    print(
        "These parameters have already"
        " been tested."
    )

    print()

    print(
        "Existing experiment:"
    )

    print(
        previous_experiment_id
    )

    print()

    print(
        "No new experiment will be created."
    )

    print()

    print(
        "To deliberately repeat the"
        " experiment, use:"
    )

    print()

    print(
        "FORCE_RERUN=true"
    )

    print()

    raise SystemExit(0)


# ============================================================
# STEP 4
# CREATE SEQUENTIAL EXPERIMENT ID
# ============================================================
#
# We search BOTH:
#
#   1. leaderboard.csv
#   2. experiments/
#
# This is important.
#
# Suppose someone deletes EXP-0005 from the CSV but the
# experiment folder still exists.
#
# We should NOT create another EXP-0005.
#
# ============================================================


highest_experiment_number = 0


# ------------------------------------------------------------
# Check IDs in leaderboard.csv
# ------------------------------------------------------------

for row in existing_rows:

    experiment_id = row.get(
        "experiment_id",
        ""
    ).strip()


    match = re.fullmatch(
        r"EXP-(\d+)",
        experiment_id
    )


    if match:

        number = int(
            match.group(1)
        )


        if number > highest_experiment_number:

            highest_experiment_number = number


# ------------------------------------------------------------
# Check IDs in experiments/ folders
# ------------------------------------------------------------

if experiment_folder.exists():

    for folder in experiment_folder.iterdir():

        if not folder.is_dir():

            continue


        match = re.fullmatch(
            r"EXP-(\d+)",
            folder.name
        )


        if match:

            number = int(
                match.group(1)
            )


            if number > highest_experiment_number:

                highest_experiment_number = number


# ------------------------------------------------------------
# Create next sequential ID
# ------------------------------------------------------------

experiment_number = (
    highest_experiment_number + 1
)


experiment_id = (
    f"EXP-{experiment_number:04d}"
)


# ============================================================
# STEP 5
# GET RESEARCH TRACE INFORMATION
# ============================================================


commit_sha = os.environ.get(
    "GITHUB_SHA",
    "local"
)


run_timestamp = (
    datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
)


print()
print("=" * 70)

print("NEW EXPERIMENT")

print("=" * 70)

print()

print(
    "Experiment ID:"
)

print(
    experiment_id
)

print()

print(
    "Commit SHA:"
)

print(
    commit_sha
)

print()

print(
    "Timestamp (UTC):"
)

print(
    run_timestamp
)


# ============================================================
# STEP 6
# CREATE EXPERIMENT DIRECTORY
# ============================================================


current_experiment = (
    experiment_folder /
    experiment_id
)


current_experiment.mkdir(
    exist_ok=False
)


print()

print(
    "Experiment folder created:"
)

print(
    current_experiment
)


# ============================================================
# STEP 7
# RUN THE CURRENT EXPERIMENT
# ============================================================
#
# THIS IS STILL OUR SIMPLE DEMONSTRATION EXPERIMENT.
#
# Later this section becomes:
#
#     market data
#          ↓
#     indicators
#          ↓
#     strategy
#          ↓
#     VectorBT
#          ↓
#     backtest
#          ↓
#     metrics
#
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


# ============================================================
# STEP 8
# SAVE EXPERIMENT RESULT
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
        f"Commit SHA: "
        f"{commit_sha}\n"
    )

    file.write(
        f"Timestamp (UTC): "
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


    file.write(
        "\nRESULTS\n"
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
# STEP 9
# PRESERVE THE EXACT CODE AND PARAMETERS
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


# ============================================================
# STEP 10
# UPDATE LEADERBOARD
# ============================================================


rows = existing_rows


rows.append(
    {

        "experiment_id":
            experiment_id,

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

        "timestamp_utc":
            run_timestamp,

    }
)


# ------------------------------------------------------------
# Rewrite leaderboard cleanly.
# ------------------------------------------------------------

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

    writer.writerows(
        rows
    )


print()

print(
    "Leaderboard updated:"
)

print(
    leaderboard_file
)


# ============================================================
# STEP 11
# FINAL MESSAGE
# ============================================================


print()

print("=" * 70)

print(
    "EXPERIMENT COMPLETE"
)

print("=" * 70)

print()

print(
    "Experiment:"
)

print(
    experiment_id
)

print()

print(
    "Return:"
)

print(
    f"{return_percent}%"
)

print()

print(
    "Profit:"
)

print(
    profit
)

print()

print(
    "Saved:"
)

print(
    current_experiment
)

print()

print(
    "This experiment can now be"
    " reproduced from its saved:"
)

print(
    "- hello.py"
)

print(
    "- parameters.json"
)

print(
    "- experiment_result.txt"
)

print("=" * 70)

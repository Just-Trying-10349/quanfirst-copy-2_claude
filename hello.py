# ============================================================
# QUANT RESEARCH AUTOMATION — LEVEL 9
# ============================================================
#
# PURPOSE:
#
# Prepare experiment results for the GitHub → Kaggle pipeline.
#
# This version preserves:
#
# 1. EXP-0001, EXP-0002, EXP-0003 style IDs
# 2. Net return in the experiment filename
# 3. East Africa Time (UTC+3)
# 4. Parameters
# 5. Exact Python source code
# 6. Experiment result
# 7. Leaderboard history
# 8. Duplicate protection
# 9. Git commit information
# 10. Kaggle transfer files
#
# CURRENT FLOW:
#
# parameters.json
#        ↓
# hello.py
#        ↓
# experiment
#        ↓
# result + parameters + code
#        ↓
# leaderboard
#        ↓
# Kaggle transfer package
#
# FUTURE:
#
# GitHub
#    ↓
# Kaggle
#    ↓
# heavy backtesting
#    ↓
# AI analysis
#    ↓
# strategy improvement
#
# ============================================================


import csv
import hashlib
import json
import os
import shutil

from datetime import datetime, timezone, timedelta

from pathlib import Path


print("=" * 70)
print("QUANT RESEARCH EXPERIMENT — LEVEL 9")
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


# Create a hash of the parameters.
#
# This lets the system recognize whether the parameters
# are identical to the previous experiment.

parameters_hash = hashlib.sha256(
    json.dumps(
        parameters,
        sort_keys=True
    ).encode("utf-8")
).hexdigest()


# ============================================================
# STEP 2
# TIME INFORMATION
# ============================================================

utc_now = datetime.now(timezone.utc)

east_africa_time = utc_now + timedelta(hours=3)

timestamp_utc = utc_now.strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

timestamp_eat = east_africa_time.strftime(
    "%Y-%m-%dT%H:%M:%S+03:00"
)


# ============================================================
# STEP 3
# READ EXISTING LEADERBOARD
# ============================================================

leaderboard_file = Path(
    "leaderboard.csv"
)


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

print(
    "Previous experiments found:"
)

print(
    len(existing_rows)
)


# ============================================================
# STEP 4
# PREVENT DUPLICATE PARAMETERS
# ============================================================

force_rerun = (
    os.environ
    .get(
        "FORCE_RERUN",
        "false"
    )
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
    last_row.get(
        "parameters_hash"
    )
    if last_row
    else None
)


if (
    last_hash == parameters_hash
    and not force_rerun
):

    print()

    print(
        "The parameters are identical "
        "to the previous experiment."
    )

    print()

    print(
        "No duplicate experiment will be created."
    )

    print()

    print(
        "Use FORCE_RERUN=true if you "
        "deliberately want to run it again."
    )

    raise SystemExit(0)


# ============================================================
# STEP 5
# CREATE EXPERIMENT ID
# ============================================================
#
# We deliberately use:
#
# EXP-0001
# EXP-0002
# EXP-0003
#
# rather than GitHub's very long run ID.
#
# ============================================================

highest_id = 0


for row in existing_rows:

    experiment_id_value = row.get(
        "experiment_id",
        ""
    )

    if experiment_id_value.startswith(
        "EXP-"
    ):

        try:

            number = int(
                experiment_id_value.replace(
                    "EXP-",
                    ""
                )
            )

            if number > highest_id:

                highest_id = number

        except ValueError:

            pass


experiment_number = (
    highest_id + 1
)


experiment_id = (
    f"EXP-{experiment_number:04d}"
)


print()

print("Experiment ID:")

print(experiment_id)


# ============================================================
# STEP 6
# GITHUB INFORMATION
# ============================================================

commit_sha = os.environ.get(
    "GITHUB_SHA",
    "unknown"
)


print()

print("Commit SHA:")

print(commit_sha)


print()

print("UTC:")

print(timestamp_utc)


print()

print("East Africa Time:")

print(timestamp_eat)


# ============================================================
# STEP 7
# CREATE EXPERIMENT DIRECTORY
# ============================================================

experiment_folder = Path(
    "experiments"
)


experiment_folder.mkdir(
    exist_ok=True
)


current_experiment = (
    experiment_folder /
    experiment_id
)


# exist_ok=True prevents the workflow
# from crashing if the directory already exists.

current_experiment.mkdir(
    exist_ok=True
)


print()

print("Experiment directory:")

print(current_experiment)


# ============================================================
# STEP 8
# RUN EXPERIMENT
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

print("RESULT")

print("-" * 70)

print(
    f"Starting capital: {capital}"
)

print(
    f"Strategy return: {strategy_return}"
)

print(
    f"Profit: {profit}"
)

print(
    f"Return: {return_percent}%"
)


# ============================================================
# STEP 9
# CREATE NET-RETURN FILENAME
# ============================================================

# Example:
#
# EXP-0009_10.0.csv
# EXP-0009_10.0.json
#
# This gives us both:
#
# unique experiment ID
# +
# easily visible return
#
# ============================================================

net_return_string = (
    f"{return_percent:.2f}"
)


csv_filename = (
    f"{experiment_id}_"
    f"{net_return_string}.csv"
)


json_filename = (
    f"{experiment_id}_"
    f"{net_return_string}.json"
)


# ============================================================
# STEP 10
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
        f"UTC: "
        f"{timestamp_utc}\n"
    )

    file.write(
        f"East Africa Time: "
        f"{timestamp_eat}\n\n"
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
# STEP 11
# COPY CODE AND PARAMETERS
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
# STEP 12
# CREATE KAGGLE TRANSFER DIRECTORY
# ============================================================

kaggle_folder = Path(
    "kaggle_transfer"
)


kaggle_folder.mkdir(
    exist_ok=True
)


# ============================================================
# STEP 13
# CREATE CSV FOR KAGGLE
# ============================================================

transfer_csv = (
    kaggle_folder /
    csv_filename
)


with transfer_csv.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "experiment_id",
            "return_percent",
            "profit",
            "status",
            "parameters_hash",
            "commit_sha",
            "timestamp_utc",
            "timestamp_eat"
        ]
    )

    writer.writerow(
        [
            experiment_id,
            round(return_percent, 2),
            round(profit, 2),
            "completed",
            parameters_hash,
            commit_sha,
            timestamp_utc,
            timestamp_eat
        ]
    )


# ============================================================
# STEP 14
# CREATE JSON FOR KAGGLE
# ============================================================

transfer_json = (
    kaggle_folder /
    json_filename
)


kaggle_record = {

    "experiment_id":
        experiment_id,

    "return_percent":
        round(return_percent, 2),

    "profit":
        round(profit, 2),

    "status":
        "completed",

    "parameters":
        parameters,

    "parameters_hash":
        parameters_hash,

    "commit_sha":
        commit_sha,

    "timestamp_utc":
        timestamp_utc,

    "timestamp_eat":
        timestamp_eat
}


with transfer_json.open(
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        kaggle_record,
        file,
        indent=4
    )


# ============================================================
# STEP 15
# UPDATE LEADERBOARD
# ============================================================

# IMPORTANT:
#
# This field list includes timestamp_eat.
#
# This is the exact problem that caused your
# previous ValueError.
#
# ============================================================

FIELDNAMES = [

    "experiment_id",

    "return_percent",

    "profit",

    "status",

    "parameters_hash",

    "commit_sha",

    "timestamp_utc",

    "timestamp_eat"

]


new_row = {

    "experiment_id":
        experiment_id,

    "return_percent":
        round(return_percent, 2),

    "profit":
        round(profit, 2),

    "status":
        "completed",

    "parameters_hash":
        parameters_hash,

    "commit_sha":
        commit_sha,

    "timestamp_utc":
        timestamp_utc,

    "timestamp_eat":
        timestamp_eat

}


existing_ids = {

    row.get(
        "experiment_id"
    )
    for row in existing_rows

}


if experiment_id not in existing_ids:

    existing_rows.append(
        new_row
    )


# ============================================================
# WRITE CLEAN LEADERBOARD
# ============================================================

with leaderboard_file.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=FIELDNAMES,
        extrasaction="ignore"
    )

    writer.writeheader()

    writer.writerows(
        existing_rows
    )


# ============================================================
# STEP 16
# FINAL OUTPUT
# ============================================================

print()

print("=" * 70)

print(
    "EXPERIMENT COMPLETE"
)

print("=" * 70)

print()

print(
    "Saved experiment:"
)

print(
    current_experiment
)

print()

print(
    "Kaggle CSV:"
)

print(
    transfer_csv
)

print()

print(
    "Kaggle JSON:"
)

print(
    transfer_json
)

print()

print(
    "Leaderboard:"
)

print(
    leaderboard_file
)

print()

print(
    "Level 9 GitHub → Kaggle "
    "transfer package prepared successfully."
)

print("=" * 70)

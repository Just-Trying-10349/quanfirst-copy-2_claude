# ============================================================
# QUANT RESEARCH AUTOMATION — LEVEL 9
# GITHUB → KAGGLE
# ============================================================
#
# PURPOSE:
#
# This program proves that GitHub can send an experiment
# to Kaggle and have Kaggle execute Python code.
#
# This is deliberately NOT VectorBT yet.
#
# We are testing the connection first.
#
# ============================================================

import json
from pathlib import Path


print("=" * 70)
print("QUANT RESEARCH AUTOMATION — LEVEL 9")
print("KAGGLE RESEARCH ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# STEP 1
# LOAD PARAMETERS
# ------------------------------------------------------------

parameters_file = Path("parameters.json")


if parameters_file.exists():

    with parameters_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        parameters = json.load(file)

else:

    # Temporary fallback.
    #
    # This allows us to test the Kaggle notebook by itself.
    # Later GitHub will provide the real parameters.

    parameters = {

        "starting_capital": 10000,

        "strategy_return": 0.25
    }


# ------------------------------------------------------------
# STEP 2
# DISPLAY RECEIVED PARAMETERS
# ------------------------------------------------------------

print()
print("PARAMETERS RECEIVED BY KAGGLE")
print("-" * 70)

print(
    "Starting capital:",
    parameters["starting_capital"]
)

print(
    "Strategy return:",
    parameters["strategy_return"]
)


# ------------------------------------------------------------
# STEP 3
# RUN EXPERIMENT
# ------------------------------------------------------------

starting_capital = parameters[
    "starting_capital"
]

strategy_return = parameters[
    "strategy_return"
]


profit = (
    starting_capital *
    strategy_return
)


ending_capital = (
    starting_capital +
    profit
)


net_return_percent = (
    strategy_return *
    100
)


# ------------------------------------------------------------
# STEP 4
# DISPLAY RESULTS
# ------------------------------------------------------------

print()
print("KAGGLE EXPERIMENT RESULT")
print("-" * 70)

print(
    f"Starting capital: ${starting_capital:,.2f}"
)

print(
    f"Net return: {net_return_percent:.2f}%"
)

print(
    f"Profit: ${profit:,.2f}"
)

print(
    f"Ending capital: ${ending_capital:,.2f}"
)


# ------------------------------------------------------------
# STEP 5
# CREATE RESULT FILE
# ------------------------------------------------------------

# We use the return in the filename because it makes
# the experiment easy to identify visually.

return_text = (
    f"{net_return_percent:g}"
)


result_filename = (
    f"net_return_{return_text}pct.json"
)


result = {

    "starting_capital":
        starting_capital,

    "net_return_percent":
        round(
            net_return_percent,
            2
        ),

    "profit":
        round(
            profit,
            2
        ),

    "ending_capital":
        round(
            ending_capital,
            2
        ),

    "status":
        "completed"
}


result_file = Path(
    result_filename
)


with result_file.open(
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        result,
        file,
        indent=4
    )


print()
print("RESULT FILE CREATED:")
print(result_file)


# ------------------------------------------------------------
# FINISH
# ------------------------------------------------------------

print()
print("=" * 70)
print("KAGGLE LEVEL 9 TEST COMPLETE")
print("=" * 70)

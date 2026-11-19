"""
Configuration for the Fault Simulation Framework.
"""

import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def find_atalanta_directory():
    """Locate an ATALANTA installation from the environment or workspace."""
    configured = os.getenv("ATALANTA_DIR")
    candidates = []
    if configured:
        candidates.append(Path(configured).expanduser())

    for directory in PROJECT_DIR.parents:
        candidates.append(directory / "Atalanta-master")
        candidates.append(directory / "atalanta")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return None


ATALANTA_DIR = find_atalanta_directory()
if ATALANTA_DIR:
    executable_name = "atalanta.exe" if os.name == "nt" else "atalanta"
    ATALANTA_EXEC = str(ATALANTA_DIR / executable_name)
    CIRCUITS_DIR = str(ATALANTA_DIR / "data")
else:
    ATALANTA_EXEC = "atalanta"
    CIRCUITS_DIR = str(PROJECT_DIR / "data")

RESULTS_DIR = str(PROJECT_DIR / "results")
LOGS_DIR = str(PROJECT_DIR / "logs")
REPORTS_DIR = str(PROJECT_DIR / "reports")

# Circuits to test (starting with smaller ones for faster testing)
CIRCUITS = [
    "s9234tc.bench",
    "s13207tc.bench",
    "s15850tc.bench",
    "s35932tc.bench",
    "s38417tc.bench",
    "s38584tc.bench"
]

# ATPG Parameters to experiment with
EXPERIMENTS = [
    {
        "name": "default",
        "options": "",
        "description": "Default ATALANTA settings"
    },
    {
        "name": "no_random",
        "options": "-r 0",
        "description": "No random pattern generation"
    },
    {
        "name": "high_backtrack",
        "options": "-b 20 -B 40",
        "description": "Increased backtrack limits"
    },
    {
        "name": "no_compaction",
        "options": "-N",
        "description": "No test compaction"
    }
]

# Subset for quick testing (you can change this)
QUICK_TEST_CIRCUITS = ["s9234tc.bench", "s13207tc.bench"]
QUICK_TEST_EXPERIMENTS = [EXPERIMENTS[0]]  # Just default settings

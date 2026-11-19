# Fault Simulation Framework

A Python automation framework for stuck-at fault simulation and ATPG experimentation using the ATALANTA automatic test pattern generator.

## Features

- Batch execution across BENCH/ISCAS-style circuits
- Configurable backtracking and test-compaction experiments
- ATPG log parsing and fault-coverage analysis
- JSON, CSV, and text result generation
- Tkinter GUI for interactive execution
- Matplotlib-based result visualization

## Project Structure

```text
.
|-- run_experiments.py       # Batch experiment runner
|-- fault_simulation_gui.py  # Desktop GUI
|-- analyze_results.py       # Result analysis
|-- atalanta_parser.py       # ATALANTA output parser
|-- config.py                # Portable path and experiment configuration
|-- bench_to_logisim.py      # BENCH conversion utility
|-- generate_flowchart.py    # Architecture chart generator
|-- *.test                   # Experiment circuit netlists
|-- images/                  # Paper and presentation figures
|-- paper.tex / paper.pdf    # IEEE-format project report
```

## Requirements

- Python 3.8+
- Tkinter for the GUI
- Matplotlib
- A compiled ATALANTA executable

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## ATALANTA Setup

Set `ATALANTA_DIR` to the directory containing the executable and `data/` folder:

```powershell
$env:ATALANTA_DIR = "C:\path\to\Atalanta-master"
python run_experiments.py --quick
```

The executable is detected as `atalanta.exe` on Windows and `atalanta` on Unix-like systems. The framework also searches its parent directories for `Atalanta-master`.

## Usage

Run the quick experiment set:

```powershell
python run_experiments.py --quick
```

Run the full experiment set:

```powershell
python run_experiments.py
```

Analyze the latest saved results:

```powershell
python analyze_results.py
```

Generate the GUI:

```powershell
python fault_simulation_gui.py
```

Generated results are written to `results/`, execution logs to `logs/`, and reports to `reports/`. These directories are ignored by Git.

## Notes

ATALANTA is distributed for teaching and research use. Its license terms and citation requirements should be reviewed before redistribution or commercial use.

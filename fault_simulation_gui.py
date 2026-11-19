#!/usr/bin/env python3
"""
Phase 2: Fault Simulation GUI - File Selection + ATALANTA Execution
Simple Tkinter interface to select .bench files and run ATALANTA
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import subprocess
import threading
import time
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


class FaultSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fault Simulation GUI (ATALANTA)")
        self.root.geometry("900x700")
        
        # List to store selected file paths
        self.selected_files = []
        
        # Default directory for file browsing
        self.circuits_dir = "/home/karthik/Desktop/DFT EL/Atalanta-master/data"
        
        # Path to ATALANTA executable
        self.atalanta_path = "/home/karthik/Desktop/DFT EL/Atalanta-master/atalanta"
        
        # Output directory for saving ATALANTA results
        self.outputs_dir = "/home/karthik/Desktop/DFT EL/Fault_Simulation_Framework/atalanta_outputs"
        os.makedirs(self.outputs_dir, exist_ok=True)
        
        # Track last output file and parsed metrics
        self.last_output_file = None
        self.current_metrics = None
        
        # Flag to track if ATALANTA is running
        self.is_running = False
        
        # ATALANTA option variables
        self.enable_random_patterns = tk.BooleanVar(value=False)
        self.random_pattern_limit = tk.StringVar(value="16")
        self.enable_compaction = tk.BooleanVar(value=True)
        self.disable_compaction = tk.BooleanVar(value=False)
        self.backtrack_limit = tk.StringVar(value="10")
        
        # Timer and progress variables
        self.start_time = None
        self.timer_job = None
        self.total_patterns = 0
        self.current_patterns = 0
        self.process = None  # Track the running process
        
        # Batch execution variables
        self.batch_files = []
        self.is_batch_running = False
        self.current_batch_index = 0
        self.batch_results = []
        self.batch_output_dir = None
        
        # Setup the UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        
        # Main heading
        heading = tk.Label(
            self.root,
            text="Fault Simulation Framework",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        heading.pack(fill=tk.X)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_atpg_runner_tab()
        self.create_result_analyzer_tab()
        self.create_batch_execution_tab()
    
    def create_atpg_runner_tab(self):
        """Create the ATPG Runner tab with all existing functionality"""
        
        # Create tab frame
        atpg_tab = tk.Frame(self.notebook)
        self.notebook.add(atpg_tab, text="ATPG Runner")
        
        # Frame for buttons
        button_frame = tk.Frame(atpg_tab)
        button_frame.pack(pady=15)
        
        # Browse button
        browse_btn = tk.Button(
            button_frame,
            text="Browse Files",
            command=self.browse_files,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="Clear Selection",
            command=self.clear_selection,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Run ATALANTA button
        run_btn = tk.Button(
            button_frame,
            text="Run ATALANTA",
            command=self.run_atalanta,
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        run_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop_execution,
            font=("Arial", 11),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Label for listbox
        list_label = tk.Label(
            atpg_tab,
            text="Selected Files:",
            font=("Arial", 11, "bold")
        )
        list_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Frame to hold listbox and scrollbar
        list_frame = tk.Frame(atpg_tab)
        list_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=5)
        
        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox to display selected file paths
        self.file_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED,
            bg="#f5f5f5",
            height=5
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # ATALANTA Options Section
        options_frame = tk.LabelFrame(
            atpg_tab,
            text="ATALANTA Options",
            font=("", 11, "bold"),
            padx=15,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=2
        )
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # First row: Random Patterns
        row1 = tk.Frame(options_frame)
        row1.pack(fill=tk.X, pady=5)
        
        self.random_check = tk.Checkbutton(
            row1,
            text="Enable Random Patterns (-r)",
            variable=self.enable_random_patterns,
            font=("Arial", 10),
            command=self._on_option_changed
        )
        self.random_check.pack(side=tk.LEFT)
        
        tk.Label(row1, text="Limit:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 5))
        self.random_entry = tk.Entry(
            row1,
            textvariable=self.random_pattern_limit,
            font=("Arial", 10),
            width=8,
            state=tk.DISABLED
        )
        self.random_entry.pack(side=tk.LEFT)
        
        # Second row: Compaction options
        row2 = tk.Frame(options_frame)
        row2.pack(fill=tk.X, pady=5)
        
        self.compaction_check = tk.Checkbutton(
            row2,
            text="Enable Compaction (-c)",
            variable=self.enable_compaction,
            font=("Arial", 10),
            command=self._on_compaction_option_changed
        )
        self.compaction_check.pack(side=tk.LEFT)
        
        self.no_compaction_check = tk.Checkbutton(
            row2,
            text="Disable Compaction (-N)",
            variable=self.disable_compaction,
            font=("Arial", 10),
            command=self._on_compaction_option_changed
        )
        self.no_compaction_check.pack(side=tk.LEFT, padx=(30, 0))
        
        # Third row: Backtracking limit
        row3 = tk.Frame(options_frame)
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(row3, text="Backtracking Limit (-B):", font=("Arial", 10)).pack(side=tk.LEFT)
        self.backtrack_entry = tk.Entry(
            row3,
            textvariable=self.backtrack_limit,
            font=("Arial", 10),
            width=8
        )
        self.backtrack_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(
            row3,
            text="(0 = unlimited)",
            font=("Arial", 9),
            fg="gray"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Separator
        separator = tk.Frame(atpg_tab, height=2, bg="gray")
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Output section label
        output_label = tk.Label(
            atpg_tab,
            text="ATALANTA Output:",
            font=("Arial", 11, "bold")
        )
        output_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        # Progress bar (initially hidden)
        self.progress_frame = tk.Frame(atpg_tab)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=300,
            maximum=100
        )
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Arial", 9, "bold"),
            fg="#2196F3",
            width=15
        )
        
        # Scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(
            atpg_tab,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            wrap=tk.WORD,
            height=15
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Status label at the bottom
        self.status_label = tk.Label(
            atpg_tab,
            text="No files selected",
            font=("Arial", 10),
            fg="gray",
            anchor="w"
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=10)
    
    def create_result_analyzer_tab(self):
        """Create the Result Analyzer tab with output parsing functionality"""
        
        # Create tab frame
        analyzer_tab = tk.Frame(self.notebook)
        self.notebook.add(analyzer_tab, text="Result Analyzer")
        
        # Title label
        title_label = tk.Label(
            analyzer_tab,
            text="ATALANTA Result Analyzer",
            font=("Arial", 14, "bold"),
            fg="#4CAF50",
            pady=10
        )
        title_label.pack()
        
        # Description label
        description = tk.Label(
            analyzer_tab,
            text="Load saved ATALANTA output files and view complete analysis results.",
            font=("Arial", 10),
            fg="gray"
        )
        description.pack(pady=(0, 10))
        
        # Dropdown frame for selecting recent logs
        dropdown_frame = tk.Frame(analyzer_tab)
        dropdown_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(
            dropdown_frame,
            text="Recent Logs:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_dropdown = ttk.Combobox(
            dropdown_frame,
            state="readonly",
            font=("Arial", 10),
            width=50
        )
        self.log_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.log_dropdown.bind("<<ComboboxSelected>>", self.on_log_selected)
        
        load_dropdown_btn = tk.Button(
            dropdown_frame,
            text="Load Selected",
            command=self.load_selected_log,
            font=("Arial", 9),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=3,
            cursor="hand2"
        )
        load_dropdown_btn.pack(side=tk.LEFT)
        
        # Refresh logs list
        self.refresh_log_list()
        
        # Button frame
        btn_frame = tk.Frame(analyzer_tab)
        btn_frame.pack(pady=10)
        
        # Generate Charts button
        self.chart_btn = tk.Button(
            btn_frame,
            text="Generate Charts",
            command=self.generate_charts,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.chart_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            btn_frame,
            text="Clear Results",
            command=self.clear_analyzer_results,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Selected file label
        file_label_frame = tk.Frame(analyzer_tab)
        file_label_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        tk.Label(
            file_label_frame,
            text="Selected File:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)
        
        self.analyzer_file_label = tk.Label(
            file_label_frame,
            text="No file loaded",
            font=("Arial", 10),
            fg="gray",
            anchor="w"
        )
        self.analyzer_file_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Results text area
        results_label = tk.Label(
            analyzer_tab,
            text="Extracted Metrics:",
            font=("Arial", 11, "bold")
        )
        results_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.results_text = scrolledtext.ScrolledText(
            analyzer_tab,
            font=("Courier", 11),
            bg="#f9f9f9",
            fg="#333333",
            wrap=tk.WORD,
            height=20,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def create_batch_execution_tab(self):
        """Create the Batch Execution & Reports tab"""
        
        # Create tab frame
        batch_tab = tk.Frame(self.notebook)
        self.notebook.add(batch_tab, text="Batch Execution & Reports")
        
        # Title label
        title_label = tk.Label(
            batch_tab,
            text="Batch ATPG Execution & Report Generation",
            font=("Arial", 14, "bold"),
            fg="#4CAF50",
            pady=10
        )
        title_label.pack()
        
        # Description
        description = tk.Label(
            batch_tab,
            text="Run ATALANTA on multiple circuits and automatically generate comparison reports.",
            font=("Arial", 10),
            fg="gray"
        )
        description.pack(pady=(0, 15))
        
        # File selection frame
        file_frame = tk.LabelFrame(
            batch_tab,
            text="Circuit Selection",
            font=("", 11, "bold"),
            padx=15,
            pady=10
        )
        file_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=False)
        
        # Button frame
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Select Circuits",
            command=self.batch_select_files,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Clear All",
            command=self.batch_clear_files,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Listbox for selected files
        tk.Label(
            file_frame,
            text="Selected Circuits:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        list_container = tk.Frame(file_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.batch_listbox = tk.Listbox(
            list_container,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            height=6,
            bg="#f5f5f5"
        )
        self.batch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_listbox.yview)
        
        # Execution controls
        control_frame = tk.LabelFrame(
            batch_tab,
            text="Batch Execution",
            font=("", 11, "bold"),
            padx=15,
            pady=10
        )
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Info label
        info_label = tk.Label(
            control_frame,
            text="Note: Will use the same ATALANTA options configured in ATPG Runner tab",
            font=("Arial", 9, "italic"),
            fg="#666666"
        )
        info_label.pack(pady=(0, 10))
        
        # Control buttons
        control_btn_frame = tk.Frame(control_frame)
        control_btn_frame.pack()
        
        self.batch_run_btn = tk.Button(
            control_btn_frame,
            text="Start Batch Execution",
            command=self.start_batch_execution,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=25,
            pady=8
        )
        self.batch_run_btn.pack(side=tk.LEFT, padx=5)
        
        self.batch_stop_btn = tk.Button(
            control_btn_frame,
            text="Stop Batch",
            command=self.stop_batch_execution,
            font=("Arial", 11),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.batch_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = tk.LabelFrame(
            batch_tab,
            text="Progress",
            font=("", 11, "bold"),
            padx=15,
            pady=10
        )
        progress_frame.pack(fill=tk.X, padx=20, pady=10, expand=False)
        
        # Status label
        self.batch_status_label = tk.Label(
            progress_frame,
            text="Ready to execute batch",
            font=("Arial", 10),
            fg="gray"
        )
        self.batch_status_label.pack(pady=5)
        
        # Progress bar
        self.batch_progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.batch_progress.pack(pady=5)
        
        # Current circuit label
        self.batch_current_label = tk.Label(
            progress_frame,
            text="",
            font=("Arial", 9),
            fg="#2196F3"
        )
        self.batch_current_label.pack(pady=5)
        
        # Output text area
        tk.Label(
            progress_frame,
            text="Execution Log:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.batch_output_text = scrolledtext.ScrolledText(
            progress_frame,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            wrap=tk.WORD,
            height=8
        )
        self.batch_output_text.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # Results Summary Section
        results_frame = tk.LabelFrame(
            batch_tab,
            text="Results Summary",
            font=("", 11, "bold"),
            padx=15,
            pady=10
        )
        results_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Statistics labels frame
        stats_frame = tk.Frame(results_frame, bg="#f0f0f0", relief=tk.RIDGE, borderwidth=2)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statistics title
        tk.Label(
            stats_frame,
            text="Overall Statistics",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        ).pack(pady=5)
        
        # Statistics display
        stats_display_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        stats_display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Three columns for statistics
        col1 = tk.Frame(stats_display_frame, bg="#f0f0f0")
        col1.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        col2 = tk.Frame(stats_display_frame, bg="#f0f0f0")
        col2.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        col3 = tk.Frame(stats_display_frame, bg="#f0f0f0")
        col3.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Average Coverage
        tk.Label(
            col1,
            text="Avg Coverage:",
            font=("Arial", 9, "bold"),
            bg="#f0f0f0"
        ).pack()
        self.avg_coverage_label = tk.Label(
            col1,
            text="-",
            font=("Arial", 12, "bold"),
            fg="#4CAF50",
            bg="#f0f0f0"
        )
        self.avg_coverage_label.pack()
        
        # Average CPU Time
        tk.Label(
            col2,
            text="Avg CPU Time:",
            font=("Arial", 9, "bold"),
            bg="#f0f0f0"
        ).pack()
        self.avg_time_label = tk.Label(
            col2,
            text="-",
            font=("Arial", 12, "bold"),
            fg="#2196F3",
            bg="#f0f0f0"
        )
        self.avg_time_label.pack()
        
        # Average Pattern Reduction
        tk.Label(
            col3,
            text="Avg Pattern Reduction:",
            font=("Arial", 9, "bold"),
            bg="#f0f0f0"
        ).pack()
        self.avg_reduction_label = tk.Label(
            col3,
            text="-",
            font=("Arial", 12, "bold"),
            fg="#FF9800",
            bg="#f0f0f0"
        )
        self.avg_reduction_label.pack(pady=(0, 5))
        
        # Results table
        tk.Label(
            results_frame,
            text="Circuit Results Table:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Create Treeview with scrollbars
        table_container = tk.Frame(results_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = tk.Scrollbar(table_container, orient="vertical")
        hsb = tk.Scrollbar(table_container, orient="horizontal")
        
        # Treeview
        self.results_tree = ttk.Treeview(
            table_container,
            columns=('Coverage', 'Patterns_After', 'CPU_Time', 'Gates', 'Total_Faults'),
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=8
        )
        
        vsb.config(command=self.results_tree.yview)
        hsb.config(command=self.results_tree.xview)
        
        # Configure columns
        self.results_tree.heading('#0', text='Circuit Name')
        self.results_tree.heading('Coverage', text='Coverage (%)')
        self.results_tree.heading('Patterns_After', text='Patterns')
        self.results_tree.heading('CPU_Time', text='CPU Time (s)')
        self.results_tree.heading('Gates', text='Gates')
        self.results_tree.heading('Total_Faults', text='Total Faults')
        
        self.results_tree.column('#0', width=200, minwidth=150)
        self.results_tree.column('Coverage', width=100, anchor='center')
        self.results_tree.column('Patterns_After', width=80, anchor='center')
        self.results_tree.column('CPU_Time', width=100, anchor='center')
        self.results_tree.column('Gates', width=80, anchor='center')
        self.results_tree.column('Total_Faults', width=100, anchor='center')
        
        # Pack elements
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _on_option_changed(self):
        """Handle random pattern checkbox state change"""
        if self.enable_random_patterns.get():
            self.random_entry.config(state=tk.NORMAL)
        else:
            self.random_entry.config(state=tk.DISABLED)
    
    def _on_compaction_option_changed(self):
        """Ensure -c and -N are mutually exclusive"""
        if self.enable_compaction.get() and self.disable_compaction.get():
            # If both are checked, uncheck the other one
            caller = self.root.focus_get()
            if caller == self.compaction_check:
                self.disable_compaction.set(False)
            else:
                self.enable_compaction.set(False)
    
    def _validate_options(self):
        """Validate ATALANTA options before execution"""
        # Validate random pattern limit
        if self.enable_random_patterns.get():
            try:
                limit = int(self.random_pattern_limit.get())
                if limit < 1:
                    messagebox.showerror("Invalid Input", "Random pattern limit must be >= 1")
                    return False
            except ValueError:
                messagebox.showerror("Invalid Input", "Random pattern limit must be a valid integer")
                return False
        
        # Validate backtracking limit
        try:
            backtrack = int(self.backtrack_limit.get())
            if backtrack < 0:
                messagebox.showerror("Invalid Input", "Backtracking limit must be >= 0")
                return False
        except ValueError:
            messagebox.showerror("Invalid Input", "Backtracking limit must be a valid integer")
            return False
        
        return True
    
    def _build_atalanta_command(self, circuit_file):
        """Build ATALANTA command dynamically based on user options"""
        cmd = [self.atalanta_path]
        
        # Add random patterns option
        if self.enable_random_patterns.get():
            cmd.extend(["-r", self.random_pattern_limit.get()])
        
        # Add compaction option (mutually exclusive with -N)
        if self.enable_compaction.get():
            cmd.append("-c")
        elif self.disable_compaction.get():
            cmd.append("-N")
        
        # Add backtracking limit
        backtrack = int(self.backtrack_limit.get())
        if backtrack > 0:  # Only add if not unlimited (0)
            cmd.extend(["-B", str(backtrack)])
        
        # Add circuit file
        cmd.append(circuit_file)
        
        return cmd
    
    def _get_options_metadata(self):
        """Get current ATALANTA options as metadata string"""
        options = []
        
        if self.enable_random_patterns.get():
            options.append(f"-r {self.random_pattern_limit.get()}")
        
        if self.enable_compaction.get():
            options.append("-c")
        elif self.disable_compaction.get():
            options.append("-N")
        
        backtrack = int(self.backtrack_limit.get())
        if backtrack > 0:
            options.append(f"-B {backtrack}")
        elif backtrack == 0:
            options.append("-B 0 (unlimited)")
        
        return " ".join(options) if options else "Default options"
    
    def browse_files(self):
        """Open file dialog to select multiple .bench files"""
        
        # Open file dialog - allows multiple file selection
        files = filedialog.askopenfilenames(
            title="Select Benchmark Circuit Files",
            initialdir=self.circuits_dir,
            filetypes=[("Benchmark files", "*.bench"), ("All files", "*.*")]
        )
        
        # Add selected files to the list (avoid duplicates)
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, file)
        
        # Update status
        self.update_status()
    
    def clear_selection(self):
        """Clear all selected files"""
        
        if not self.selected_files:
            return
        
        # Ask for confirmation
        if messagebox.askyesno("Clear Selection", "Remove all selected files?"):
            self.selected_files.clear()
            self.file_listbox.delete(0, tk.END)
            self.update_status()
    
    def update_status(self):
        """Update the status label with file count"""
        
        count = len(self.selected_files)
        if count == 0:
            self.status_label.config(text="No files selected", fg="gray")
        elif count == 1:
            self.status_label.config(text="1 file selected", fg="green")
        else:
            self.status_label.config(text=f"{count} files selected", fg="green")
    
    def run_atalanta(self):
        """Run ATALANTA on the selected file"""
        
        # Check if already running
        if self.is_running:
            messagebox.showwarning("Warning", "ATALANTA is already running!\nPlease wait for it to complete.")
            return
        
        # Check if any files are selected
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected!\nPlease select a .bench file first.")
            return
        
        # Get the selected file from the listbox
        selected_indices = self.file_listbox.curselection()
        
        if selected_indices:
            # Use the file selected in the listbox (highlighted)
            selected_index = selected_indices[0]
            circuit_file = self.selected_files[selected_index]
        else:
            # If no file is highlighted, show error message
            messagebox.showerror("Error", "Please click on a file in the list to select which one to run!")
            return
        
        # Clear previous output
        filename = os.path.basename(circuit_file)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Running ATALANTA on: {filename}\n")
        self.output_text.insert(tk.END, "=" * 70 + "\n\n")
        
        # Show progress bar
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.progress_label.pack(side=tk.LEFT)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0% completed")
        
        # Reset progress tracking
        self.current_patterns = 0
        self.total_patterns = 0
        
        # Start timer
        self.start_time = time.time()
        
        # Update status
        self.status_label.config(text=f"Running ATALANTA on {filename}...", fg="orange")
        
        # Set running flag
        self.is_running = True
        
        # Enable stop button
        self.stop_btn.config(state=tk.NORMAL)
        
        # Run in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self._execute_atalanta, args=(circuit_file,))
        thread.daemon = True
        thread.start()
    
    def _execute_atalanta(self, circuit_file):
        """Execute ATALANTA command and capture output"""
        
        output_buffer = []
        
        try:
            # Build the command dynamically based on user options
            cmd = self._build_atalanta_command(circuit_file)
            
            # Log the command for traceability
            cmd_str = " ".join(cmd)
            log_header = f"{'='*70}\n"
            log_header += f"ATALANTA Command: {cmd_str}\n"
            log_header += f"Options: {self._get_options_metadata()}\n"
            log_header += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            log_header += f"{'='*70}\n\n"
            output_buffer.append(log_header)
            
            # Display command in output
            self.root.after(0, self._display_command, log_header)
            
            # Run the command and capture output line by line
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Parse output to track progress
            for line in self.process.stdout:
                output_buffer.append(line)
                
                # Look for total faults to estimate progress
                if "total faults" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i > 0 and "fault" in parts[i-1].lower():
                            self.total_patterns = int(part)
                            break
                
                # Count test patterns generated (look for pattern indicators)
                if "test" in line.lower() and ("pattern" in line.lower() or "vector" in line.lower()):
                    self.current_patterns += 1
                    
                # Update progress every 10 lines
                if len(output_buffer) % 10 == 0:
                    self._update_progress()
            
            # Wait for process to complete
            self.process.wait()
            
            # Check if process was terminated by user
            if self.process.returncode == -15 or self.process.returncode == -9:
                # Process was killed, don't display output
                return
            
            # Set to 100% when done
            self.root.after(0, self._set_progress, 100)
            
            # Display all output at once
            full_output = ''.join(output_buffer)
            self.root.after(0, self._display_output, full_output, self.process.returncode)
            
            # Save output to file if successful
            if self.process.returncode == 0:
                self.root.after(0, self._save_output, circuit_file, full_output)
                
        except FileNotFoundError:
            error_msg = f"Error: ATALANTA executable not found at:\n{self.atalanta_path}\n"
            self.root.after(0, self._display_output, error_msg, -1)
        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            self.root.after(0, self._display_output, error_msg, -1)
        finally:
            # Always reset running state and hide progress bar
            self.root.after(0, self._cleanup_execution)
    
    def _display_command(self, command_str):
        """Display the ATALANTA command being executed"""
        self.output_text.insert(tk.END, command_str)
        self.output_text.see(tk.END)
    
    def _display_output(self, output, return_code):
        """Display output and show completion status"""
        # Insert the output
        self.output_text.insert(tk.END, output)
        
        # Add completion message
        self.output_text.insert(tk.END, f"\n{'='*70}\n")
        if return_code == 0:
            self.output_text.insert(tk.END, "✓ ATALANTA completed successfully!\n")
            self.status_label.config(text="ATALANTA execution completed", fg="green")
        else:
            self.output_text.insert(tk.END, f"✗ ATALANTA failed with code {return_code}\n")
            self.status_label.config(text="ATALANTA execution failed", fg="red")
        
        # Auto-scroll to bottom
        self.output_text.see(tk.END)
    
    def _update_progress(self):
        """Update progress bar based on estimated completion"""
        if not self.is_running:
            return
        
        # Estimate progress based on patterns or elapsed time
        if self.total_patterns > 0 and self.current_patterns > 0:
            # Progress based on patterns (cap at 98% to let completion set 100%)
            progress = min(98, int((self.current_patterns / self.total_patterns) * 100))
        else:
            # Time-based estimation (assume ~30 seconds average, cap at 98%)
            elapsed = time.time() - self.start_time if self.start_time else 0
            progress = min(98, int((elapsed / 30.0) * 100))
        
        self._set_progress(progress)
    
    def _set_progress(self, value):
        """Set progress bar value and label"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"{value}% completed")
    
    def stop_execution(self):
        """Stop the running ATALANTA process"""
        if not self.is_running or self.process is None:
            return
        
        # Confirm stop
        if messagebox.askyesno("Stop Execution", "Are you sure you want to stop ATALANTA execution?"):
            try:
                # Terminate the process
                self.process.terminate()
                # Wait briefly, then kill if still running
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                
                # Clear output and update UI
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "✗ Execution stopped by user\n")
                self.status_label.config(text="Execution stopped", fg="red")
                
                # Cleanup
                self._cleanup_execution()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop process: {str(e)}")
    
    def _cleanup_execution(self):
        """Clean up after execution completes"""
        # Calculate total time
        if self.start_time:
            total_time = time.time() - self.start_time
            # Keep the "Completed in X.Xs" message visible
            final_msg = f"100% - {total_time:.1f}s"
            self.progress_label.config(text=final_msg)
        
        # Reset running flag BEFORE hiding progress bar
        self.is_running = False
        
        # Disable stop button
        self.stop_btn.config(state=tk.DISABLED)
        
        # Clear process reference
        self.process = None
        
        # Reset progress tracking
        self.current_patterns = 0
        self.total_patterns = 0
        self.start_time = None
        
        # Hide progress bar after delay
        self.root.after(2000, self._hide_progress)
    
    def _hide_progress(self):
        """Hide the progress bar and label"""
        self.progress_bar['value'] = 0
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
    
    def _save_output(self, circuit_file, output):
        """Save ATALANTA output to a file with metadata"""
        try:
            # Generate filename with timestamp
            circuit_name = os.path.splitext(os.path.basename(circuit_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{circuit_name}_{timestamp}.log"
            output_path = os.path.join(self.outputs_dir, output_filename)
            
            # Prepare metadata header
            metadata = f"{'='*70}\n"
            metadata += f"ATALANTA RUN METADATA\n"
            metadata += f"{'='*70}\n"
            metadata += f"Circuit: {circuit_name}\n"
            metadata += f"Timestamp: {timestamp}\n"
            metadata += f"Options: {self._get_options_metadata()}\n"
            metadata += f"{'='*70}\n\n"
            
            # Save metadata and output to file
            with open(output_path, 'w') as f:
                f.write(metadata)
                f.write(output)
            
            # Track the last output file
            self.last_output_file = output_path
            
            # Update status briefly
            self.status_label.config(text=f"Output saved: {output_filename}", fg="blue")
            
            # Refresh log list in Result Analyzer
            self.refresh_log_list()
            
            # Auto-switch to Result Analyzer tab and load the file
            self.root.after(2500, lambda: self.auto_load_latest_result(output_path))
            
        except Exception as e:
            print(f"Warning: Failed to save output: {str(e)}")
    
    def auto_load_latest_result(self, file_path):
        """Automatically switch to Result Analyzer tab and load the latest result"""
        try:
            # Switch to Result Analyzer tab (tab index 1)
            self.notebook.select(1)
            
            # Load the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update file label
            self.analyzer_file_label.config(text=file_path, fg="green")
            
            # Parse and display
            metrics = self.parse_atalanta_output(content, file_path)
            self.current_metrics = metrics
            self.display_full_summary(content, metrics)
            
            # Select in dropdown
            filename = os.path.basename(file_path)
            if filename in self.log_dropdown['values']:
                self.log_dropdown.set(filename)
                
        except Exception as e:
            print(f"Warning: Failed to auto-load result: {str(e)}")
    
    def refresh_log_list(self):
        """Refresh the dropdown list with available log files"""
        try:
            if os.path.exists(self.outputs_dir):
                log_files = [f for f in os.listdir(self.outputs_dir) if f.endswith('.log')]
                # Sort by modification time, newest first
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.outputs_dir, x)), reverse=True)
                self.log_dropdown['values'] = log_files
                if log_files:
                    self.log_dropdown.set(log_files[0])
        except Exception as e:
            print(f"Warning: Failed to refresh log list: {str(e)}")
    
    def on_log_selected(self, event):
        """Handle log selection from dropdown"""
        pass  # Selection handled by Load Selected button
    
    def load_selected_log(self):
        """Load the log file selected in the dropdown"""
        selected = self.log_dropdown.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a log file from the dropdown.")
            return
        
        file_path = os.path.join(self.outputs_dir, selected)
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"Log file not found: {selected}")
            return
        
        try:
            # Update file label
            self.analyzer_file_label.config(text=file_path, fg="green")
            
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the content
            metrics = self.parse_atalanta_output(content, file_path)
            
            # Store metrics for chart generation
            self.current_metrics = metrics
            
            # Display the full summary
            self.display_full_summary(content, metrics)
            
        except Exception as e:
            self.analyzer_file_label.config(text="Error loading file", fg="red")
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def load_atalanta_output(self):
        """Load and parse ATALANTA output file"""
        
        # Open file dialog to select output file - browse outputs directory by default
        file_path = filedialog.askopenfilename(
            title="Select ATALANTA Output File",
            initialdir=self.outputs_dir,
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Update file label
            self.analyzer_file_label.config(text=file_path, fg="green")
            
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the content
            metrics = self.parse_atalanta_output(content, file_path)
            
            # Store metrics for chart generation
            self.current_metrics = metrics
            
            # Display the full summary
            self.display_full_summary(content, metrics)
            
            # Refresh dropdown and select this file
            self.refresh_log_list()
            filename = os.path.basename(file_path)
            if filename in self.log_dropdown['values']:
                self.log_dropdown.set(filename)
            
        except Exception as e:
            self.analyzer_file_label.config(text="Error loading file", fg="red")
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def parse_atalanta_output(self, content, file_path):
        """Parse ATALANTA output to extract comprehensive metrics for charting"""
        
        metrics = {
            # Basic metrics
            'circuit_name': 'Not Found',
            'total_faults': 'Not Found',
            'detected_faults': 'Not Found',
            'fault_coverage': 'Not Found',
            'test_patterns': 'Not Found',
            'cpu_time': 'Not Found',
            
            # Extended metrics for enhanced charting
            'redundant_faults': 'Not Found',
            'aborted_faults': 'Not Found',
            'patterns_before_compaction': 'Not Found',
            'patterns_after_compaction': 'Not Found',
            
            # Time breakdown
            'init_time': 'Not Found',
            'fault_sim_time': 'Not Found',
            'fan_time': 'Not Found',
            'total_time': 'Not Found',
            
            # Circuit complexity
            'num_inputs': 'Not Found',
            'num_outputs': 'Not Found',
            'num_gates': 'Not Found',
            'circuit_level': 'Not Found',
            
            # Run metadata
            'options_used': 'Not Found',
            'timestamp': 'Not Found'
        }
        
        # Extract metadata from file header
        metadata_match = re.search(r'Options:\s*([^\n]+)', content)
        if metadata_match:
            metrics['options_used'] = metadata_match.group(1).strip()
        
        timestamp_match = re.search(r'Timestamp:\s*([^\n]+)', content)
        if timestamp_match:
            metrics['timestamp'] = timestamp_match.group(1).strip()
        
        # Extract circuit name from file path
        filename = os.path.basename(file_path)
        circuit_match = re.match(r'([^._]+)', filename)
        if circuit_match:
            metrics['circuit_name'] = circuit_match.group(1)
        
        # Also try to find circuit name in content
        match = re.search(r'Name of the circuit\s*:\s*([^\s\n]+)', content, re.IGNORECASE)
        if match:
            circuit_name = match.group(1)
            if circuit_name.endswith('.bench'):
                circuit_name = circuit_name[:-6]
            metrics['circuit_name'] = circuit_name
        
        # Extract total faults (collapsed faults)
        match = re.search(r'Number of collapsed faults\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['total_faults'] = match.group(1)
        
        # Extract redundant faults
        match = re.search(r'Number of identified redundant faults\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['redundant_faults'] = match.group(1)
        
        # Extract aborted faults
        match = re.search(r'Number of aborted faults\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['aborted_faults'] = match.group(1)
        
        # Extract fault coverage percentage
        match = re.search(r'Fault coverage\s*:\s*([\d.]+)\s*%', content, re.IGNORECASE)
        if match:
            coverage_val = float(match.group(1))
            metrics['fault_coverage'] = f"{coverage_val} %"
            
            # Calculate detected faults if we have total faults
            if metrics['total_faults'] != 'Not Found':
                try:
                    total = int(metrics['total_faults'])
                    detected = int((coverage_val / 100.0) * total)
                    metrics['detected_faults'] = str(detected)
                except:
                    pass
        
        # Extract test patterns before compaction
        match = re.search(r'Number of test patterns before compaction\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['patterns_before_compaction'] = match.group(1)
        
        # Extract test patterns after compaction
        match = re.search(r'Number of test patterns after compaction\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['test_patterns'] = match.group(1)
            metrics['patterns_after_compaction'] = match.group(1)
        
        # Extract CPU time breakdown
        # Initialization time
        match = re.search(r'Initialization\s*:\s*([\d.]+)\s*Secs', content, re.IGNORECASE)
        if match:
            metrics['init_time'] = match.group(1)
        
        # Fault simulation time
        match = re.search(r'Fault simulation\s*:\s*([\d.]+)\s*Secs', content, re.IGNORECASE)
        if match:
            metrics['fault_sim_time'] = match.group(1)
        
        # FAN time
        match = re.search(r'FAN\s*:\s*([\d.]+)\s*Secs', content, re.IGNORECASE)
        if match:
            metrics['fan_time'] = match.group(1)
        
        # Total CPU time
        match = re.search(r'Total\s*:\s*([\d.]+)\s*Secs', content, re.IGNORECASE)
        if match:
            metrics['cpu_time'] = f"{match.group(1)} sec"
            metrics['total_time'] = match.group(1)
        
        # Extract circuit complexity metrics
        # Number of primary inputs
        match = re.search(r'Number of primary inputs\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['num_inputs'] = match.group(1)
        
        # Number of primary outputs
        match = re.search(r'Number of primary outputs\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['num_outputs'] = match.group(1)
        
        # Number of gates
        match = re.search(r'Number of gates\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['num_gates'] = match.group(1)
        
        # Circuit level
        match = re.search(r'Level of the circuit\s*:\s*(\d+)', content, re.IGNORECASE)
        if match:
            metrics['circuit_level'] = match.group(1)
        
        return metrics
    
    def display_full_summary(self, content, metrics):
        """Display complete ATALANTA summary from the output"""
        
        # Enable editing temporarily
        self.results_text.config(state=tk.NORMAL)
        
        # Clear previous content
        self.results_text.delete(1.0, tk.END)
        
        # Display run metadata header if available
        if metrics.get('options_used') != 'Not Found':
            metadata_header = f"{'='*70}\n"
            metadata_header += f"RUN CONFIGURATION\n"
            metadata_header += f"{'='*70}\n"
            metadata_header += f"Circuit: {metrics.get('circuit_name', 'Unknown')}\n"
            if metrics.get('timestamp') != 'Not Found':
                metadata_header += f"Timestamp: {metrics.get('timestamp')}\n"
            metadata_header += f"ATALANTA Options: {metrics.get('options_used')}\n"
            metadata_header += f"{'='*70}\n\n"
            self.results_text.insert(tk.END, metadata_header)
        
        # Extract the summary section from ATALANTA output
        # Look for the summary header and capture everything until the end
        summary_match = re.search(
            r'(\*\*\*\*\*\*\s+SUMMARY OF TEST PATTERN GENERATION RESULTS\s+\*\*\*\*\*\*.*?)(?=\n\n\n|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if summary_match:
            # Display the complete summary
            summary_text = summary_match.group(1).strip()
            self.results_text.insert(tk.END, summary_text)
        else:
            # Try alternative pattern - look for numbered sections
            summary_start = content.find('SUMMARY OF TEST PATTERN GENERATION RESULTS')
            if summary_start != -1:
                # Find the end - usually at end of file or before next major section
                summary_section = content[summary_start:]
                # Take everything or stop at multiple newlines
                summary_lines = summary_section.split('\n')
                
                # Find where meaningful content ends (multiple blank lines)
                end_idx = len(summary_lines)
                blank_count = 0
                for i, line in enumerate(summary_lines):
                    if not line.strip():
                        blank_count += 1
                        if blank_count >= 3:
                            end_idx = i
                            break
                    else:
                        blank_count = 0
                
                summary_text = '\n'.join(summary_lines[:end_idx])
                self.results_text.insert(tk.END, summary_text)
            else:
                # Final fallback to simple metrics
                output = [
                    "******   SUMMARY OF TEST PATTERN GENERATION RESULTS   ******",
                    "",
                    "--------------------------------",
                    f"Circuit Name      : {metrics['circuit_name']}",
                    f"Total Faults      : {metrics['total_faults']}",
                    f"Detected Faults   : {metrics['detected_faults']}",
                    f"Fault Coverage    : {metrics['fault_coverage']}",
                    f"Test Patterns     : {metrics['test_patterns']}",
                    f"CPU Time          : {metrics['cpu_time']}",
                    "--------------------------------"
                ]
                self.results_text.insert(tk.END, "\n".join(output))
        
        # Disable editing
        self.results_text.config(state=tk.DISABLED)
    
    def display_metrics(self, metrics):
        """Display extracted metrics in the results text area"""
        
        # Enable editing temporarily
        self.results_text.config(state=tk.NORMAL)
        
        # Clear previous content
        self.results_text.delete(1.0, tk.END)
        
        # Format and display results with exact specification
        output = [
            "--------------------------------",
            f"Circuit Name      : {metrics['circuit_name']}",
            f"Total Faults      : {metrics['total_faults']}",
            f"Detected Faults   : {metrics['detected_faults']}",
            f"Fault Coverage    : {metrics['fault_coverage']}",
            f"Test Patterns     : {metrics['test_patterns']}",
            f"CPU Time          : {metrics['cpu_time']}",
            "--------------------------------"
        ]
        
        self.results_text.insert(tk.END, "\n".join(output))
        
        # Disable editing
        self.results_text.config(state=tk.DISABLED)
    
    def clear_analyzer_results(self):
        """Clear the results text area and reset file label"""
        
        # Reset file label
        self.analyzer_file_label.config(text="No file loaded", fg="gray")
        
        # Clear stored metrics
        self.current_metrics = None
        
        # Clear results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def generate_charts(self):
        """Generate comprehensive professional charts for ATALANTA results analysis"""
        
        # Validate that data is loaded
        if self.current_metrics is None:
            messagebox.showwarning(
                "No Data", 
                "Load ATALANTA result first.\n\nPlease select a log file from the dropdown and click 'Load Selected'."
            )
            return
        
        metrics = self.current_metrics
        circuit_name = metrics.get('circuit_name', 'Unknown Circuit')
        
        # Validate we have sufficient data
        if circuit_name == 'Not Found':
            messagebox.showerror("Invalid Data", "Unable to parse circuit data. Please ensure you've loaded a valid ATALANTA output file.")
            return
        
        try:
            # Create figure with 2x3 grid for 5 charts
            fig = plt.figure(figsize=(16, 10))
            fig.suptitle(f'ATALANTA ATPG Analysis Report - {circuit_name}', 
                        fontsize=16, fontweight='bold', y=0.995)
            
            # Define professional color scheme
            colors = {
                'detected': '#4CAF50',      # Green
                'redundant': '#FF9800',     # Orange
                'aborted': '#F44336',       # Red
                'before': '#2196F3',        # Blue
                'after': '#4CAF50',         # Green
                'init': '#9C27B0',          # Purple
                'fault_sim': '#2196F3',     # Blue
                'fan': '#FF9800',           # Orange
                'complexity': '#607D8B'     # Blue Grey
            }
            
            chart_count = 0
            
            # Chart 1: Fault Distribution
            if (metrics['total_faults'] != 'Not Found' and 
                metrics['redundant_faults'] != 'Not Found' and 
                metrics['aborted_faults'] != 'Not Found'):
                
                ax1 = plt.subplot(2, 3, 1)
                chart_count += 1
                
                total_faults = int(metrics['total_faults'])
                redundant = int(metrics['redundant_faults'])
                aborted = int(metrics['aborted_faults'])
                detected = int(metrics['detected_faults']) if metrics['detected_faults'] != 'Not Found' else 0
                
                categories = ['Detected', 'Redundant', 'Aborted']
                values = [detected, redundant, aborted]
                bar_colors = [colors['detected'], colors['redundant'], colors['aborted']]
                
                bars = ax1.bar(categories, values, color=bar_colors, edgecolor='black', linewidth=1.2)
                ax1.set_ylabel('Number of Faults', fontsize=10, fontweight='bold')
                ax1.set_title('1. Fault Distribution', fontsize=11, fontweight='bold', pad=10)
                ax1.grid(axis='y', alpha=0.3, linestyle='--')
                
                # Add value labels on bars
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{val}',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                # Add total faults annotation
                ax1.text(0.5, 0.98, f'Total Collapsed Faults: {total_faults}',
                        transform=ax1.transAxes, ha='center', va='top',
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Chart 2: Test Pattern Reduction (Before vs After Compaction)
            if (metrics['patterns_before_compaction'] != 'Not Found' and 
                metrics['patterns_after_compaction'] != 'Not Found'):
                
                ax2 = plt.subplot(2, 3, 2)
                chart_count += 1
                
                before = int(metrics['patterns_before_compaction'])
                after = int(metrics['patterns_after_compaction'])
                reduction = before - after
                reduction_pct = (reduction / before * 100) if before > 0 else 0
                
                categories = ['Before\nCompaction', 'After\nCompaction']
                values = [before, after]
                bar_colors = [colors['before'], colors['after']]
                
                bars = ax2.bar(categories, values, color=bar_colors, edgecolor='black', linewidth=1.2)
                ax2.set_ylabel('Number of Patterns', fontsize=10, fontweight='bold')
                ax2.set_title('2. Test Pattern Reduction', fontsize=11, fontweight='bold', pad=10)
                ax2.grid(axis='y', alpha=0.3, linestyle='--')
                
                # Add value labels
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{val}',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                # Add reduction annotation
                ax2.text(0.5, 0.98, f'Reduction: {reduction} patterns ({reduction_pct:.1f}%)',
                        transform=ax2.transAxes, ha='center', va='top',
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
            
            # Chart 3: Fault Coverage Gauge
            if metrics['fault_coverage'] != 'Not Found':
                ax3 = plt.subplot(2, 3, 3)
                chart_count += 1
                
                coverage = float(metrics['fault_coverage'].replace('%', '').strip())
                
                # Create horizontal bar gauge
                ax3.barh(['Coverage'], [coverage], color=colors['detected'], 
                        edgecolor='black', linewidth=1.2, height=0.5)
                ax3.barh(['Coverage'], [100-coverage], left=[coverage], 
                        color='#E0E0E0', edgecolor='black', linewidth=1.2, height=0.5)
                
                ax3.set_xlim(0, 100)
                ax3.set_xlabel('Percentage (%)', fontsize=10, fontweight='bold')
                ax3.set_title('3. Fault Coverage Quality', fontsize=11, fontweight='bold', pad=10)
                ax3.grid(axis='x', alpha=0.3, linestyle='--')
                
                # Add percentage label
                ax3.text(coverage/2, 0, f'{coverage:.2f}%',
                        ha='center', va='center', fontsize=12, fontweight='bold', color='white')
                
                # Add quality indicator
                if coverage >= 95:
                    quality = 'Excellent'
                    quality_color = 'darkgreen'
                elif coverage >= 90:
                    quality = 'Good'
                    quality_color = 'green'
                elif coverage >= 85:
                    quality = 'Fair'
                    quality_color = 'orange'
                else:
                    quality = 'Poor'
                    quality_color = 'red'
                
                ax3.text(0.5, 0.02, f'Quality: {quality}',
                        transform=ax3.transAxes, ha='center', va='bottom',
                        fontsize=9, fontweight='bold', color=quality_color,
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Chart 4: Time Breakdown (Execution Time Analysis)
            if (metrics['init_time'] != 'Not Found' and 
                metrics['fault_sim_time'] != 'Not Found' and 
                metrics['fan_time'] != 'Not Found'):
                
                ax4 = plt.subplot(2, 3, 4)
                chart_count += 1
                
                init_time = float(metrics['init_time'])
                fault_sim_time = float(metrics['fault_sim_time'])
                fan_time = float(metrics['fan_time'])
                
                # Create stacked bar chart
                categories = ['Execution\nTime']
                
                bars1 = ax4.bar(categories, [init_time], label='Initialization', 
                              color=colors['init'], edgecolor='black', linewidth=1.2)
                bars2 = ax4.bar(categories, [fault_sim_time], bottom=[init_time], 
                              label='Fault Simulation', color=colors['fault_sim'], 
                              edgecolor='black', linewidth=1.2)
                bars3 = ax4.bar(categories, [fan_time], 
                              bottom=[init_time + fault_sim_time], label='FAN',
                              color=colors['fan'], edgecolor='black', linewidth=1.2)
                
                ax4.set_ylabel('Time (seconds)', fontsize=10, fontweight='bold')
                ax4.set_title('4. CPU Time Breakdown', fontsize=11, fontweight='bold', pad=10)
                ax4.legend(loc='upper right', fontsize=8)
                ax4.grid(axis='y', alpha=0.3, linestyle='--')
                
                # Add time labels on segments
                total = init_time + fault_sim_time + fan_time
                if init_time > 0.01:
                    ax4.text(0, init_time/2, f'{init_time:.3f}s',
                            ha='center', va='center', fontsize=8, fontweight='bold')
                if fault_sim_time > 0.01:
                    ax4.text(0, init_time + fault_sim_time/2, f'{fault_sim_time:.3f}s',
                            ha='center', va='center', fontsize=8, fontweight='bold')
                if fan_time > 0.01:
                    ax4.text(0, init_time + fault_sim_time + fan_time/2, f'{fan_time:.3f}s',
                            ha='center', va='center', fontsize=8, fontweight='bold')
                
                # Add total time
                ax4.text(0.5, 0.98, f'Total: {total:.3f} seconds',
                        transform=ax4.transAxes, ha='center', va='top',
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
            
            # Chart 5: Circuit Complexity Overview
            if (metrics['num_inputs'] != 'Not Found' and 
                metrics['num_outputs'] != 'Not Found' and 
                metrics['num_gates'] != 'Not Found' and
                metrics['circuit_level'] != 'Not Found'):
                
                ax5 = plt.subplot(2, 3, 5)
                chart_count += 1
                
                num_inputs = int(metrics['num_inputs'])
                num_outputs = int(metrics['num_outputs'])
                num_gates = int(metrics['num_gates'])
                circuit_level = int(metrics['circuit_level'])
                
                categories = ['Inputs', 'Outputs', 'Gates', 'Levels']
                values = [num_inputs, num_outputs, num_gates, circuit_level]
                
                bars = ax5.bar(categories, values, color=colors['complexity'], 
                             edgecolor='black', linewidth=1.2)
                ax5.set_ylabel('Count', fontsize=10, fontweight='bold')
                ax5.set_title('5. Circuit Complexity', fontsize=11, fontweight='bold', pad=10)
                ax5.grid(axis='y', alpha=0.3, linestyle='--')
                
                # Add value labels
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax5.text(bar.get_x() + bar.get_width()/2., height,
                            f'{val}',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # Chart 6: Summary Box (if we have space)
            ax6 = plt.subplot(2, 3, 6)
            ax6.axis('off')
            
            # Create summary text with options
            summary_lines = [
                f"Circuit: {circuit_name}",
                ""
            ]
            
            # Add options if available
            if metrics.get('options_used') != 'Not Found':
                summary_lines.append(f"Options: {metrics.get('options_used')}")
                summary_lines.append("")
            
            summary_lines.extend([
                "Key Metrics:",
                f"• Coverage: {metrics.get('fault_coverage', 'N/A')}",
                f"• Test Patterns: {metrics.get('test_patterns', 'N/A')}",
                f"• CPU Time: {metrics.get('cpu_time', 'N/A')}",
                "",
                "Fault Classification:",
                f"• Total: {metrics.get('total_faults', 'N/A')}",
                f"• Detected: {metrics.get('detected_faults', 'N/A')}",
                f"• Redundant: {metrics.get('redundant_faults', 'N/A')}",
                f"• Aborted: {metrics.get('aborted_faults', 'N/A')}"
            ])
            
            summary_text = "\n".join(summary_lines)
            ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
                    fontsize=9, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
            ax6.set_title('Summary', fontsize=11, fontweight='bold', pad=10)
            
            # Check if we generated any charts
            if chart_count == 0:
                messagebox.showwarning(
                    "Insufficient Data",
                    "The loaded log file does not contain enough data to generate charts.\n"
                    "Please ensure the ATALANTA output is complete."
                )
                plt.close(fig)
                return
            
            # Adjust layout and display
            plt.tight_layout(rect=[0, 0, 1, 0.99])
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Failed to generate charts:\n\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    # ========================================
    # BATCH EXECUTION METHODS
    # ========================================
    
    def batch_select_files(self):
        """Select multiple .bench files for batch execution"""
        files = filedialog.askopenfilenames(
            title="Select Benchmark Circuit Files",
            initialdir=self.circuits_dir,
            filetypes=[("Bench Files", "*.bench"), ("All Files", "*.*")]
        )
        
        if files:
            self.batch_files = list(files)
            self.batch_listbox.delete(0, tk.END)
            for file in self.batch_files:
                filename = os.path.basename(file)
                self.batch_listbox.insert(tk.END, filename)
            
            self.batch_status_label.config(
                text=f"{len(self.batch_files)} circuit(s) selected",
                fg="blue"
            )
    
    def batch_clear_files(self):
        """Clear batch file selection"""
        self.batch_files = []
        self.batch_listbox.delete(0, tk.END)
        self.batch_status_label.config(text="Ready to execute batch", fg="gray")
    
    def start_batch_execution(self):
        """Start batch ATALANTA execution"""
        # Validate files selected
        if not self.batch_files:
            messagebox.showwarning("No Files", "Please select .bench files first.")
            return
        
        # Validate options
        if not self._validate_options():
            return
        
        # Check if already running
        if self.is_batch_running:
            messagebox.showwarning("Already Running", "Batch execution is already in progress.")
            return
        
        # Clear previous results
        self.batch_results = []
        self.current_batch_index = 0
        self.batch_output_text.delete(1.0, tk.END)
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_output_dir = os.path.join(
            self.outputs_dir,
            "results",
            f"batch_{timestamp}"
        )
        os.makedirs(self.batch_output_dir, exist_ok=True)
        
        # Update UI
        self.is_batch_running = True
        self.batch_run_btn.config(state=tk.DISABLED)
        self.batch_stop_btn.config(state=tk.NORMAL)
        self.batch_progress['maximum'] = len(self.batch_files)
        self.batch_progress['value'] = 0
        
        # Log batch start
        log_msg = f"{'='*70}\n"
        log_msg += f"BATCH EXECUTION STARTED\n"
        log_msg += f"{'='*70}\n"
        log_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_msg += f"Total Circuits: {len(self.batch_files)}\n"
        log_msg += f"Options: {self._get_options_metadata()}\n"
        log_msg += f"Output Directory: {self.batch_output_dir}\n"
        log_msg += f"{'='*70}\n\n"
        self.batch_output_text.insert(tk.END, log_msg)
        
        # Start execution in thread
        thread = threading.Thread(target=self._run_batch_execution)
        thread.daemon = True
        thread.start()
    
    def stop_batch_execution(self):
        """Stop batch execution"""
        if self.process:
            self.process.terminate()
        
        self.is_batch_running = False
        self.batch_run_btn.config(state=tk.NORMAL)
        self.batch_stop_btn.config(state=tk.DISABLED)
        self.batch_status_label.config(text="Batch execution stopped by user", fg="red")
    
    def _run_batch_execution(self):
        """Execute ATALANTA on all circuits sequentially"""
        options_str = self._get_options_metadata()
        
        for idx, circuit_file in enumerate(self.batch_files):
            if not self.is_batch_running:
                break
            
            self.current_batch_index = idx
            circuit_name = os.path.basename(circuit_file)
            
            # Update UI
            self.root.after(0, self._update_batch_progress, idx + 1, circuit_name)
            
            # Execute ATALANTA
            try:
                cmd = self._build_atalanta_command(circuit_file)
                cmd_str = " ".join(cmd)
                
                # Log circuit start
                log_msg = f"\n[{idx+1}/{len(self.batch_files)}] Processing: {circuit_name}\n"
                log_msg += f"Command: {cmd_str}\n"
                self.root.after(0, self._append_batch_log, log_msg)
                
                # Run ATALANTA
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                output, _ = self.process.communicate()
                
                # Parse results
                metrics = self.parse_atalanta_output(output, circuit_file)
                metrics['options_used'] = options_str
                metrics['timestamp'] = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Store results
                self.batch_results.append(metrics)
                
                # Save individual circuit log
                circuit_basename = os.path.splitext(circuit_name)[0]
                log_filename = f"{circuit_basename}_{metrics['timestamp']}.log"
                log_path = os.path.join(self.batch_output_dir, log_filename)
                
                with open(log_path, 'w') as f:
                    f.write(f"{'='*70}\n")
                    f.write(f"ATALANTA RUN METADATA\n")
                    f.write(f"{'='*70}\n")
                    f.write(f"Circuit: {circuit_basename}\n")
                    f.write(f"Timestamp: {metrics['timestamp']}\n")
                    f.write(f"Options: {options_str}\n")
                    f.write(f"{'='*70}\n\n")
                    f.write(output)
                
                # Generate per-circuit report
                self._generate_circuit_report(metrics, circuit_basename)
                
                # Log completion
                log_msg = f"✓ Completed: {circuit_name} (Coverage: {metrics.get('fault_coverage', 'N/A')})\n"
                self.root.after(0, self._append_batch_log, log_msg)
                
            except Exception as e:
                log_msg = f"✗ Error processing {circuit_name}: {str(e)}\n"
                self.root.after(0, self._append_batch_log, log_msg)
        
        # Generate summary reports
        if self.batch_results:
            self.root.after(0, self._finalize_batch_execution)
    
    def _update_batch_progress(self, current, circuit_name):
        """Update batch progress UI"""
        self.batch_progress['value'] = current
        self.batch_current_label.config(
            text=f"Processing ({current}/{len(self.batch_files)}): {circuit_name}"
        )
        self.batch_status_label.config(
            text=f"Executing batch... {current}/{len(self.batch_files)} complete",
            fg="blue"
        )
    
    def _append_batch_log(self, message):
        """Append message to batch output log"""
        self.batch_output_text.insert(tk.END, message)
        self.batch_output_text.see(tk.END)
    
    def _display_batch_results(self):
        """Display batch results in the UI table and statistics"""
        # Clear existing data
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Calculate statistics
        total_coverage = 0
        total_cpu_time = 0
        total_reduction = 0
        coverage_count = 0
        time_count = 0
        reduction_count = 0
        
        # Populate table
        for metrics in self.batch_results:
            circuit = metrics.get('circuit_name', 'N/A')
            
            # Extract and format coverage
            coverage = metrics.get('fault_coverage', 'N/A')
            coverage_display = coverage
            if coverage != 'N/A' and coverage != 'Not Found':
                cov_val = float(coverage.replace('%', '').strip())
                coverage_display = f"{cov_val:.2f}%"
                total_coverage += cov_val
                coverage_count += 1
            
            # Extract patterns
            patterns = metrics.get('patterns_after_compaction', 'N/A')
            
            # Extract and format CPU time
            cpu_time = metrics.get('cpu_time', 'N/A')
            cpu_display = cpu_time
            if cpu_time != 'N/A' and cpu_time != 'Not Found':
                time_val = float(cpu_time.replace('sec', '').strip())
                cpu_display = f"{time_val:.3f}"
                total_cpu_time += time_val
                time_count += 1
            
            # Extract gates and faults
            gates = metrics.get('num_gates', 'N/A')
            total_faults = metrics.get('total_faults', 'N/A')
            
            # Calculate reduction for statistics
            if (metrics.get('patterns_before_compaction') != 'Not Found' and 
                metrics.get('patterns_after_compaction') != 'Not Found'):
                before = int(metrics['patterns_before_compaction'])
                after = int(metrics['patterns_after_compaction'])
                if before > 0:
                    reduction = (before - after) / before * 100
                    total_reduction += reduction
                    reduction_count += 1
            
            # Insert into table
            self.results_tree.insert(
                '',
                'end',
                text=circuit,
                values=(coverage_display, patterns, cpu_display, gates, total_faults)
            )
        
        # Update statistics labels
        if coverage_count > 0:
            avg_coverage = total_coverage / coverage_count
            self.avg_coverage_label.config(text=f"{avg_coverage:.2f}%")
        else:
            self.avg_coverage_label.config(text="N/A")
        
        if time_count > 0:
            avg_time = total_cpu_time / time_count
            self.avg_time_label.config(text=f"{avg_time:.3f}s")
        else:
            self.avg_time_label.config(text="N/A")
        
        if reduction_count > 0:
            avg_reduction = total_reduction / reduction_count
            self.avg_reduction_label.config(text=f"{avg_reduction:.2f}%")
        else:
            self.avg_reduction_label.config(text="N/A")
    
    def _generate_circuit_report(self, metrics, circuit_name):
        """Generate individual circuit report"""
        report_path = os.path.join(self.batch_output_dir, f"{circuit_name}_report.txt")
        
        with open(report_path, 'w') as f:
            f.write(f"{'='*70}\n")
            f.write(f"ATALANTA ATPG REPORT - {circuit_name}\n")
            f.write(f"{'='*70}\n\n")
            
            f.write(f"CIRCUIT INFORMATION\n")
            f.write(f"{'-'*70}\n")
            f.write(f"Name              : {metrics.get('circuit_name', 'N/A')}\n")
            f.write(f"Primary Inputs    : {metrics.get('num_inputs', 'N/A')}\n")
            f.write(f"Primary Outputs   : {metrics.get('num_outputs', 'N/A')}\n")
            f.write(f"Number of Gates   : {metrics.get('num_gates', 'N/A')}\n")
            f.write(f"Circuit Level     : {metrics.get('circuit_level', 'N/A')}\n\n")
            
            f.write(f"ATPG CONFIGURATION\n")
            f.write(f"{'-'*70}\n")
            f.write(f"Options Used      : {metrics.get('options_used', 'N/A')}\n")
            f.write(f"Execution Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"TEST PATTERN GENERATION RESULTS\n")
            f.write(f"{'-'*70}\n")
            f.write(f"Fault Coverage    : {metrics.get('fault_coverage', 'N/A')}\n")
            f.write(f"Total Faults      : {metrics.get('total_faults', 'N/A')}\n")
            f.write(f"Detected Faults   : {metrics.get('detected_faults', 'N/A')}\n")
            f.write(f"Redundant Faults  : {metrics.get('redundant_faults', 'N/A')}\n")
            f.write(f"Aborted Faults    : {metrics.get('aborted_faults', 'N/A')}\n\n")
            
            f.write(f"TEST PATTERN COMPACTION\n")
            f.write(f"{'-'*70}\n")
            f.write(f"Before Compaction : {metrics.get('patterns_before_compaction', 'N/A')}\n")
            f.write(f"After Compaction  : {metrics.get('patterns_after_compaction', 'N/A')}\n")
            
            # Calculate reduction if available
            if (metrics.get('patterns_before_compaction') != 'Not Found' and 
                metrics.get('patterns_after_compaction') != 'Not Found'):
                before = int(metrics['patterns_before_compaction'])
                after = int(metrics['patterns_after_compaction'])
                reduction = before - after
                reduction_pct = (reduction / before * 100) if before > 0 else 0
                f.write(f"Reduction         : {reduction} patterns ({reduction_pct:.2f}%)\n")
            f.write(f"\n")
            
            f.write(f"EXECUTION TIME\n")
            f.write(f"{'-'*70}\n")
            f.write(f"Total CPU Time    : {metrics.get('cpu_time', 'N/A')}\n")
            if metrics.get('init_time') != 'Not Found':
                f.write(f"  Initialization  : {metrics.get('init_time', 'N/A')} Secs\n")
                f.write(f"  Fault Simulation: {metrics.get('fault_sim_time', 'N/A')} Secs\n")
                f.write(f"  FAN Algorithm   : {metrics.get('fan_time', 'N/A')} Secs\n")
            
            f.write(f"\n{'='*70}\n")
    
    def _finalize_batch_execution(self):
        """Generate summary reports and finalize batch execution"""
        try:
            # Generate CSV summary
            self._generate_csv_summary()
            
            # Generate text summary
            self._generate_text_summary()
            
            # Display results in UI
            self._display_batch_results()
            
            # Update UI
            self.is_batch_running = False
            self.batch_run_btn.config(state=tk.NORMAL)
            self.batch_stop_btn.config(state=tk.DISABLED)
            self.batch_status_label.config(
                text=f"Batch execution completed! {len(self.batch_results)} circuits processed",
                fg="green"
            )
            self.batch_current_label.config(text="")
            
            # Append completion log
            log_msg = f"\n{'='*70}\n"
            log_msg += f"BATCH EXECUTION COMPLETED\n"
            log_msg += f"{'='*70}\n"
            log_msg += f"Total Circuits Processed: {len(self.batch_results)}\n"
            log_msg += f"Output Directory: {self.batch_output_dir}\n"
            log_msg += f"Files Generated:\n"
            log_msg += f"  - summary.csv (Excel-compatible data)\n"
            log_msg += f"  - summary.txt (Formatted report)\n"
            log_msg += f"  - <circuit>_report.txt (Per-circuit reports)\n"
            log_msg += f"  - <circuit>_<timestamp>.log (Raw ATALANTA logs)\n"
            log_msg += f"{'='*70}\n"
            self.batch_output_text.insert(tk.END, log_msg)
            self.batch_output_text.see(tk.END)
            
            # Show completion popup
            messagebox.showinfo(
                "Batch Execution Complete",
                f"Successfully processed {len(self.batch_results)} circuits!\n\n"
                f"Results saved to:\n{self.batch_output_dir}\n\n"
                f"Files generated:\n"
                f"• summary.csv\n"
                f"• summary.txt\n"
                f"• Individual circuit reports"
            )
            
        except Exception as e:
            messagebox.showerror("Report Generation Error", f"Failed to generate reports:\n{str(e)}")
    
    def _generate_csv_summary(self):
        """Generate CSV summary file"""
        import csv
        
        csv_path = os.path.join(self.batch_output_dir, "summary.csv")
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = [
                'Circuit Name',
                'Inputs',
                'Outputs',
                'Gates',
                'Circuit Level',
                'Fault Coverage (%)',
                'Total Faults',
                'Detected Faults',
                'Redundant Faults',
                'Aborted Faults',
                'Patterns Before',
                'Patterns After',
                'Pattern Reduction (%)',
                'CPU Time (sec)',
                'Init Time (sec)',
                'Fault Sim Time (sec)',
                'FAN Time (sec)',
                'ATPG Options'
            ]
            writer.writerow(headers)
            
            # Write data rows
            for metrics in self.batch_results:
                # Calculate pattern reduction
                reduction_pct = ''
                if (metrics.get('patterns_before_compaction') != 'Not Found' and 
                    metrics.get('patterns_after_compaction') != 'Not Found'):
                    before = int(metrics['patterns_before_compaction'])
                    after = int(metrics['patterns_after_compaction'])
                    if before > 0:
                        reduction_pct = f"{((before - after) / before * 100):.2f}"
                
                # Extract coverage value
                coverage = metrics.get('fault_coverage', 'N/A')
                if coverage != 'N/A' and coverage != 'Not Found':
                    coverage = coverage.replace('%', '').strip()
                
                # Extract CPU time value
                cpu_time = metrics.get('cpu_time', 'N/A')
                if cpu_time != 'N/A' and cpu_time != 'Not Found':
                    cpu_time = cpu_time.replace('sec', '').strip()
                
                row = [
                    metrics.get('circuit_name', 'N/A'),
                    metrics.get('num_inputs', 'N/A'),
                    metrics.get('num_outputs', 'N/A'),
                    metrics.get('num_gates', 'N/A'),
                    metrics.get('circuit_level', 'N/A'),
                    coverage,
                    metrics.get('total_faults', 'N/A'),
                    metrics.get('detected_faults', 'N/A'),
                    metrics.get('redundant_faults', 'N/A'),
                    metrics.get('aborted_faults', 'N/A'),
                    metrics.get('patterns_before_compaction', 'N/A'),
                    metrics.get('patterns_after_compaction', 'N/A'),
                    reduction_pct,
                    cpu_time,
                    metrics.get('init_time', 'N/A'),
                    metrics.get('fault_sim_time', 'N/A'),
                    metrics.get('fan_time', 'N/A'),
                    metrics.get('options_used', 'N/A')
                ]
                writer.writerow(row)
    
    def _generate_text_summary(self):
        """Generate formatted text summary with statistics"""
        txt_path = os.path.join(self.batch_output_dir, "summary.txt")
        
        with open(txt_path, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"ATALANTA BATCH EXECUTION SUMMARY REPORT\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"Execution Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Circuits : {len(self.batch_results)}\n")
            f.write(f"ATPG Options   : {self.batch_results[0].get('options_used', 'N/A') if self.batch_results else 'N/A'}\n\n")
            
            # Per-circuit results table
            f.write(f"{'='*80}\n")
            f.write(f"INDIVIDUAL CIRCUIT RESULTS\n")
            f.write(f"{'='*80}\n\n")
            
            # Table header
            f.write(f"{'Circuit':<20} {'Coverage':<12} {'Patterns':<12} {'CPU Time':<12} {'Gates':<10}\n")
            f.write(f"{'-'*80}\n")
            
            # Calculate statistics
            total_coverage = 0
            total_cpu_time = 0
            total_reduction = 0
            coverage_count = 0
            time_count = 0
            reduction_count = 0
            
            for metrics in self.batch_results:
                circuit = metrics.get('circuit_name', 'N/A')[:19]
                coverage = metrics.get('fault_coverage', 'N/A')
                patterns = metrics.get('patterns_after_compaction', 'N/A')
                cpu_time = metrics.get('cpu_time', 'N/A')
                gates = metrics.get('num_gates', 'N/A')
                
                # Accumulate for averages
                if coverage != 'N/A' and coverage != 'Not Found':
                    cov_val = float(coverage.replace('%', '').strip())
                    total_coverage += cov_val
                    coverage_count += 1
                
                if cpu_time != 'N/A' and cpu_time != 'Not Found':
                    time_val = float(cpu_time.replace('sec', '').strip())
                    total_cpu_time += time_val
                    time_count += 1
                
                if (metrics.get('patterns_before_compaction') != 'Not Found' and 
                    metrics.get('patterns_after_compaction') != 'Not Found'):
                    before = int(metrics['patterns_before_compaction'])
                    after = int(metrics['patterns_after_compaction'])
                    if before > 0:
                        reduction = (before - after) / before * 100
                        total_reduction += reduction
                        reduction_count += 1
                
                f.write(f"{circuit:<20} {coverage:<12} {patterns:<12} {cpu_time:<12} {gates:<10}\n")
            
            # Overall statistics
            f.write(f"\n{'='*80}\n")
            f.write(f"OVERALL STATISTICS\n")
            f.write(f"{'='*80}\n\n")
            
            if coverage_count > 0:
                avg_coverage = total_coverage / coverage_count
                f.write(f"Average Fault Coverage      : {avg_coverage:.2f}%\n")
            else:
                f.write(f"Average Fault Coverage      : N/A\n")
            
            if time_count > 0:
                avg_time = total_cpu_time / time_count
                f.write(f"Average CPU Time            : {avg_time:.3f} seconds\n")
                f.write(f"Total CPU Time              : {total_cpu_time:.3f} seconds\n")
            else:
                f.write(f"Average CPU Time            : N/A\n")
            
            if reduction_count > 0:
                avg_reduction = total_reduction / reduction_count
                f.write(f"Average Pattern Reduction   : {avg_reduction:.2f}%\n")
            else:
                f.write(f"Average Pattern Reduction   : N/A\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"END OF REPORT\n")
            f.write(f"{'='*80}\n")


def main():
    root = tk.Tk()
    app = FaultSimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
